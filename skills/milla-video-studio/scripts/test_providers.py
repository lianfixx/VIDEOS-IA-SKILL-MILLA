"""Offline adapter tests. No credentials, live API requests or generation fees."""
import contextlib
import io
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import urllib.error

import providers as p


class ProvidersTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.prompt = self.root / "prompt.txt"
        self.prompt.write_text("Private script that must not appear in console")
        self.env = patch.dict(os.environ, {"KIE_API_KEY": "example_kie_fixture", "FISH_API_KEY": "example_fish_fixture"})
        self.env.start()

    def tearDown(self):
        self.env.stop()
        self.temp.cleanup()

    def args(self, *values):
        return p.parser().parse_args(["--workspace", str(self.root), *values])

    def image_args(self, execute=True):
        values = ["kie-image", "--prompt-file", str(self.prompt), "--state", "private/image.json"]
        return self.args(*(values + (["--execute"] if execute else [])))

    def tts_args(self, execute=True):
        values = ["fish-tts", "--text-file", str(self.prompt), "--reference-id", "voice-123", "--model", "s2.1-pro-free", "--out", "voice.wav", "--state", "tts.json"]
        return self.args(*(values + (["--execute"] if execute else [])))

    def task(self, **extra):
        result = {"provider": "kie", "task_id": "task-123", "status": "submitted"}
        result.update(extra)
        (self.root / "task.json").write_text(json.dumps(result))

    def test_dry_runs_never_call_network_or_leak_inputs(self):
        with patch.object(p, "request") as mocked:
            outputs = [p.image(self.image_args(False)), p.tts(self.tts_args(False))]
        mocked.assert_not_called()
        text = json.dumps(outputs)
        for value in ("Private script", "example_kie_fixture", "example_fish_fixture", "voice-123"):
            self.assertNotIn(value, text)
        self.assertFalse((self.root / "private").exists())

    def test_kie_schema_and_saved_id(self):
        with patch.object(p, "request", return_value=b'{"code":200,"data":{"taskId":"task-123"}}') as mocked:
            result = p.image(self.image_args())
        body = mocked.call_args.args[2]
        self.assertEqual(body["model"], "nano-banana-2-lite")
        self.assertEqual(set(body["input"]), {"prompt", "aspect_ratio"})
        self.assertEqual(result["task_id"], "task-123")
        path = self.root / "private/image.json"
        self.assertEqual(path.stat().st_mode & 0o777, 0o600)
        self.assertNotIn("Private script", path.read_text())

    def test_duplicate_and_uncertain_submission_do_not_retry(self):
        with patch.object(p, "request", side_effect=p.ProviderError("Timeout")) as mocked:
            with self.assertRaises(p.ProviderError):
                p.image(self.image_args())
            with self.assertRaises(p.ProviderError):
                p.image(self.image_args())
        self.assertEqual(mocked.call_count, 1)
        record = json.loads((self.root / "private/image.json").read_text())
        self.assertEqual(record["status"], "submission_unconfirmed")

    def test_application_error_not_http_success(self):
        with patch.object(p, "request", return_value=b'{"code":401,"msg":"secret echoed"}'):
            with self.assertRaisesRegex(p.ProviderError, "application-level"):
                p.image(self.image_args())

    def test_status_single_request_and_result_urls_private(self):
        self.task()
        body = {"code": 200, "data": {"taskId": "task-123", "state": "success", "resultJson": json.dumps({"resultUrls": ["https://cdn.example.test/image?token=private"]})}}
        with patch.object(p, "request", return_value=json.dumps(body).encode()) as mocked:
            result = p.status(self.args("kie-status", "--state", "task.json", "--execute"))
        self.assertEqual(mocked.call_count, 1)
        self.assertNotIn("token", json.dumps(result))
        self.assertEqual(result["result_count"], 1)

    def test_task_mismatch_refused(self):
        self.task()
        with patch.object(p, "request", return_value=b'{"code":200,"data":{"taskId":"different","state":"success"}}'):
            with self.assertRaisesRegex(p.ProviderError, "identity"):
                p.status(self.args("kie-status", "--state", "task.json", "--execute"))

    def test_fish_audio_output_and_model_header(self):
        wav = b"RIFF" + b"\x00" * 4 + b"WAVE" + b"sample"
        with patch.object(p, "request", return_value=wav) as mocked:
            p.tts(self.tts_args())
        self.assertEqual(mocked.call_args.args[4]["model"], "s2.1-pro-free")
        self.assertEqual(mocked.call_args.args[2]["reference_id"], "voice-123")
        self.assertEqual((self.root / "voice.wav").read_bytes(), wav)

    def test_fish_json_error_is_not_audio(self):
        with patch.object(p, "request", return_value=b'{"error":"private-body"}'):
            with self.assertRaisesRegex(p.ProviderError, "not the requested WAV"):
                p.tts(self.tts_args())
        self.assertFalse((self.root / "voice.wav").exists())

    def test_paths_traversal_absolute_and_symlink_rejected(self):
        for path in ("../outside", "/tmp/outside"):
            with self.assertRaises(p.ProviderError):
                p.private_path(self.root, path)
        (self.root / "link").symlink_to("/tmp", target_is_directory=True)
        with self.assertRaises(p.ProviderError):
            p.private_path(self.root, "link/file")

    def test_download_allowlist_and_no_auth(self):
        self.task(result_urls=["https://cdn.example.test/image?signature=private"])
        args = self.args("download", "--state", "task.json", "--allow-host", "cdn.example.test", "--out", "image.png", "--execute")
        with patch.object(p.socket, "getaddrinfo", return_value=[(2, 1, 6, "", ("8.8.8.8", 443))]), patch.object(p, "request", return_value=b"image") as mocked:
            result = p.download(args)
        self.assertEqual(len(mocked.call_args.args), 1)
        self.assertNotIn("key", mocked.call_args.kwargs)
        self.assertNotIn("signature", json.dumps(result))

    def test_download_rejects_private_addresses_and_unlisted_hosts(self):
        with self.assertRaises(p.ProviderError):
            p.public_https("https://elsewhere.test/file", {"cdn.example.test"})
        with patch.object(p.socket, "getaddrinfo", return_value=[(2, 1, 6, "", ("127.0.0.1", 443))]):
            with self.assertRaises(p.ProviderError):
                p.public_https("https://cdn.example.test/file", {"cdn.example.test"}, True)

    def test_http_error_does_not_echo_private_response(self):
        error = urllib.error.HTTPError("https://secret-url.test/?token=private", 401, "secret", {}, io.BytesIO(b"private response"))
        with patch.object(p.urllib.request, "build_opener") as factory:
            factory.return_value.open.side_effect = error
            with self.assertRaises(p.ProviderError) as caught:
                p.request(p.KIE_BASE, key="private-key")
        self.assertEqual(str(caught.exception), "Provider HTTP 401; no automatic retry.")

    def test_redirects_refused(self):
        with self.assertRaises(p.ProviderError):
            p.NoRedirect().redirect_request(None, None, 302, "", {}, "https://attacker.test")

    def test_state_shape_and_atomic_no_overwrite(self):
        path = self.root / "state.json"
        path.write_text("[]")
        with self.assertRaisesRegex(p.ProviderError, "JSON object"):
            p.read_state(path)
        with self.assertRaises(p.ProviderError):
            p.write_private(path, b"replacement")
        self.assertEqual(path.read_text(), "[]")

    def test_cli_error_output_is_redacted(self):
        output = io.StringIO()
        with patch.object(p, "read_text", side_effect=OSError("private-file-and-secret")), contextlib.redirect_stderr(output):
            code = p.main(["--workspace", str(self.root), "kie-image", "--prompt-file", str(self.prompt), "--state", "state.json"])
        self.assertEqual(code, 2)
        self.assertNotIn("private-file-and-secret", output.getvalue())


if __name__ == "__main__":
    unittest.main()
