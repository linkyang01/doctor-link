from pathlib import Path

from doctor_link.diagnose_report import build_report

NL = "\n"


def build_summary(files: list[Path]) -> str:
    report = build_report(files)
    lines = [
        "# Doctor link diagnose-now",
        "",
        "Files: " + str(report["files"]),
        "",
        "## Extensions",
    ]
    extensions = report["extensions"]
    lines += ["- " + key + ": " + str(extensions[key]) for key in extensions]
    lines += ["", "## Recommendations"]
    lines += ["- " + item for item in report["recommendations"]]
    return NL.join(lines) + NL
