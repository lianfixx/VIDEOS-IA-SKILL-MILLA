"""Local tests for policy drift, path safety and FFmpeg measurement (no APIs)."""
import copy
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest
from unittest import mock

import milla


class ProjectTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.project = milla.project_template("Prueba")
        self.project["output"]["durationSeconds"] = 6
        sample = self.root / "sample.mp3"
        sample.write_bytes(b"approved test sample")
        self.project["voice"] = {"provider": "fish", "model": "s2.1-pro-free", "reference_id": "user-selected-reference",
            "rejected_reference_ids": [], "approval": {"status": "approved", "sample_path": sample.name,
                "model": "s2.1-pro-free", "reference_id": "user-selected-reference",
                "sample_sha256": milla.digest(sample), "approved_by": "test-user", "approved_at": "2026-10-04T18:00:00Z"}}
        self.project["sources"] = [{"id": "source1", "title": "Official source",
            "url": "https://www.diputados.gob.mx/", "accessed_at": "2026-10-04"}]
        for i in range(6):
            self.add_asset(f"visual{i}", "image", "kie")
            self.project["scenes"].append({"id": f"scene{i}", "title": f"Escena {i}", "start": i,
                "end": i + 1.2 if i < 5 else 6, "asset_ids": [f"visual{i}"],
                "transition": {"family": ["fade", "wipe", "push", "mask", "depth", "zoom"][i],
                    "durationSeconds": 0 if i == 0 else 0.2}})
        self.add_asset("voice", "audio", "fish")
        self.add_asset("music", "audio", "kie")
        self.project["audio"]["voice"] = "voice"
        self.project["audio"]["music"] = "music"
        self.project["subtitleCues"] = [{"start": 0, "end": 6, "text": "Texto de prueba."}]
        self.project["subtitlesVerified"] = True

    def add_asset(self, aid, kind, provider):
        path = self.root / (aid + ".bin")
        path.write_bytes(f"unique-asset-{aid}".encode())
        self.project["assets"].append({"id": aid, "path": path.name, "sha256": milla.digest(path),
            "kind": kind, "provider": provider,
            "model": "s2.1-pro-free" if provider == "fish" else "nano-banana-2-lite",
            "reference_id": "user-selected-reference" if provider == "fish" else "",
            "source": {"type": "generated", "url": "https://provider.example/terms",
                "license": "Rights reviewed for this account and use", "rights_confirmed": True},
            "qa": {"watermark": False, "third_party_logo": False, "particles": False, "approved": True}})

    def errors(self, allow_pending=False):
        return milla.validate(self.project, self.root, allow_pending)["errors"]

    def test_complete_manifest_is_ready_for_review_not_approved(self):
        result = milla.validate(self.project, self.root)
        self.assertEqual([], result["errors"])
        self.assertEqual("ready_for_review", result["status"])

    def test_policy_drift_blocked_even_in_draft(self):
        for field, value in (("particles_allowed", True), ("watermarks_allowed", True),
                             ("allowed_image_providers", ["kie", "chatgpt"]), ("minimum_transition_families", 1)):
            with self.subTest(field=field):
                data = copy.deepcopy(self.project)
                data["quality"][field] = value
                self.assertTrue(milla.validate(data, self.root, True)["errors"])

    def test_prohibited_image_provider_and_logo(self):
        self.project["assets"][0]["provider"] = "chatgpt-imagegen"
        self.project["assets"][0]["qa"]["third_party_logo"] = True
        errors = " ".join(self.errors(True))
        self.assertIn("prohibited image provider", errors)
        self.assertIn("third_party_logo", errors)

    def test_hash_tampering_and_duplicate_content(self):
        asset = self.project["assets"][0]
        (self.root / asset["path"]).write_bytes(b"changed bytes")
        self.assertIn("SHA-256 mismatch", " ".join(self.errors()))
        self.project["assets"][1]["sha256"] = asset["sha256"]
        self.assertIn("duplicate asset content", " ".join(self.errors()))

    def test_duplicate_visual_reuse_rejected(self):
        self.project["scenes"][1]["asset_ids"] = ["visual0"]
        self.assertIn("repeated across scenes", " ".join(self.errors()))

    def test_unsafe_paths_and_symlink_escape(self):
        for path in ("../outside.png", "/etc/passwd", "C:/outside.png", "..\\outside.png", "https://x/a.png"):
            with self.subTest(path=path):
                data = copy.deepcopy(self.project)
                data["assets"][0]["path"] = path
                self.assertTrue(milla.validate(data, self.root)["errors"])
        link = self.root / "escape"
        link.symlink_to(self.root.parent, target_is_directory=True)
        self.project["assets"][0]["path"] = "escape/outside.png"
        self.assertIn("stay inside", " ".join(self.errors()))

    def test_voice_requires_approved_exact_sample_and_reference(self):
        self.project["voice"]["approval"]["status"] = "pending"
        self.assertIn("explicitly approved", " ".join(self.errors()))
        self.assertEqual([], self.errors(True))
        self.project["voice"]["approval"]["status"] = "approved"
        self.project["voice"]["approval"]["sample_sha256"] = "a" * 64
        self.assertIn("SHA-256 mismatch", " ".join(self.errors(True)))
        self.project["voice"]["rejected_reference_ids"] = ["user-selected-reference"]
        self.assertIn("explicitly rejected", " ".join(self.errors(True)))

    def test_final_narration_cannot_silently_change_voice(self):
        self.project["assets"][-2]["reference_id"] = "different-voice"
        self.assertIn("must match the approved voice", " ".join(self.errors()))

    def test_changing_parent_and_narration_does_not_reuse_old_sample_approval(self):
        self.project["voice"]["reference_id"] = "new-voice"
        self.project["voice"]["model"] = "new-engine"
        self.project["assets"][-2]["reference_id"] = "new-voice"
        self.project["assets"][-2]["model"] = "new-engine"
        errors = " ".join(self.errors())
        self.assertIn("voice.approval.reference_id must match", errors)
        self.assertIn("voice.approval.model must match", errors)

    def test_real_photo_with_documented_rights_is_allowed(self):
        photo = self.project["assets"][0]
        photo["provider"] = "real-photo"
        photo["source"]["type"] = "owned"
        photo["discovery_provider"] = "apify"
        photo.pop("model")
        self.assertEqual([], self.errors())
        photo["source"]["type"] = "generated"
        self.assertIn("requires licensed or owned", " ".join(self.errors()))
        photo["source"]["type"] = "licensed"
        photo["source"]["rights_confirmed"] = False
        self.assertIn("usage rights", " ".join(self.errors()))

    def test_kie_fallback_requires_reason(self):
        self.project["assets"][0]["model"] = "another-kie-model"
        self.assertIn("fallback_reason", " ".join(self.errors()))

    def test_transition_variety_overlap_and_repetition(self):
        self.project["scenes"][2]["transition"]["family"] = "wipe"
        self.assertIn("consecutive transitions", " ".join(self.errors()))
        self.project["scenes"][2]["transition"]["family"] = "push"
        self.project["scenes"][0]["end"] = 1.1
        self.assertIn("overlap completes", " ".join(self.errors()))
        for i, scene in enumerate(self.project["scenes"]):
            scene["transition"]["family"] = "wipe" if i % 2 else "push"
        self.assertIn("at least 4 families", " ".join(self.errors()))

    def test_short_video_does_not_require_four_families(self):
        self.project["scenes"] = self.project["scenes"][:3]
        self.project["scenes"][-1]["end"] = 6
        self.assertEqual([], self.errors())

    def test_reduced_transition_minimum_requires_recorded_rationale(self):
        self.project["quality"]["minimum_transition_families"] = 2
        for i, scene in enumerate(self.project["scenes"]):
            scene["transition"]["family"] = "wipe" if i % 2 else "push"
        self.assertIn("transition_variety_rationale", " ".join(self.errors()))
        self.project["quality"]["transition_variety_rationale"] = "A deliberate restrained variation for an approved accessibility brief."
        report = milla.validate(self.project, self.root)
        self.assertEqual([], report["errors"])
        self.assertEqual(2, report["profile_adjustments"][0]["value"])

    def test_rights_and_legal_sources_required(self):
        self.project["sources"] = []
        self.project["assets"][0]["source"]["rights_confirmed"] = False
        errors = " ".join(self.errors())
        self.assertIn("primary research", errors)
        self.assertIn("usage rights", errors)

    def test_malformed_transition_returns_errors_without_crash(self):
        self.project["scenes"][2]["transition"]["family"] = []
        self.assertTrue(self.errors())

    def test_init_never_overwrites(self):
        child = self.root / "new"
        milla.init_project(child, "Draft")
        before = (child / "project.json").read_bytes()
        with self.assertRaises(ValueError):
            milla.init_project(child, "Replacement")
        self.assertEqual(before, (child / "project.json").read_bytes())
        data = json.loads(before)
        self.assertEqual("draft", milla.validate(data, child, True)["status"])


class SecretTests(unittest.TestCase):
    def test_scan_reports_location_never_value(self):
        with tempfile.TemporaryDirectory() as tmp:
            token = "ghp_" + "Abc123XYZ987" * 4
            fish_token = "abcDEF0123456789" * 2
            Path(tmp, ".env").write_text("FISH_API_KEY=" + fish_token + "\nGITHUB_TOKEN=" + token, encoding="utf-8")
            result = milla.secret_scan(tmp)
            output = json.dumps(result)
            self.assertEqual("findings", result["status"])
            self.assertNotIn(token, output)
            self.assertNotIn(fish_token, output)
            self.assertIn(".env", output)

    def test_doctor_does_not_print_credentials_or_use_network(self):
        value = "a-secret-value-must-not-be-printed"
        with mock.patch.dict(os.environ, {"FISH_API_KEY": value}):
            result = milla.doctor()
        self.assertTrue(result["credentials"]["FISH_API_KEY"]["configured"])
        self.assertNotIn(value, json.dumps(result))
        self.assertEqual(0, result["api_calls"])


@unittest.skipUnless(shutil.which("ffmpeg") and shutil.which("ffprobe"), "FFmpeg not installed")
class VideoTests(unittest.TestCase):
    def test_real_encode_reports_audio_and_black_candidates_without_approval(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp, "synthetic.mp4")
            subprocess.run(["ffmpeg", "-v", "error", "-f", "lavfi", "-i", "color=c=black:s=160x284:r=30:d=0.8",
                "-f", "lavfi", "-i", "sine=frequency=440:sample_rate=48000:duration=0.8",
                "-c:v", "libx264", "-pix_fmt", "yuv420p", "-c:a", "aac", "-shortest", str(path)],
                check=True, capture_output=True, timeout=30)
            report = milla.inspect_video(path, luminance=True)
            self.assertEqual("needs_human_review", report["status"])
            self.assertEqual("h264", report["video"]["video_codec"])
            self.assertGreater(len(report["black_intervals"]), 0)
            self.assertIsNotNone(report["audio_measurements"]["integrated_lufs"])
            self.assertGreater(report["luminance"]["frames"], 0)
            self.assertIn("format_differs_from_1080x1920_30fps_profile", report["flags"])
            self.assertEqual(1, report["video"]["audio_channels"])
            self.assertEqual(48000, report["video"]["audio_sample_rate_hz"])
            self.assertEqual("yuv420p", report["video"]["pixel_format"])
            self.assertIn("audio_channels_differ_from_stereo_review_delivery_mix", report["flags"])
            self.assertIn("ffmpeg", report["method"]["tool_versions"])
            self.assertEqual(-1.5, report["method"]["thresholds"]["true_peak_max_dbtp"])
            self.assertIn("TP=-2", report["method"]["audio_filter"])


if __name__ == "__main__":
    unittest.main()
