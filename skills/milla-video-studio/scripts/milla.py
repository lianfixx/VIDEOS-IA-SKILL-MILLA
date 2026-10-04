#!/usr/bin/env python3
"""Offline project setup, policy checks and measurements. No API calls or secrets."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import math
import os
from pathlib import Path, PurePosixPath
import re
import shutil
import subprocess
import sys
from urllib.parse import urlparse

FAMILIES = {"wipe", "push", "mask", "depth", "match-cut", "pan", "zoom",
            "diagram-morph", "object-reveal", "fade"}
SHA256 = re.compile(r"^[a-fA-F0-9]{64}$")
ENV_NAMES = ("KIE_API_KEY", "FISH_API_KEY", "APIFY_TOKEN")


def now():
    return datetime.now(timezone.utc).isoformat()


def digest(path):
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def write_json(path, obj):
    with path.open("x", encoding="utf-8") as stream:
        json.dump(obj, stream, ensure_ascii=False, indent=2, allow_nan=False)
        stream.write("\n")


def safe_path(root, value):
    """Project-owned, relative POSIX paths only; also stops escaping symlinks."""
    if not isinstance(value, str) or not value or "\x00" in value or "\\" in value:
        raise ValueError("expected a relative POSIX path")
    p = PurePosixPath(value)
    if p.is_absolute() or ".." in p.parts or re.match(r"^[A-Za-z][A-Za-z0-9+.-]*:", value):
        raise ValueError("absolute paths and traversal are forbidden")
    target = (root / value).resolve()
    if not target.is_relative_to(root.resolve()) or target == root.resolve():
        raise ValueError("path must stay inside the project")
    return target


def valid_url(value):
    if not isinstance(value, str):
        return False
    try:
        p = urlparse(value)
        return p.scheme in ("https", "http") and bool(p.hostname) and not p.username and not p.password
    except ValueError:
        return False


def number(value):
    return isinstance(value, (float, int)) and not isinstance(value, bool) and math.isfinite(value)


def project_template(title="Nuevo video MILLA"):
    return {
        "schema_version": 1,
        "project": {"id": "nuevo-video", "title": title, "content_domain": "legal"},
        "output": {"width": 1080, "height": 1920, "fps": 30, "durationSeconds": 55},
        "quality": {"particles_allowed": False, "watermarks_allowed": False,
                    "allowed_image_providers": ["kie"], "minimum_transition_families": 4},
        "voice": {"provider": "fish", "model": "", "reference_id": "", "rejected_reference_ids": [],
                  "approval": {"status": "pending", "model": "", "reference_id": "", "sample_path": "audio/voice-sample.mp3",
                               "sample_sha256": "", "approved_by": "", "approved_at": ""}},
        "assets": [], "scenes": [], "sources": [], "subtitleCues": [],
        "subtitlesVerified": False,
        "audio": {"voice": "", "music": "", "voiceVolume": 1, "musicVolume": 0.12, "sfx": []},
        "delivery": {"video_path": "out/final.mp4"}}


def validate(data, root, allow_pending=False):
    errors, warnings, adjustments = [], [], []

    def fail(message):
        errors.append(message)

    def pending(message):
        (warnings if allow_pending else errors).append(message)

    def obj(value, label):
        if not isinstance(value, dict):
            fail(f"{label}: expected object")
            return {}
        return value

    def array(value, label):
        if not isinstance(value, list):
            fail(f"{label}: expected array")
            return []
        return value

    def text_field(value, label):
        if not isinstance(value, str) or not value.strip():
            pending(f"{label}: required")
            return False
        return True

    def check_path(value, label):
        try:
            return safe_path(root, value)
        except ValueError as exc:
            fail(f"{label}: {exc}")
            return None

    def check_file(path_value, sha, label):
        path = check_path(path_value, f"{label}.path")
        valid_sha = isinstance(sha, str) and bool(SHA256.fullmatch(sha))
        if not valid_sha:
            pending(f"{label}: SHA-256 required")
        if path is not None:
            if not path.is_file():
                pending(f"{label}: local file missing")
            elif valid_sha and digest(path) != sha.lower():
                fail(f"{label}: SHA-256 mismatch")
        return path

    if not isinstance(data, dict):
        return {"status": "invalid", "errors": ["root: expected object"], "warnings": []}
    if type(data.get("schema_version")) is not int or data.get("schema_version") != 1:
        fail("schema_version must be 1")
    project = obj(data.get("project"), "project")
    text_field(project.get("id"), "project.id")
    text_field(project.get("title"), "project.title")
    quality = obj(data.get("quality"), "quality")
    if quality.get("particles_allowed") is not False:
        fail("quality.particles_allowed must be false")
    if quality.get("watermarks_allowed") is not False:
        fail("quality.watermarks_allowed must be false")
    if quality.get("allowed_image_providers") != ["kie"]:
        fail("quality.allowed_image_providers must be ['kie']; ChatGPT/ImageGen is forbidden")
    minimum = quality.get("minimum_transition_families")
    if not isinstance(minimum, int) or isinstance(minimum, bool) or not 1 <= minimum <= len(FAMILIES):
        fail("quality.minimum_transition_families must be an integer within 1..10 (default 4)")
        minimum = 4
    elif minimum < 4:
        rationale = quality.get("transition_variety_rationale")
        if not isinstance(rationale, str) or not rationale.strip():
            fail("reducing the default of 4 transition families requires quality.transition_variety_rationale")
        else:
            adjustments.append({"field": "minimum_transition_families", "value": minimum, "rationale": rationale})
    output = obj(data.get("output"), "output")
    for k, expected in (("width", 1080), ("height", 1920), ("fps", 30)):
        if output.get(k) != expected:
            fail(f"output.{k}: MILLA profile requires {expected}")
    duration = output.get("durationSeconds")
    if not number(duration) or duration <= 0:
        fail("output.durationSeconds must be positive")
        duration = 0
    voice = obj(data.get("voice"), "voice")
    if voice.get("provider") != "fish":
        fail("voice.provider must be fish for the current profile")
    text_field(voice.get("model"), "voice.model (actual TTS engine)")
    reference = voice.get("reference_id")
    text_field(reference, "voice.reference_id")
    rejected = array(voice.get("rejected_reference_ids", []), "voice.rejected_reference_ids")
    if reference and reference in rejected:
        fail("voice.reference_id is explicitly rejected")
    approval = obj(voice.get("approval"), "voice.approval")
    for field in ("model", "reference_id"):
        if text_field(approval.get(field), f"voice.approval.{field}") and approval[field] != voice.get(field):
            fail(f"voice.approval.{field} must match the voice used for the approved sample")
    if approval.get("status") not in ("pending", "approved", "rejected"):
        fail("voice.approval.status must be pending, approved or rejected")
    if approval.get("status") == "rejected":
        fail("voice sample was rejected; select a different reference")
    elif approval.get("status") != "approved":
        pending("voice sample has not been explicitly approved")
    check_file(approval.get("sample_path"), approval.get("sample_sha256"), "voice.approval")
    if approval.get("status") == "approved":
        text_field(approval.get("approved_by"), "voice.approval.approved_by")
        text_field(approval.get("approved_at"), "voice.approval.approved_at")

    assets = array(data.get("assets"), "assets")
    if not assets:
        pending("assets: no assets registered")
    asset_map, path_set, hash_set = {}, set(), set()
    for i, raw in enumerate(assets):
        label = f"assets[{i}]"
        asset = obj(raw, label)
        aid = asset.get("id")
        if not isinstance(aid, str) or not aid:
            fail(f"{label}.id must be nonempty text")
            continue
        if aid in asset_map:
            fail(f"{label}: duplicate asset id")
        asset_map[aid] = asset
        path = check_file(asset.get("path"), asset.get("sha256"), label)
        if path in path_set and path is not None:
            fail(f"{label}: duplicate asset path")
        path_set.add(path)
        sha = asset.get("sha256")
        if isinstance(sha, str) and SHA256.fullmatch(sha):
            if sha.lower() in hash_set:
                fail(f"{label}: duplicate asset content SHA-256")
            hash_set.add(sha.lower())
        kind = asset.get("kind")
        if kind not in ("image", "audio", "video", "font", "graphic"):
            fail(f"{label}.kind is unsupported")
        provider = asset.get("provider")
        real_photo = kind == "image" and provider == "real-photo"
        if kind in ("image", "video") and provider != "kie" and not real_photo:
            fail(f"{label}: generated visual assets must come from kie")
        if isinstance(provider, str) and any(x in provider.lower() for x in ("chatgpt", "imagegen", "openai", "dall-e")):
            fail(f"{label}: prohibited image provider")
        if kind == "graphic" and provider != "local-code":
            fail(f"{label}: explanatory graphics must be local-code")
        if kind in ("image", "video") and not real_photo:
            text_field(asset.get("model"), f"{label}.model (record actual provider model ID)")
        if kind == "image" and provider == "kie" and asset.get("model") and asset["model"] != "nano-banana-2-lite":
            text_field(asset.get("fallback_reason"), f"{label}.fallback_reason (Lite has first priority)")
        source = obj(asset.get("source"), f"{label}.source")
        if real_photo:
            if source.get("type") not in ("licensed", "owned"):
                fail(f"{label}: real-photo requires licensed or owned provenance")
            if not source.get("url"):
                pending(f"{label}: real-photo provenance URL required")
            if "discovery_provider" in asset and asset["discovery_provider"] != "apify":
                fail(f"{label}.discovery_provider must be apify when specified")
        if source.get("type") not in ("generated", "licensed", "owned", "code"):
            fail(f"{label}.source.type is unsupported")
        text_field(source.get("license"), f"{label}.source.license")
        if source.get("rights_confirmed") is not True:
            pending(f"{label}: usage rights must be checked")
        if source.get("url") and not valid_url(source["url"]):
            fail(f"{label}.source.url must be http(s) without credentials")
        if source.get("type") in ("generated", "licensed") and not source.get("url"):
            pending(f"{label}: provenance URL required")
        qa = obj(asset.get("qa"), f"{label}.qa")
        for flag in ("watermark", "third_party_logo", "particles"):
            if qa.get(flag) is not False:
                fail(f"{label}.qa.{flag} must be false")
        if qa.get("approved") is not True:
            pending(f"{label}: visual/audio review pending")

    scenes = array(data.get("scenes"), "scenes")
    if not scenes:
        pending("scenes: no storyboard yet")
    scene_ids, visual_uses, families = set(), set(), []
    previous = None
    for i, raw in enumerate(scenes):
        label = f"scenes[{i}]"
        scene = obj(raw, label)
        sid = scene.get("id")
        if not isinstance(sid, str) or not sid or sid in scene_ids:
            fail(f"{label}.id must be unique nonempty text")
        else:
            scene_ids.add(sid)
        text_field(scene.get("title"), f"{label}.title")
        start, end = scene.get("start"), scene.get("end")
        timing_valid = number(start) and number(end) and 0 <= start < end <= duration
        if not timing_valid:
            fail(f"{label}: require 0 <= start < end <= durationSeconds")
        if i == 0 and start != 0:
            fail("first scene must start at zero")
        refs = array(scene.get("asset_ids"), f"{label}.asset_ids")
        local_refs = set()
        for aid in refs:
            if not isinstance(aid, str) or aid not in asset_map:
                fail(f"{label}: unknown asset reference")
                continue
            if aid in local_refs:
                fail(f"{label}: repeated asset reference")
            local_refs.add(aid)
            if asset_map[aid].get("kind") in ("image", "video"):
                if aid in visual_uses:
                    fail(f"{label}: image/video repeated across scenes")
                visual_uses.add(aid)
        transition = obj(scene.get("transition"), f"{label}.transition")
        family = transition.get("family")
        if not isinstance(family, str) or family not in FAMILIES:
            fail(f"{label}: unsupported transition family (circles/rings prohibited)")
            family = "invalid"
        overlap = transition.get("durationSeconds")
        if not number(overlap) or overlap < 0 or (timing_valid and overlap > end - start):
            fail(f"{label}: transition duration must fit the scene")
            overlap = 0
        if i > 0:
            families.append(family)
            if len(families) > 1 and family == families[-2]:
                fail(f"{label}: consecutive transitions repeat the same family")
            if overlap <= 0:
                fail(f"{label}: transitions must overlap")
            if timing_valid and previous:
                ps, pe = previous.get("start"), previous.get("end")
                if number(ps) and start <= ps:
                    fail(f"{label}: scene start times must increase")
                if number(pe) and pe + 1e-6 < start + overlap:
                    fail(f"{label}: previous scene ends before transition overlap completes")
        previous = scene
    if scenes and isinstance(scenes[-1], dict) and scenes[-1].get("end") != duration:
        fail("last scene must end at output.durationSeconds")
    if len(families) >= 5 and len(set(families)) < minimum:
        fail(f"transitions: at least {minimum} families required for 5+ changes")

    sources = array(data.get("sources"), "sources")
    if project.get("content_domain") == "legal" and not sources:
        pending("legal content requires dated primary research sources")
    source_ids = set()
    for i, raw in enumerate(sources):
        source = obj(raw, f"sources[{i}]")
        sid = source.get("id")
        if not isinstance(sid, str) or not sid or sid in source_ids:
            fail(f"sources[{i}].id must be unique text")
        else:
            source_ids.add(sid)
        for key in ("title", "accessed_at"):
            text_field(source.get(key), f"sources[{i}].{key}")
        if not valid_url(source.get("url")):
            fail(f"sources[{i}].url must be http(s) without credentials")
    cues = array(data.get("subtitleCues", []), "subtitleCues")
    if not cues:
        pending("subtitleCues: timed subtitles are required for final delivery")
    if cues and data.get("subtitlesVerified") is not True:
        pending("subtitleCues must be verified against actual narration")
    previous_end = 0
    for i, raw in enumerate(cues):
        cue = obj(raw, f"subtitleCues[{i}]")
        start, end = cue.get("start"), cue.get("end")
        if not number(start) or not number(end) or not 0 <= start < end <= duration:
            fail(f"subtitleCues[{i}]: invalid timing")
        elif start < previous_end - 1e-6:
            fail(f"subtitleCues[{i}]: overlap or unordered cues")
        else:
            previous_end = end
        text_field(cue.get("text"), f"subtitleCues[{i}].text")
    audio = obj(data.get("audio"), "audio")
    for key in ("voice", "music"):
        aid = audio.get(key)
        if not aid:
            pending(f"audio.{key}: required")
        elif not isinstance(aid, str) or aid not in asset_map or asset_map[aid].get("kind") != "audio":
            fail(f"audio.{key}: must reference an audio asset")
        elif key == "voice" and asset_map[aid].get("provider") != "fish":
            fail("audio.voice: the narration asset must have Fish provenance")
        elif key == "voice":
            if not reference:
                pending("audio.voice: narration reference_id is pending voice selection")
            elif asset_map[aid].get("reference_id") != reference:
                fail("audio.voice: narration reference_id must match the approved voice")
            if asset_map[aid].get("model") != voice.get("model"):
                fail("audio.voice: narration TTS engine must match the voice record")
    for key in ("voiceVolume", "musicVolume"):
        value = audio.get(key, 1 if key == "voiceVolume" else 0.12)
        if not number(value) or not 0 <= value <= 1:
            fail(f"audio.{key}: must be within 0..1")
    for i, raw in enumerate(array(audio.get("sfx", []), "audio.sfx")):
        sfx = obj(raw, f"audio.sfx[{i}]")
        aid = sfx.get("asset_id")
        if not isinstance(aid, str) or aid not in asset_map or asset_map[aid].get("kind") != "audio":
            fail(f"audio.sfx[{i}]: must reference an audio asset")
        if not number(sfx.get("start")) or not 0 <= sfx["start"] < duration:
            fail(f"audio.sfx[{i}]: invalid start")
        if not number(sfx.get("volume", 0.5)) or not 0 <= sfx.get("volume", 0.5) <= 1:
            fail(f"audio.sfx[{i}]: volume must be within 0..1")
    delivery = obj(data.get("delivery"), "delivery")
    check_path(delivery.get("video_path"), "delivery.video_path")
    return {"status": "invalid" if errors else ("draft" if warnings else "ready_for_review"),
            "errors": errors, "warnings": warnings,
            "profile_adjustments": adjustments,
            "note": "Declarations and technical checks do not replace human viewing/listening or legal review."}


def doctor():
    versions = {}
    for tool in ("ffmpeg", "ffprobe", "node", "npm", "git"):
        executable = shutil.which(tool)
        if not executable:
            versions[tool] = {"available": False}
            continue
        arg = "-version" if tool in ("ffmpeg", "ffprobe") else "--version"
        result = subprocess.run([executable, arg], capture_output=True, text=True, timeout=20)
        versions[tool] = {"available": result.returncode == 0,
                          "version": (result.stdout or result.stderr).splitlines()[0][:180]}
    return {"python": sys.version.split()[0], "tools": versions,
            "credentials": {name: {"configured": bool(os.environ.get(name))} for name in ENV_NAMES},
            "network_tested": False, "api_calls": 0,
            "note": "Presence only; no credential values printed and no balances or connections tested."}


def init_project(destination, title):
    destination = Path(destination)
    if destination.exists():
        raise ValueError("destination already exists; refusing to overwrite")
    destination.mkdir(parents=True)
    for name in ("assets", "audio", "research", "reviews", "out"):
        (destination / name).mkdir()
    write_json(destination / "project.json", project_template(title))
    write_json(destination / "state.json", {"schema_version": 1, "phase": "brief", "updated_at": now(),
                                          "completed": [], "pending": ["brief", "research", "voice_sample_approval", "assets", "storyboard", "render", "human_review"],
                                          "provider_tasks": [], "artifacts": []})
    write_json(destination / "quality-plan.json", {"schema_version": 1,
        "checks": ["policy_and_provenance", "voice_sample_explicit_approval", "legal_source_review",
                   "watermark_and_logo_visual_review", "subtitle_audio_alignment", "transition_and_overlap_review",
                   "ffprobe_format", "loudness_and_peaks", "black_and_freeze_heuristics", "full_video_human_review"],
        "reference_targets": {"integrated_lufs": -16, "true_peak_db_max": -1.5, "preferred_true_peak_dbtp": -2,
                              "black_intervals": 0, "width": 1080, "height": 1920, "fps": 30},
        "note": "Measurements flag candidates; no universal luminance threshold proves absence of flashes."})
    (destination / "brief.md").write_text(f"# {title}\n\n- Tema:\n- Público:\n- Objetivo y CTA:\n- Duración aproximada:\n- Jurisdicción y fecha relevante:\n- Presupuesto máximo y proveedores autorizados:\n- Referencias y recursos disponibles:\n- Voz: muestra pendiente de aprobación; no reutilizar una rechazada.\n\nExplica el siguiente paso en 1–3 frases. Registra decisiones y evidencia en state.json.\n", encoding="utf-8")
    return {"status": "created", "project": str(destination.resolve()), "api_calls": 0}


SECRET_PATTERNS = (
    ("private_key", re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----")),
    ("github_token", re.compile(r"\b(?:gh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,})\b")),
    ("provider_token", re.compile(r"\bsk-(?:proj-)?[A-Za-z0-9_-]{20,}\b")),
    ("bearer_token", re.compile(r"(?i)\bbearer\s+[A-Za-z0-9._~-]{24,}")),
    ("credential_assignment", re.compile(r'''(?i)(?:api[_-]?key|access[_-]?token|auth[_-]?token|client[_-]?secret|password|(?:kie|fish|apify)[_-]?(?:key|token))\s*["']?\s*[:=]\s*["']?([A-Za-z0-9_./+=~-]{20,})''')),
)
SKIP_DIRS = {".git", "node_modules", ".venv", "venv", "__pycache__", ".pytest_cache"}


def secret_scan(root):
    root = Path(root).resolve()
    if not root.exists():
        raise ValueError("scan path does not exist")
    findings, scanned, skipped = [], 0, 0
    def walk_files():
        for base, directories, files in os.walk(root, followlinks=False):
            directories[:] = [d for d in directories if d not in SKIP_DIRS and not (Path(base) / d).is_symlink()]
            for name in files:
                yield Path(base) / name
    paths = [root] if root.is_file() else walk_files()
    for path in paths:
        relative = path.name if root.is_file() else path.relative_to(root).as_posix()
        if path.is_symlink() or any(part in SKIP_DIRS for part in Path(relative).parts) or not path.is_file():
            continue
        if path.stat().st_size > 2 * 1024 * 1024:
            skipped += 1
            continue
        try:
            content = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            skipped += 1
            continue
        if "\x00" in content:
            skipped += 1
            continue
        scanned += 1
        for kind, pattern in SECRET_PATTERNS:
            for match in pattern.finditer(content):
                token = match.group(1) if kind == "credential_assignment" else ""
                if token and (token.lower().startswith(("your_", "replace_", "example_")) or len(set(token)) <= 3):
                    continue
                findings.append({"file": relative, "line": content.count("\n", 0, match.start()) + 1, "kind": kind})
    return {"status": "findings" if findings else "no_findings_in_scanned_text",
            "findings": findings, "files_scanned": scanned, "files_skipped": skipped,
            "limits": "UTF-8 text <= 2 MiB; excludes symlinks, dependency directories, git history and binary files. Not proof of absence."}


def command_output(args, timeout=1800):
    result = subprocess.run(args, capture_output=True, text=True, timeout=timeout)
    if result.returncode:
        raise ValueError(f"{Path(args[0]).name} failed (exit {result.returncode}); inspect input and tool installation")
    return result.stdout, result.stderr


def parse_number(value):
    try:
        f = float(value)
        return f if math.isfinite(f) else None
    except (TypeError, ValueError):
        return None


def inspect_video(path, luminance=False):
    path = Path(path).resolve()
    if not path.is_file():
        raise ValueError("video does not exist")
    for tool in ("ffprobe", "ffmpeg"):
        if not shutil.which(tool):
            raise ValueError(f"{tool} is required")
    # Explicit local file protocol allowlist avoids network access from crafted playlists.
    common = ["-protocol_whitelist", "file,pipe", "-i", str(path)]
    stdout, _ = command_output(["ffprobe", "-v", "error", *common, "-show_format", "-show_streams", "-of", "json"])
    probe = json.loads(stdout)
    videos = [s for s in probe.get("streams", []) if s.get("codec_type") == "video"]
    audios = [s for s in probe.get("streams", []) if s.get("codec_type") == "audio"]
    if not videos:
        raise ValueError("no video stream found")
    stream = videos[0]
    tool_versions = {}
    for tool in ("ffprobe", "ffmpeg"):
        version, _ = command_output([tool, "-version"], timeout=20)
        tool_versions[tool] = version.splitlines()[0]
    fr = stream.get("avg_frame_rate", "0/1").split("/")
    fps = float(fr[0]) / float(fr[1]) if len(fr) == 2 and float(fr[1]) else None
    vf = "blackdetect=d=0.03:pix_th=0.10:pic_th=0.98,freezedetect=n=-50dB:d=0.5"
    if luminance:
        vf += ",signalstats,metadata=print:key=lavfi.signalstats.YAVG:file=-"
    out, log = command_output(["ffmpeg", "-hide_banner", "-nostdin", *common,
                               "-map", "0:v:0", "-an", "-vf", vf, "-f", "null", "-"])
    black = [{"start": float(a), "end": float(b), "duration": float(c)}
             for a, b, c in re.findall(r"black_start:([\d.]+) black_end:([\d.]+) black_duration:([\d.]+)", log)]
    freezes = []
    for kind, value in re.findall(r"lavfi\.freezedetect\.(freeze_start|freeze_end|freeze_duration):\s*([\d.]+)", log):
        freezes.append({"event": kind, "seconds": float(value)})
    measures = None
    if audios:
        _, audio_log = command_output(["ffmpeg", "-hide_banner", "-nostdin", *common,
                                       "-map", "0:a:0", "-vn", "-af", "loudnorm=I=-16:TP=-2:LRA=11:print_format=json",
                                       "-f", "null", "-"])
        blocks = re.findall(r"\{\s*\"input_i\".*?\}", audio_log, re.S)
        if blocks:
            raw = json.loads(blocks[-1])
            measures = {"integrated_lufs": parse_number(raw.get("input_i")),
                        "true_peak_dbtp": parse_number(raw.get("input_tp")),
                        "loudness_range_lu": parse_number(raw.get("input_lra"))}
    luminance_report = None
    if luminance:
        values = [float(x) for x in re.findall(r"lavfi.signalstats.YAVG=([\d.]+)", out)]
        deltas = [(i + 1, abs(b - a)) for i, (a, b) in enumerate(zip(values, values[1:]))]
        largest = sorted(deltas, key=lambda x: x[1], reverse=True)[:10]
        luminance_report = {"frames": len(values), "largest_mean_luma_changes": [
            {"frame": i, "seconds_approx": i / fps if fps else None, "delta_yavg": d} for i, d in largest],
            "note": "Candidate cuts only. Mean luma cannot certify flash safety or detect every local flash."}
    flags = []
    if stream.get("width") != 1080 or stream.get("height") != 1920 or fps is None or abs(fps - 30) > 0.01:
        flags.append("format_differs_from_1080x1920_30fps_profile")
    if stream.get("codec_name") != "h264":
        flags.append("video_codec_differs_from_h264")
    if not audios or audios[0].get("codec_name") != "aac":
        flags.append("audio_missing_or_codec_differs_from_aac")
    if stream.get("pix_fmt") != "yuv420p":
        flags.append("pixel_format_differs_from_yuv420p")
    if audios and audios[0].get("channels") != 2:
        flags.append("audio_channels_differ_from_stereo_review_delivery_mix")
    if audios and audios[0].get("sample_rate") != "48000":
        flags.append("audio_sample_rate_differs_from_48000hz")
    if black:
        flags.append("black_intervals_require_review")
    if freezes:
        flags.append("freeze_candidates_require_review_intentional_holds_may_be_valid")
    if measures is None or measures["integrated_lufs"] is None:
        flags.append("loudness_not_measurable_or_audio_missing")
    else:
        if abs(measures["integrated_lufs"] + 16) > 1:
            flags.append("loudness_outside_reference_minus16_plusminus1_lufs")
        if measures["true_peak_dbtp"] is None or measures["true_peak_dbtp"] > -1.5:
            flags.append("true_peak_exceeds_reference_minus1_5_dbtp_or_unknown")
    return {"status": "needs_human_review", "created_at": now(), "sha256": digest(path),
            "video": {"file": path.name, "duration_seconds": parse_number(probe.get("format", {}).get("duration")),
                      "width": stream.get("width"), "height": stream.get("height"), "fps": fps,
                      "video_codec": stream.get("codec_name"),
                      "pixel_format": stream.get("pix_fmt"),
                      "audio_codec": audios[0].get("codec_name") if audios else None,
                      "audio_channels": audios[0].get("channels") if audios else None,
                      "audio_sample_rate_hz": int(audios[0]["sample_rate"]) if audios and audios[0].get("sample_rate", "").isdigit() else None},
            "method": {"tool_versions": tool_versions,
                       "video_filters": vf,
                       "audio_filter": "loudnorm=I=-16:TP=-2:LRA=11:print_format=json" if audios else None,
                       "thresholds": {"black_min_duration_seconds": 0.03, "black_pixel_threshold": 0.10,
                                      "black_picture_ratio": 0.98, "freeze_noise_db": -50, "freeze_min_duration_seconds": 0.5,
                                      "target_lufs": -16, "lufs_tolerance": 1, "true_peak_max_dbtp": -1.5,
                                      "preferred_true_peak_dbtp": -2},
                       "luminance_enabled": luminance, "modifies_input": False},
            "audio_measurements": measures, "black_intervals": black, "freeze_events": freezes,
            "luminance": luminance_report, "flags": flags,
            "human_checks_required": ["watch_and_listen_to_complete_encoded_file", "voice_intention_and_pronunciation",
                "subtitles_and_timing", "third_party_logos_watermarks_and_anatomy", "centering_safe_areas_and_transitions", "legal_claims_and_cta"],
            "limitations": "Black/freeze detection is heuristic. No measurement here approves a voice, proves legal accuracy or certifies absence of flashes."}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("doctor", help="List local prerequisites and credential presence; no API calls")
    init = sub.add_parser("init-project", help="Create a new draft; never overwrite")
    init.add_argument("destination")
    init.add_argument("--title", default="Nuevo video MILLA")
    val = sub.add_parser("validate", help="Validate project.json and local asset hashes")
    val.add_argument("manifest")
    val.add_argument("--allow-pending", action="store_true", help="Missing approvals/resources become draft warnings; policy violations stay errors")
    scan = sub.add_parser("secret-scan", help="Scan UTF-8 text; print locations/categories, never matched values")
    scan.add_argument("path")
    inspect = sub.add_parser("inspect-video", help="Measure MP4; always requires human review")
    inspect.add_argument("video")
    inspect.add_argument("--luminance", action="store_true")
    inspect.add_argument("--output", help="Write a NEW JSON report; refuses to overwrite")
    args = parser.parse_args(argv)
    try:
        if args.command == "doctor":
            result = doctor()
        elif args.command == "init-project":
            result = init_project(args.destination, args.title)
        elif args.command == "validate":
            path = Path(args.manifest).resolve()
            result = validate(json.loads(path.read_text(encoding="utf-8")), path.parent, args.allow_pending)
        elif args.command == "secret-scan":
            result = secret_scan(args.path)
        else:
            if args.output and Path(args.output).exists():
                raise ValueError("report already exists; use a new output filename")
            result = inspect_video(args.video, args.luminance)
            if args.output:
                write_json(Path(args.output), result)
        print(json.dumps(result, indent=2, ensure_ascii=False, allow_nan=False))
        return 1 if result.get("status") in ("invalid", "findings") else 0
    except (OSError, ValueError, subprocess.TimeoutExpired) as exc:
        # Avoid echoing raw source content or subprocess stderr containing credentials.
        message = str(exc) if isinstance(exc, ValueError) and not isinstance(exc, json.JSONDecodeError) else type(exc).__name__
        print(json.dumps({"status": "error", "message": message}, ensure_ascii=False), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
