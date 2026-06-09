from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any


FIELD_MARKERS = [
    "source_scenes",
    "scene_moment",
    "character_intro_notes",
    "opening_bridge",
    "companion_insight",
    "transition_to_next",
]

ROLE_CARD_PATTERN = re.compile(r"(^|\n\n)\s*[\u4e00-\u9fffA-Za-z0-9·]{2,12}[：:]\s*\S+")


def main() -> None:
    parser = argparse.ArgumentParser(description="Check generated script output for field-stitching regressions.")
    parser.add_argument("result_json", help="Path to a generated result JSON file.")
    args = parser.parse_args()

    result = json.loads(Path(args.result_json).read_text(encoding="utf-8"))
    content = str(result.get("content") or "")
    problems = check_content(content)

    if problems:
        for problem in problems:
            print(f"FAIL: {problem}")
        raise SystemExit(1)

    print("regression check ok")


def check_content(content: str) -> list[str]:
    problems: list[str] = []
    stripped = content.strip()

    if not stripped:
        return ["content is empty"]

    for marker in FIELD_MARKERS:
        if marker in stripped:
            problems.append(f"content contains internal field marker: {marker}")

    if ROLE_CARD_PATTERN.search(stripped):
        problems.append("content appears to contain a role-card line like '角色名：解释'")

    paragraphs = normalize_paragraphs(stripped)
    for previous, current in zip(paragraphs, paragraphs[1:]):
        if previous == current:
            problems.append("content contains consecutive duplicate paragraphs")
            break

    if len(paragraphs) < 2:
        problems.append("content should contain natural paragraphs")

    if "{" in stripped or "}" in stripped:
        problems.append("content appears to contain JSON syntax")

    return problems


def normalize_paragraphs(content: str) -> list[str]:
    paragraphs = re.split(r"\n\s*\n", content)
    return [" ".join(paragraph.split()) for paragraph in paragraphs if paragraph.strip()]


if __name__ == "__main__":
    main()
