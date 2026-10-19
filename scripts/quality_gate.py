import json
import os
import sys
from collections import Counter
from pathlib import Path


LEVELS = ("CRITICAL", "HIGH", "MEDIUM", "LOW")

SEMGREP_LEVELS = {
    "CRITICAL": "CRITICAL",
    "HIGH": "HIGH",
    "ERROR": "HIGH",
    "MEDIUM": "MEDIUM",
    "WARNING": "MEDIUM",
    "LOW": "LOW",
    "INFO": "LOW",
}


def read_json(filename):
    with open(filename, encoding="utf-8") as file:
        return json.load(file)


def main():
    bandit = read_json("reports/bandit.json")
    semgrep = read_json("reports/semgrep.json")

    counts = Counter()
    findings = []

    for item in bandit["results"]:
        level = item["issue_severity"].upper()

        if level not in LEVELS:
            raise ValueError(f"Unknown Bandit severity: {level}")

        counts[level] += 1
        findings.append((
            "Bandit",
            item["test_id"],
            level,
            item["filename"],
            item["line_number"],
        ))

    for item in semgrep["results"]:
        raw_level = item["extra"]["severity"].upper()
        level = SEMGREP_LEVELS[raw_level]

        counts[level] += 1
        findings.append((
            "Semgrep",
            item["check_id"],
            level,
            item["path"],
            item["start"]["line"],
        ))

    passed = (
        counts["CRITICAL"] == 0
        and counts["HIGH"] == 0
        and counts["MEDIUM"] < 5
    )

    print("=== SAST Quality Gate ===")

    for level in LEVELS:
        print(f"{level}: {counts[level]}")

    print("\nDetected findings:")

    for tool, rule, level, filename, line in findings:
        print(
            f"{tool} | {rule} | {level} | "
            f"{filename}:{line}"
        )

    status = "PASSED" if passed else "FAILED"
    print(f"\nQuality Gate: {status}")

    summary_path = os.environ.get("GITHUB_STEP_SUMMARY")

    if summary_path:
        lines = [
            "## SAST Quality Gate",
            "",
            "| Severity | Count |",
            "|---|---:|",
        ]

        for level in LEVELS:
            lines.append(f"| {level} | {counts[level]} |")

        lines.extend([
            "",
            f"**Result: {status}**",
            "",
            "Required: 0 HIGH/CRITICAL, <5 MEDIUM.",
        ])

        with open(summary_path, "a", encoding="utf-8") as file:
            file.write("\n".join(lines) + "\n")

    return 0 if passed else 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (
        OSError,
        json.JSONDecodeError,
        KeyError,
        ValueError,
    ) as error:
        print(f"Quality Gate error: {error}")
        sys.exit(2)
