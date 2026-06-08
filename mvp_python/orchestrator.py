from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Protocol

from . import prompts


class LLM(Protocol):
    def complete(self, system: str, user: str) -> str:
        ...


@dataclass
class GenerateOptions:
    book_name: str
    duration_minutes: int = 12
    mode: str = "first_encounter"
    user_note: str = ""
    factuality_retries: int = 2


def generate_script(llm: LLM, options: GenerateOptions) -> dict[str, Any]:
    recall = generate_recall(llm, options.book_name)
    profile = generate_profile(llm, options, recall)
    outline = generate_outline(llm, recall, profile)
    nodes = generate_nodes(llm, recall, profile, outline, options.duration_minutes)
    content = assemble_script(profile, outline, nodes)

    factuality_reviews: list[dict[str, Any]] = []
    factuality = review_factuality(llm, recall, profile, outline, nodes, content)
    factuality_reviews.append(factuality)

    retry_count = 0
    while not factuality.get("passed") and retry_count < options.factuality_retries:
        nodes = revise_nodes(llm, recall, outline, nodes, factuality.get("issues", []))
        content = assemble_script(profile, outline, nodes)
        factuality = review_factuality(llm, recall, profile, outline, nodes, content)
        factuality_reviews.append(factuality)
        retry_count += 1

    if factuality.get("passed"):
        final_content = content
        draft_content = ""
        quality = review_quality(llm, recall, profile, outline, final_content, factuality)
        status = "ok"
    else:
        final_content = ""
        draft_content = content
        quality = {
            "skipped": True,
            "reason": "factuality_failed",
            "message": "Quality review is skipped because factuality did not pass after retries.",
        }
        status = "factuality_failed"

    return {
        "status": status,
        "recall": recall,
        "profile": profile,
        "outline": outline,
        "nodes": nodes,
        "content": final_content,
        "draftContent": draft_content,
        "factuality": factuality,
        "factualityReviews": factuality_reviews,
        "quality": quality,
    }


def generate_recall(llm: LLM, book_name: str) -> dict[str, Any]:
    raw = llm.complete(
        prompts.RECALL_SYSTEM,
        prompts.RECALL_USER.format(book_name=book_name),
    )
    return parse_json(raw)


def generate_profile(llm: LLM, options: GenerateOptions, recall: dict[str, Any]) -> dict[str, Any]:
    raw = llm.complete(
        prompts.PROFILE_SYSTEM,
        prompts.PROFILE_USER.format(
            book_name=options.book_name,
            duration_minutes=options.duration_minutes,
            mode=options.mode,
            user_note=options.user_note or "无",
            recall_json=json.dumps(recall, ensure_ascii=False, indent=2),
        ),
    )
    return parse_json(raw)


def generate_outline(
    llm: LLM,
    recall: dict[str, Any],
    profile: dict[str, Any],
) -> dict[str, Any]:
    raw = llm.complete(
        prompts.OUTLINE_SYSTEM,
        prompts.OUTLINE_USER.format(
            recall_json=json.dumps(recall, ensure_ascii=False, indent=2),
            profile_json=json.dumps(profile, ensure_ascii=False, indent=2),
        ),
    )
    return parse_json(raw)


def generate_nodes(
    llm: LLM,
    recall: dict[str, Any],
    profile: dict[str, Any],
    outline: dict[str, Any],
    duration_minutes: int,
) -> list[dict[str, Any]]:
    segments = outline.get("segments", [])
    if not isinstance(segments, list) or not segments:
        raise ValueError("Outline must contain a non-empty segments array.")

    target_words = max(350, int(duration_minutes * 280 / len(segments)))
    nodes: list[dict[str, Any]] = []

    for segment in segments:
        raw = llm.complete(
            prompts.NODE_SYSTEM,
            prompts.NODE_USER.format(
                recall_json=json.dumps(recall, ensure_ascii=False, indent=2),
                profile_json=json.dumps(profile, ensure_ascii=False, indent=2),
                outline_json=json.dumps(outline, ensure_ascii=False, indent=2),
                segment_json=json.dumps(segment, ensure_ascii=False, indent=2),
                target_words=target_words,
            ),
        ).strip()
        node = normalize_node(parse_json(raw), segment)
        nodes.append(node)

    return nodes


def normalize_node(raw_node: Any, segment: dict[str, Any]) -> dict[str, Any]:
    if isinstance(raw_node, str):
        raw_node = {"narration": raw_node}
    if not isinstance(raw_node, dict):
        raw_node = {"narration": str(raw_node)}

    return {
        "node_id": raw_node.get("node_id") or segment.get("node_id") or str(segment.get("id", "")),
        "title": raw_node.get("title") or segment.get("title") or "",
        "source_scenes": raw_node.get("source_scenes") or segment.get("source_scenes") or [],
        "required_facts": raw_node.get("required_facts") or segment.get("required_facts") or [],
        "causal_context": raw_node.get("causal_context") or segment.get("causal_context") or "",
        "emotional_context": raw_node.get("emotional_context") or segment.get("emotional_context") or "",
        "narration": raw_node.get("narration") or "",
        "uncertainty_notes": raw_node.get("uncertainty_notes") or segment.get("uncertainty_notes") or [],
    }


def assemble_script(
    profile: dict[str, Any],
    outline: dict[str, Any],
    nodes: list[dict[str, Any]],
) -> str:
    title = profile.get("title") or "这本书"
    opening = outline.get("openingHook") or f"好，我们来讲《{title}》。"
    closing = outline.get("closingQuestion") or "你会怎样评价这个人物的选择？"

    parts = [
        f"好，我们来讲《{title}》。",
        opening,
    ]

    shallow = profile.get("shallowMisread")
    if shallow:
        parts.extend(["很多人会先把它讲成：", shallow, "但如果这样讲，就太浅了。"])

    for node in nodes:
        narration = node.get("narration", "").strip()
        if narration:
            parts.append(narration)

    parts.extend(["所以讲到这里，我反而想把问题留给你：", closing])
    return "\n\n".join(part for part in parts if part)


def review_factuality(
    llm: LLM,
    recall: dict[str, Any],
    profile: dict[str, Any],
    outline: dict[str, Any],
    nodes: list[dict[str, Any]],
    script: str,
) -> dict[str, Any]:
    raw = llm.complete(
        prompts.FACTUALITY_REVIEW_SYSTEM,
        prompts.FACTUALITY_REVIEW_USER.format(
            recall_json=json.dumps(recall, ensure_ascii=False, indent=2),
            profile_json=json.dumps(profile, ensure_ascii=False, indent=2),
            outline_json=json.dumps(outline, ensure_ascii=False, indent=2),
            nodes_json=json.dumps(nodes, ensure_ascii=False, indent=2),
            script=script,
        ),
    )
    result = parse_json(raw)
    if not isinstance(result, dict):
        raise ValueError("Factuality review must return a JSON object.")
    result.setdefault("passed", False)
    result.setdefault("issues", [])
    return result


def revise_nodes(
    llm: LLM,
    recall: dict[str, Any],
    outline: dict[str, Any],
    nodes: list[dict[str, Any]],
    issues: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    raw = llm.complete(
        prompts.REVISION_SYSTEM,
        prompts.REVISION_USER.format(
            recall_json=json.dumps(recall, ensure_ascii=False, indent=2),
            outline_json=json.dumps(outline, ensure_ascii=False, indent=2),
            nodes_json=json.dumps(nodes, ensure_ascii=False, indent=2),
            issues_json=json.dumps(issues, ensure_ascii=False, indent=2),
        ),
    )
    result = parse_json(raw)
    revised_nodes = result.get("nodes") if isinstance(result, dict) else result
    if not isinstance(revised_nodes, list):
        raise ValueError("Node revision must return a nodes array.")

    segment_by_id = {segment.get("node_id"): segment for segment in outline.get("segments", [])}
    normalized = []
    for node in revised_nodes:
        segment = segment_by_id.get(node.get("node_id"), {}) if isinstance(node, dict) else {}
        normalized.append(normalize_node(node, segment))
    return normalized


def review_quality(
    llm: LLM,
    recall: dict[str, Any],
    profile: dict[str, Any],
    outline: dict[str, Any],
    script: str,
    factuality: dict[str, Any],
) -> dict[str, Any]:
    raw = llm.complete(
        prompts.REVIEW_SYSTEM,
        prompts.REVIEW_USER.format(
            recall_json=json.dumps(recall, ensure_ascii=False, indent=2),
            profile_json=json.dumps(profile, ensure_ascii=False, indent=2),
            outline_json=json.dumps(outline, ensure_ascii=False, indent=2),
            factuality_json=json.dumps(factuality, ensure_ascii=False, indent=2),
            script=script,
        ),
    )
    return parse_json(raw)


def parse_json(raw: str) -> Any:
    text = raw.strip()
    if text.startswith("```"):
        lines = text.splitlines()
        if lines and lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].startswith("```"):
            lines = lines[:-1]
        text = "\n".join(lines).strip()

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        start_candidates = [idx for idx in [text.find("{"), text.find("[")] if idx != -1]
        if not start_candidates:
            raise

        start = min(start_candidates)
        end = max(text.rfind("}"), text.rfind("]"))
        if end <= start:
            raise
        return json.loads(text[start : end + 1])


def save_result(result: dict[str, Any], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
