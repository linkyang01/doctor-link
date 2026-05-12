from __future__ import annotations

from collections import Counter

from doctor_link.core.models import ScanResult, TestPlan


REQUIRED_EXTENSIONS = {
    "mp4": "Basic MP4 playback",
    "mkv": "MKV container playback",
    "mov": "MOV playback",
    "avi": "AVI playback",
    "flv": "FLV playback",
    "ts": "TS transport stream playback",
    "m2ts": "M2TS / Blu-ray stream playback",
    "webm": "WebM playback",
    "wmv": "WMV playback",
    "srt": "External SRT subtitle test",
    "ass": "External ASS subtitle test",
    "ssa": "External SSA subtitle test",
    "iso": "ISO disc image test",
}

REQUIRED_FOLDERS = {
    "BDMV": "Blu-ray folder structure test",
    "VIDEO_TS": "DVD folder structure test",
}


def generate_test_plan(scan_result: ScanResult) -> TestPlan:
    """Generate a basic test plan from detected files."""
    extensions = Counter(item.extension or "no-extension" for item in scan_result.files)
    detected_folder_names = {item.path.parent.name for item in scan_result.files}

    missing_categories: list[str] = []
    recommended_tests: list[str] = []

    for extension, description in REQUIRED_EXTENSIONS.items():
        if extensions.get(extension, 0) == 0:
            missing_categories.append(f"Missing .{extension}: {description}")
        else:
            recommended_tests.append(f"Run {description} with detected .{extension} sample(s)")

    for folder, description in REQUIRED_FOLDERS.items():
        if folder not in detected_folder_names:
            missing_categories.append(f"Missing {folder}/ folder: {description}")
        else:
            recommended_tests.append(f"Run {description}")

    return TestPlan(
        title="Doctor link Test Plan",
        missing_categories=missing_categories,
        recommended_tests=recommended_tests,
        detected_extensions=dict(extensions),
    )
