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

# Keep this set in lockstep with remotion-template/src/manifest-validation.mjs.
# Aspirational transition names are rejected until the renderer implements them.
FAMILIES = {"wipe", "push", "mask", "depth", "pan", "zoom", "fade"}
SHA256 = re.compile(r"^[a-fA-F0-9]{64}$")
ENV_NAMES = ("KIE_API_KEY", "FISH_API_KEY", "APIFY_TOKEN")
# ECMAScript WhiteSpace + LineTerminator code points used by trim() and /\s/.
JS_WHITESPACE = "\u0009\u000a\u000b\u000c\u000d\u0020\u00a0\u1680\u2000\u2001\u2002\u2003\u2004\u2005\u2006\u2007\u2008\u2009\u200a\u2028\u2029\u202f\u205f\u3000\ufeff"
JS_WHITESPACE_RE = re.compile(f"[{re.escape(JS_WHITESPACE)}]+")


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
    if (not isinstance(value, str) or not value or "\\" in value or
            any(ord(char) < 32 for char in value) or any(char in value for char in "%?#")):
        raise ValueError("expected a relative POSIX path")
    raw_parts = value.split("/")
    if any(part in ("", ".", "..") for part in raw_parts):
        raise ValueError("empty, dot and traversal path segments are forbidden")
    p = PurePosixPath(value)
    if p.is_absolute() or re.match(r"^[A-Za-z][A-Za-z0-9+.-]*:", value):
        raise ValueError("absolute paths and traversal are forbidden")
    target = (root / value).resolve()
    if not target.is_relative_to(root.resolve()) or target == root.resolve():
        raise ValueError("path must stay inside the project")
    return target


def safe_public_path(root, value):
    """Resolve the exact file Remotion staticFile(value) reads from public/."""
    public = safe_path(root, "public")
    return safe_path(public, value)


def valid_url(value):
    if not isinstance(value, str):
        return False
    try:
        p = urlparse(value)
        return p.scheme in ("https", "http") and bool(p.hostname) and not p.username and not p.password
    except ValueError:
        return False


def number(value):
    if not isinstance(value, (float, int)) or isinstance(value, bool):
        return False
    try:
        return math.isfinite(value)
    except OverflowError:
        return False


def frame_of(seconds, fps=30):
    """Match JavaScript Math.round for non-negative timeline values."""
    scaled = seconds * fps
    try:
        if not math.isfinite(scaled):
            return math.inf
    except OverflowError:
        return math.inf
    return math.floor(scaled + 0.5)


def utf16_length(value):
    """Match JavaScript string.length used by the renderer's layout guards."""
    return len(value.encode("utf-16-le", errors="surrogatepass")) // 2


def js_trim(value):
    return value.strip(JS_WHITESPACE)


def normalize_js_text(value):
    return JS_WHITESPACE_RE.sub(" ", js_trim(value))


def project_template(title="Nuevo video MILLA"):
    return {
        "schema_version": 1,
        "project": {"id": "nuevo-video", "title": title, "content_domain": "legal"},
        "output": {"width": 1080, "height": 1920, "fps": 30, "durationSeconds": 55},
        "quality": {"particles_allowed": False, "watermarks_allowed": False,
                    "allowed_image_providers": ["kie"], "minimum_transition_families": 4},
        "voice": {"provider": "fish", "model": "", "reference_id": "", "rejected_reference_ids": [],
                  "approval": {"status": "pending", "model": "", "reference_id": "", "sample_path": "audio/voice-sample.wav",
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
        if not isinstance(value, str) or not js_trim(value):
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
        try:
            path = safe_public_path(root, path_value)
        except ValueError as exc:
            fail(f"{label}.path: {exc}")
            path = None
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
        fail(f"quality.minimum_transition_families must be an integer within 1..{len(FAMILIES)} (default 4)")
        minimum = 4
    elif minimum < 4:
        rationale = quality.get("transition_variety_rationale")
        if not isinstance(rationale, str) or not js_trim(rationale):
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
    else:
        total_frames = frame_of(duration)
        if not isinstance(total_frames, int) or not 1 <= total_frames <= 2**53 - 1:
            fail("output.durationSeconds must produce a positive safe integer frame count")
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
        if not isinstance(aid, str) or not js_trim(aid) or utf16_length(aid) > 100:
            fail(f"{label}.id must be nonempty text of at most 100 characters")
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
        if kind == "image" and provider == "kie" and source.get("type") != "generated":
            fail(f"{label}: Kie images require source.type generated")
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

    def check_diagram(raw, label):
        if not isinstance(raw, dict):
            fail(f"{label}: expected object")
            return
        nodes = raw.get("nodes")
        edges = raw.get("edges")
        if not isinstance(nodes, list) or not 1 <= len(nodes) <= 6:
            fail(f"{label}.nodes must contain 1..6 nodes")
            nodes = []
        if not isinstance(edges, list):
            fail(f"{label}.edges must be an array")
            edges = []
        node_map = {}
        positioned = []
        for j, raw_node in enumerate(nodes):
            node_label = f"{label}.nodes[{j}]"
            if not isinstance(raw_node, dict):
                fail(f"{node_label}: expected object")
                continue
            nid, caption = raw_node.get("id"), raw_node.get("label")
            if not isinstance(nid, str) or not js_trim(nid) or utf16_length(nid) > 64:
                fail(f"{node_label}.id must be nonempty text of at most 64 characters")
            elif nid in node_map:
                fail(f"{node_label}.id must be unique within the diagram")
            else:
                node_map[nid] = raw_node
            if not isinstance(caption, str) or not js_trim(caption) or utf16_length(caption) > 28:
                fail(f"{node_label}.label must be nonempty text of at most 28 characters")
            x, y = raw_node.get("x"), raw_node.get("y")
            if not number(x) or not number(y) or not 15 <= x <= 85 or not 15 <= y <= 85:
                fail(f"{node_label}: x/y must be finite numbers within 15..85")
                continue
            for other_x, other_y in positioned:
                if abs(x - other_x) * 8.4 < 214 and abs(y - other_y) * 4.8 < 102:
                    fail(f"{node_label}: diagram nodes overlap")
            positioned.append((x, y))
        for j, raw_edge in enumerate(edges):
            edge_label = f"{label}.edges[{j}]"
            if not isinstance(raw_edge, dict):
                fail(f"{edge_label}: expected object")
                continue
            source_id, target_id = raw_edge.get("from"), raw_edge.get("to")
            if (not isinstance(source_id, str) or not isinstance(target_id, str) or
                    source_id not in node_map or target_id not in node_map or source_id == target_id):
                fail(f"{edge_label}: from/to must reference distinct diagram nodes")
            caption = raw_edge.get("label")
            if caption is not None and (not isinstance(caption, str) or not js_trim(caption) or utf16_length(caption) > 24):
                fail(f"{edge_label}.label must be nonempty text of at most 24 characters")

    scenes = array(data.get("scenes"), "scenes")
    if not scenes:
        pending("scenes: no storyboard yet")
    scene_ids, visual_uses, families = set(), set(), []
    previous_timing = None
    total_frames = frame_of(duration)
    for i, raw in enumerate(scenes):
        label = f"scenes[{i}]"
        scene = obj(raw, label)
        sid = scene.get("id")
        if not isinstance(sid, str) or not js_trim(sid) or utf16_length(sid) > 100 or sid in scene_ids:
            fail(f"{label}.id must be unique nonempty text of at most 100 characters")
        else:
            scene_ids.add(sid)
        title = scene.get("title")
        if not isinstance(title, str) or not js_trim(title) or utf16_length(title) > 74:
            fail(f"{label}.title must be nonempty text of at most 74 characters")
        for field, limit in (("kicker", 48), ("body", 145)):
            value = scene.get(field)
            if value is not None and (not isinstance(value, str) or not js_trim(value) or utf16_length(value) > limit):
                fail(f"{label}.{field} must be nonempty text of at most {limit} characters when present")
        if "theme" in scene and scene.get("theme") not in ("ivory", "navy"):
            fail(f"{label}.theme must be ivory or navy when present")
        if "kind" in scene:
            fail(f"{label}.kind is not implemented; use image/body/diagram fields instead")
        start, end = scene.get("start"), scene.get("end")
        timing_valid = number(start) and number(end) and 0 <= start < end <= duration
        start_frame = end_frame = None
        if not timing_valid:
            fail(f"{label}: require 0 <= start < end <= durationSeconds")
        else:
            start_frame, end_frame = frame_of(start), frame_of(end)
            if end_frame <= start_frame or end_frame > total_frames:
                fail(f"{label}: times must span at least one frame and stay inside the composition")
        if i == 0 and start != 0:
            fail("first scene must start at zero")
        refs = array(scene.get("asset_ids"), f"{label}.asset_ids")
        if len(refs) > 3:
            fail(f"{label}.asset_ids supports at most 3 images")
        local_refs = set()
        for aid in refs:
            if not isinstance(aid, str) or aid not in asset_map:
                fail(f"{label}: unknown asset reference")
                continue
            if aid in local_refs:
                fail(f"{label}: repeated asset reference")
            local_refs.add(aid)
            if asset_map[aid].get("kind") != "image":
                fail(f"{label}: scene assets must be registered images; video/font/graphic rendering is not implemented")
            elif aid in visual_uses:
                fail(f"{label}: image repeated across scenes")
            else:
                visual_uses.add(aid)
        diagram = scene.get("diagram")
        if diagram is not None:
            check_diagram(diagram, f"{label}.diagram")
        if diagram is not None and refs and scene.get("body") is not None:
            fail(f"{label}: image + diagram + body exceeds the safe layout zones")
        transition = obj(scene.get("transition"), f"{label}.transition")
        family = transition.get("family")
        if not isinstance(family, str) or family not in FAMILIES:
            fail(f"{label}: unsupported transition family (circles/rings prohibited)")
            family = "invalid"
        overlap = transition.get("durationSeconds")
        overlap_valid = number(overlap) and overlap >= 0
        overlap_frames = frame_of(overlap) if overlap_valid else 0
        if (not overlap_valid or
                (start_frame is not None and end_frame is not None and overlap_frames >= end_frame - start_frame)):
            fail(f"{label}: transition duration must fit the scene")
        if i == 0 and overlap_frames != 0:
            fail("first scene transition must round to zero frames")
        if i > 0:
            families.append(family)
            if len(families) > 1 and family == families[-2]:
                fail(f"{label}: consecutive transitions repeat the same family")
            if overlap_frames < 2:
                fail(f"{label}: transitions must overlap by at least 2 encoded frames")
            if start_frame is not None and end_frame is not None and previous_timing is not None:
                previous_start, previous_end = previous_timing
                if start_frame <= previous_start or end_frame <= previous_end:
                    fail(f"{label}: scene start and end frames must both increase")
                if previous_end < start_frame + overlap_frames:
                    fail(f"{label}: previous scene ends before transition overlap completes")
        previous_timing = (start_frame, end_frame) if start_frame is not None and end_frame is not None else None
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
        fail("subtitleCues must be verified against actual narration before rendering")
    previous_end_frame = -1
    for i, raw in enumerate(cues):
        label = f"subtitleCues[{i}]"
        cue = obj(raw, label)
        start, end = cue.get("start"), cue.get("end")
        cue_start_frame = cue_end_frame = None
        if not number(start) or not number(end) or not 0 <= start < end <= duration:
            fail(f"{label}: invalid timing")
        else:
            cue_start_frame, cue_end_frame = frame_of(start), frame_of(end)
            if cue_end_frame <= cue_start_frame or cue_start_frame < previous_end_frame:
                fail(f"{label}: cues must be ordered, non-overlapping and at least one frame long")
            previous_end_frame = cue_end_frame
        cue_text = cue.get("text")
        if not isinstance(cue_text, str) or not js_trim(cue_text) or utf16_length(cue_text) > 85:
            fail(f"{label}.text must be nonempty text of at most 85 characters")
        words = cue.get("words")
        if words is not None:
            if not isinstance(words, list) or not words:
                fail(f"{label}.words must be a nonempty array of verified word timings")
                words = []
            if data.get("wordTimestampsVerified") is not True:
                fail(f"{label}.words requires wordTimestampsVerified true")
            normalized_words = []
            previous_word_end = cue_start_frame
            for j, raw_word in enumerate(words):
                word_label = f"{label}.words[{j}]"
                if not isinstance(raw_word, dict):
                    fail(f"{word_label}: expected object")
                    continue
                word_text = raw_word.get("text")
                if not isinstance(word_text, str) or not js_trim(word_text) or utf16_length(word_text) > 40:
                    fail(f"{word_label}.text must be nonempty text of at most 40 characters")
                else:
                    normalized_words.append(word_text)
                word_start, word_end = raw_word.get("start"), raw_word.get("end")
                if (not number(word_start) or not number(word_end) or
                        not number(start) or not number(end) or
                        word_start < start or word_end > end or word_end <= word_start):
                    fail(f"{word_label}: word timing must stay inside its cue")
                    continue
                word_start_frame, word_end_frame = frame_of(word_start), frame_of(word_end)
                if (previous_word_end is not None and
                        (word_start_frame < previous_word_end or word_end_frame <= word_start_frame)):
                    fail(f"{word_label}: words must be ordered, non-overlapping and at least one frame long")
                previous_word_end = word_end_frame
            if isinstance(cue_text, str):
                if normalize_js_text(" ".join(normalized_words)) != normalize_js_text(cue_text):
                    fail(f"{label}.words must reproduce the cue text exactly")
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
        if (not isinstance(aid, str) or not js_trim(aid) or utf16_length(aid) > 100 or
                aid not in asset_map or asset_map[aid].get("kind") != "audio"):
            fail(f"audio.sfx[{i}]: must reference an audio asset")
        if (not number(sfx.get("start")) or not 0 <= sfx["start"] < duration or
                (number(sfx.get("start")) and frame_of(sfx["start"]) >= total_frames)):
            fail(f"audio.sfx[{i}]: invalid start")
        if not number(sfx.get("volume", 0.25)) or not 0 <= sfx.get("volume", 0.25) <= 1:
            fail(f"audio.sfx[{i}]: volume must be within 0..1")
        effect_duration = sfx.get("duration")
        if (effect_duration is not None and
                (not number(effect_duration) or effect_duration <= 0 or
                 (number(effect_duration) and frame_of(effect_duration) < 1))):
            fail(f"audio.sfx[{i}]: duration must span at least one encoded frame")
    if data.get("fontAssetId"):
        fail("fontAssetId is not implemented by the base renderer")
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
    if destination.exists() or destination.is_symlink():
        raise ValueError("destination already exists; refusing to overwrite")
    template = Path(__file__).resolve().parent.parent / "assets" / "remotion-template"
    if not template.is_dir():
        raise ValueError("bundled Remotion template is missing")
    shutil.copytree(template, destination,
                    ignore=shutil.ignore_patterns("node_modules", "out", ".env*", "*.log"))
    for path in ("public/assets", "public/audio", "research", "reviews", "out"):
        (destination / path).mkdir(parents=True, exist_ok=True)
    write_json(destination / "project.json", project_template(title))
    write_json(destination / "state.json", {"schema_version": 1, "phase": "brief", "updated_at": now(),
                                          "completed": [], "pending": ["brief", "research", "voice_sample_approval", "assets", "storyboard", "render", "human_review"],
                                          "provider_tasks": [], "artifacts": []})
    write_json(destination / "quality-plan.json", {"schema_version": 1,
        "checks": ["policy_and_provenance", "voice_sample_explicit_approval", "legal_source_review",
                   "watermark_and_logo_visual_review", "subtitle_audio_alignment", "transition_and_overlap_review",
                   "ffprobe_format", "loudness_and_peaks", "black_and_freeze_heuristics", "full_video_human_review"],
        "reference_targets": {"integrated_lufs": -16, "true_peak_max_dbtp": -1.5, "preferred_true_peak_dbtp": -2,
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
