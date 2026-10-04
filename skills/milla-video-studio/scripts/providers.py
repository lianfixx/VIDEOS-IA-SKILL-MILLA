#!/usr/bin/env python3
"""Small, explicit provider adapters. Dry-run by default; no automatic retries."""
import argparse
import hashlib
import ipaddress
import json
import os
from pathlib import Path
import re
import socket
import sys
import tempfile
import urllib.error
import urllib.parse
import urllib.request

KIE_BASE = "https://api.kie.ai/api/v1/jobs/"
FISH_TTS = "https://api.fish.audio/v1/tts"
FISH_MODELS = ("s1", "s2-pro", "s2.1-pro", "s2.1-pro-free", "drama-3-preview")
FISH_WAV_SAMPLE_RATE = 44100
ASPECTS = ("1:1", "1:4", "1:8", "2:3", "3:2", "3:4", "4:1", "4:3", "4:5", "5:4", "8:1", "9:16", "16:9", "21:9", "auto")
LIMIT = 128 * 1024 * 1024


class ProviderError(Exception):
    """Safe message only. Never include provider bodies, URLs or credentials."""


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise ProviderError("Redirect refused; verify the destination explicitly.")


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False).encode()).hexdigest()


def private_path(workspace, name):
    root = Path(workspace).resolve()
    raw = Path(name)
    if raw.is_absolute() or ".." in raw.parts or not raw.parts:
        raise ProviderError("Output paths must be relative and stay inside the workspace.")
    target = root / raw
    for candidate in [target, *target.parents]:
        if candidate == root:
            break
        if candidate.is_symlink():
            raise ProviderError("Symlink output paths are refused.")
    if not target.resolve().is_relative_to(root):
        raise ProviderError("Output path escapes workspace.")
    return target


def write_private(path, data, replace=False):
    if path.is_symlink() or (path.exists() and not replace):
        raise ProviderError("Output already exists; choose another path.")
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    if not replace:
        try:
            fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        except FileExistsError:
            raise ProviderError("Output already exists; choose another path.") from None
        with os.fdopen(fd, "wb") as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        return
    fd, temporary = tempfile.mkstemp(prefix=".provider-", dir=path.parent)
    try:
        os.fchmod(fd, 0o600)
        with os.fdopen(fd, "wb") as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def save_state(path, record, replace=False):
    write_private(path, json.dumps(record, indent=2).encode() + b"\n", replace)


def read_state(path):
    if path.stat().st_size > 1024 * 1024:
        raise ProviderError("State file exceeds the configured size limit.")
    value = json.loads(path.read_text())
    if not isinstance(value, dict):
        raise ProviderError("State must be a JSON object.")
    return value


def secret(name):
    value = os.environ.get(name, "").strip()
    if not value:
        raise ProviderError("Missing environment variable: " + name)
    return value


def request(url, method="GET", body=None, key=None, extra_headers=None):
    headers = {"Accept": "application/json"}
    if body is not None:
        headers["Content-Type"] = "application/json"
    if key:
        headers["Authorization"] = "Bearer " + key
    headers.update(extra_headers or {})
    payload = None if body is None else json.dumps(body).encode()
    req = urllib.request.Request(url, data=payload, headers=headers, method=method)
    try:
        with urllib.request.build_opener(NoRedirect()).open(req, timeout=60) as response:
            result = response.read(LIMIT + 1)
            if len(result) > LIMIT:
                raise ProviderError("Response exceeds the configured size limit.")
            return result
    except urllib.error.HTTPError as error:
        raise ProviderError("Provider HTTP " + str(error.code) + "; no automatic retry.") from None
    except (urllib.error.URLError, TimeoutError, OSError):
        raise ProviderError("Network request failed or timed out; outcome may be unknown. Do not resubmit blindly.") from None


def json_response(raw):
    try:
        result = json.loads(raw)
    except (ValueError, UnicodeDecodeError):
        raise ProviderError("Provider returned invalid JSON.") from None
    if not isinstance(result, dict):
        raise ProviderError("Provider returned an unexpected response shape.")
    if result.get("code") != 200:
        raise ProviderError("Provider did not report application-level success; inspect its dashboard privately.")
    if not isinstance(result.get("data"), dict):
        raise ProviderError("Provider response is missing task data.")
    return result["data"]


def read_text(name):
    value = Path(name).read_text(encoding="utf-8").strip()
    if not value or len(value) > 20000:
        raise ProviderError("Text must contain between 1 and 20000 characters.")
    return value


def safe_id(value):
    if not isinstance(value, str) or not re.fullmatch(r"[A-Za-z0-9_-]{1,128}", value):
        raise ProviderError("Invalid task or voice identifier.")
    return value


def public_https(url, hosts, resolve=False):
    parsed = urllib.parse.urlparse(url)
    host = (parsed.hostname or "").lower()
    if parsed.scheme != "https" or host not in hosts or parsed.username or parsed.password or parsed.port not in (None, 443):
        raise ProviderError("HTTPS destination is outside the explicit hostname allowlist.")
    if resolve:
        try:
            addresses = socket.getaddrinfo(host, 443, type=socket.SOCK_STREAM)
        except OSError:
            raise ProviderError("Cannot resolve the approved download hostname.") from None
        if not addresses or any(not ipaddress.ip_address(item[4][0]).is_global for item in addresses):
            raise ProviderError("Private, loopback or reserved download addresses are refused.")
    return host


def image(args):
    payload = {"model": "nano-banana-2-lite", "input": {"prompt": read_text(args.prompt_file), "aspect_ratio": args.aspect_ratio}}
    state_path = private_path(args.workspace, args.state)
    record = {"provider": "kie", "model": payload["model"], "request_sha256": digest(payload), "status": "dry_run"}
    if not args.execute:
        return record
    key = secret("KIE_API_KEY")
    record["status"] = "submission_started"
    save_state(state_path, record)
    try:
        data = json_response(request(KIE_BASE + "createTask", "POST", payload, key))
        record.update(task_id=safe_id(data.get("taskId")), status="submitted")
    except ProviderError:
        record["status"] = "submission_unconfirmed"
        save_state(state_path, record, True)
        raise
    save_state(state_path, record, True)
    return {"status": "submitted", "task_id": record["task_id"], "state_file": args.state}


def status(args):
    state_path = private_path(args.workspace, args.state)
    record = read_state(state_path)
    task_id = safe_id(record.get("task_id"))
    if record.get("provider") != "kie":
        raise ProviderError("The state file is not a Kie task.")
    if not args.execute:
        return {"status": "dry_run", "operation": "one_status_request", "task_id": task_id}
    data = json_response(request(KIE_BASE + "recordInfo?" + urllib.parse.urlencode({"taskId": task_id}), key=secret("KIE_API_KEY")))
    if data.get("taskId") != task_id:
        raise ProviderError("Provider task identity does not match the saved state.")
    value = data.get("state")
    if value not in ("waiting", "queuing", "generating", "success", "fail"):
        raise ProviderError("Unknown task state; no regeneration attempted.")
    record["status"] = value
    if value == "success":
        try:
            urls = json.loads(data.get("resultJson", "{}"))["resultUrls"]
        except (ValueError, KeyError, TypeError):
            raise ProviderError("Task succeeded but result URLs are missing or invalid.") from None
        if not isinstance(urls, list) or not urls or any(not isinstance(u, str) or not u.startswith("https://") for u in urls):
            raise ProviderError("Unexpected result URLs; inspect provider dashboard privately.")
        record["result_urls"] = urls
    save_state(state_path, record, True)
    return {"status": value, "task_id": task_id, "state_file": args.state, "result_count": len(record.get("result_urls", []))}


def tts(args):
    voice_id = safe_id(args.reference_id)
    payload = {
        "text": read_text(args.text_file),
        "reference_id": voice_id,
        "format": "wav",
        "sample_rate": FISH_WAV_SAMPLE_RATE,
    }
    output = private_path(args.workspace, args.out)
    state_path = private_path(args.workspace, args.state)
    if output.suffix.lower() != ".wav":
        raise ProviderError("Fish output must use a .wav extension because this adapter requests WAV audio.")
    if output == state_path:
        raise ProviderError("Audio and state paths must differ.")
    record = {
        "provider": "fish",
        "model": args.model,
        "reference_id": voice_id,
        "format": "wav",
        "sample_rate_hz": FISH_WAV_SAMPLE_RATE,
        "request_sha256": digest({"model": args.model, "body": payload}),
        "status": "dry_run",
    }
    if not args.execute:
        return {k: v for k, v in record.items() if k != "reference_id"}
    if output.exists():
        raise ProviderError("Output already exists; choose another path.")
    key = secret("FISH_API_KEY")
    record["status"] = "submission_started"
    save_state(state_path, record)
    try:
        raw = request(FISH_TTS, "POST", payload, key, {"model": args.model, "Accept": "audio/wav"})
        if not (raw.startswith(b"RIFF") and raw[8:12] == b"WAVE"):
            raise ProviderError("Fish response is not the requested WAV audio.")
        write_private(output, raw)
        record.update(status="downloaded", audio_sha256=hashlib.sha256(raw).hexdigest())
    except ProviderError:
        record["status"] = "submission_unconfirmed"
        save_state(state_path, record, True)
        raise
    save_state(state_path, record, True)
    return {"status": "downloaded", "output": args.out, "state_file": args.state, "audio_sha256": record["audio_sha256"]}


def download(args):
    output = private_path(args.workspace, args.out)
    state_path = private_path(args.workspace, args.state)
    record = read_state(state_path)
    try:
        url = record["result_urls"][args.index]
    except (KeyError, IndexError, TypeError):
        raise ProviderError("The selected result URL is missing.") from None
    if args.index < 0 or not isinstance(url, str):
        raise ProviderError("Invalid result index.")
    host = public_https(url, set(args.allow_host), resolve=args.execute)
    if not args.execute:
        return {"status": "dry_run", "host": host, "output": args.out, "authorization_sent": False}
    if output.exists():
        raise ProviderError("Output already exists; choose another path.")
    raw = request(url)  # Deliberately no provider authentication; redirects blocked.
    if not raw:
        raise ProviderError("Downloaded file is empty.")
    write_private(output, raw)
    return {"status": "downloaded", "output": args.out, "sha256": hashlib.sha256(raw).hexdigest(), "bytes": len(raw)}


def parser():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--workspace", default=".", help="Private project output directory")
    commands = p.add_subparsers(dest="command", required=True)
    i = commands.add_parser("kie-image")
    i.add_argument("--prompt-file", required=True)
    i.add_argument("--aspect-ratio", choices=ASPECTS, default="9:16")
    i.add_argument("--state", required=True)
    i.set_defaults(handler=image)
    s = commands.add_parser("kie-status")
    s.add_argument("--state", required=True)
    s.set_defaults(handler=status)
    t = commands.add_parser("fish-tts")
    t.add_argument("--text-file", required=True)
    t.add_argument("--reference-id", required=True)
    t.add_argument("--model", choices=FISH_MODELS, required=True)
    t.add_argument("--out", required=True, help="Relative .wav output path; this adapter requests WAV from Fish")
    t.add_argument("--state", required=True)
    t.set_defaults(handler=tts)
    d = commands.add_parser("download")
    d.add_argument("--state", required=True)
    d.add_argument("--index", type=int, default=0)
    d.add_argument("--allow-host", action="append", required=True, help="Exact CDN hostname observed in provider result; no wildcard")
    d.add_argument("--out", required=True)
    d.set_defaults(handler=download)
    for command in (i, s, t, d):
        command.add_argument("--execute", action="store_true", help="Make the real request; generation may charge credits")
    return p


def main(argv=None):
    args = parser().parse_args(argv)
    try:
        result = args.handler(args)
        print(json.dumps(result, ensure_ascii=False))
        return 0
    except (ProviderError, OSError, ValueError):
        error = sys.exc_info()[1]
        message = str(error) if isinstance(error, ProviderError) else "Local file or data error; inspect the private workspace."
        print(json.dumps({"error": message}), file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
