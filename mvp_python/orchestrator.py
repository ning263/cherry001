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
    narrative_retries: int = 1


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
        nodes = revise_nodes_for_factuality(llm, recall, outline, nodes, factuality.get("issues", []))
        content = assemble_script(profile, outline, nodes)
        factuality = review_factuality(llm, recall, profile, outline, nodes, content)
        factuality_reviews.append(factuality)
        retry_count += 1

    narrative_reviews: list[dict[str, Any]] = []
    narrative = {"skipped": True, "reason": "factuality_failed", "issues": []}

    if factuality.get("passed"):
        narrative = review_narrative_coherence(llm, outline, nodes, content)
        narrative_reviews.append(narrative)

        retry_count = 0
        while not narrative.get("passed") and retry_count < options.narrative_retries:
            nodes = revise_nodes_for_narrative(llm, outline, nodes, narrative.get("issues", []))
            content = assemble_script(profile, outline, nodes)
            narrative = review_narrative_coherence(llm, outline, nodes, content)
            narrative_reviews.append(narrative)
            retry_count += 1

    if factuality.get("passed"):
        final_content = content
        draft_content = ""
        quality = review_quality(llm, recall, profile, outline, final_content, factuality, narrative)
        status = "ok" if narrative.get("passed") else "narrative_issues"
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
        "narrative": narrative,
        "narrativeReviews": narrative_reviews,
        "quality": quality,
    }


def generate_recall(llm: LLM, book_name: str) -> dict[str, Any]:
    return complete_json(
        llm,
        prompts.RECALL_SYSTEM,
        prompts.RECALL_USER.format(book_name=book_name),
        "book recall",
    )


def generate_profile(llm: LLM, options: GenerateOptions, recall: dict[str, Any]) -> dict[str, Any]:
    return complete_json(
        llm,
        prompts.PROFILE_SYSTEM,
        prompts.PROFILE_USER.format(
            book_name=options.book_name,
            duration_minutes=options.duration_minutes,
            mode=options.mode,
            user_note=options.user_note or "无",
            recall_json=json.dumps(recall, ensure_ascii=False, indent=2),
        ),
        "book profile",
    )


def generate_outline(
    llm: LLM,
    recall: dict[str, Any],
    profile: dict[str, Any],
) -> dict[str, Any]:
    return complete_json(
        llm,
        prompts.OUTLINE_SYSTEM,
        prompts.OUTLINE_USER.format(
            recall_json=json.dumps(recall, ensure_ascii=False, indent=2),
            profile_json=json.dumps(profile, ensure_ascii=False, indent=2),
        ),
        "narrative outline",
    )


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
        result = complete_json(
            llm,
            prompts.NODE_SYSTEM,
            prompts.NODE_USER.format(
                recall_json=json.dumps(recall, ensure_ascii=False, indent=2),
                profile_json=json.dumps(profile, ensure_ascii=False, indent=2),
                outline_json=json.dumps(outline, ensure_ascii=False, indent=2),
                segment_json=json.dumps(segment, ensure_ascii=False, indent=2),
                target_words=target_words,
            ),
            f"node {segment.get('node_id') or segment.get('title') or len(nodes) + 1}",
        )
        node = normalize_node(result, segment)
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
        "opening_bridge": raw_node.get("opening_bridge") or segment.get("entry_context") or "",
        "source_scenes": raw_node.get("source_scenes") or segment.get("source_scenes") or [],
        "required_facts": raw_node.get("required_facts") or segment.get("required_facts") or [],
        "causal_context": raw_node.get("causal_context") or segment.get("causal_context") or "",
        "emotional_context": raw_node.get("emotional_context") or segment.get("emotional_context") or "",
        "character_intro_notes": raw_node.get("character_intro_notes")
        or segment.get("new_characters_to_introduce")
        or [],
        "scene_moment": raw_node.get("scene_moment") or segment.get("scene_focus") or "",
        "narration": raw_node.get("narration") or "",
        "companion_insight": raw_node.get("companion_insight") or "",
        "transition_to_next": raw_node.get("transition_to_next") or segment.get("transition_to_next") or "",
        "uncertainty_notes": raw_node.get("uncertainty_notes") or segment.get("uncertainty_notes") or [],
    }


def assemble_script(
    profile: dict[str, Any],
    outline: dict[str, Any],
    nodes: list[dict[str, Any]],
) -> str:
    parts: list[str] = []
    opening = (outline.get("openingHook") or "").strip()
    if opening:
        parts.append(opening)

    for node in nodes:
        node_parts = node_to_script_parts(node)
        parts.extend(node_parts)

    closing = (outline.get("closingQuestion") or "").strip()
    if closing:
        parts.append(closing)

    return "\n\n".join(dedupe_adjacent_parts(part for part in parts if part))


def dedupe_adjacent_parts(parts: Any) -> list[str]:
    deduped: list[str] = []
    for part in parts:
        normalized = " ".join(str(part).split())
        if not normalized:
            continue
        if deduped and " ".join(deduped[-1].split()) == normalized:
            continue
        deduped.append(str(part))
    return deduped


def node_to_script_parts(node: dict[str, Any]) -> list[str]:
    parts: list[str] = []

    for key in ["opening_bridge", "scene_moment"]:
        value = (node.get(key) or "").strip()
        if value:
            parts.append(value)

    intro_notes = node.get("character_intro_notes") or []
    if isinstance(intro_notes, list):
        intro_text = " ".join(str(item).strip() for item in intro_notes if str(item).strip())
        if intro_text:
            parts.append(intro_text)
    elif str(intro_notes).strip():
        parts.append(str(intro_notes).strip())

    for key in ["narration", "companion_insight", "transition_to_next"]:
        value = (node.get(key) or "").strip()
        if value:
            parts.append(value)

    return parts


def review_factuality(
    llm: LLM,
    recall: dict[str, Any],
    profile: dict[str, Any],
    outline: dict[str, Any],
    nodes: list[dict[str, Any]],
    script: str,
) -> dict[str, Any]:
    result = complete_json(
        llm,
        prompts.FACTUALITY_REVIEW_SYSTEM,
        prompts.FACTUALITY_REVIEW_USER.format(
            recall_json=json.dumps(recall, ensure_ascii=False, indent=2),
            profile_json=json.dumps(profile, ensure_ascii=False, indent=2),
            outline_json=json.dumps(outline, ensure_ascii=False, indent=2),
            nodes_json=json.dumps(nodes, ensure_ascii=False, indent=2),
            script=script,
        ),
        "factuality review",
    )
    return normalize_review(result, default_passed=False)


def revise_nodes_for_factuality(
    llm: LLM,
    recall: dict[str, Any],
    outline: dict[str, Any],
    nodes: list[dict[str, Any]],
    issues: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    result = complete_json(
        llm,
        prompts.FACTUAL_REVISION_SYSTEM,
        prompts.FACTUAL_REVISION_USER.format(
            recall_json=json.dumps(recall, ensure_ascii=False, indent=2),
            outline_json=json.dumps(outline, ensure_ascii=False, indent=2),
            nodes_json=json.dumps(nodes, ensure_ascii=False, indent=2),
            issues_json=json.dumps(issues, ensure_ascii=False, indent=2),
        ),
        "factuality revision",
    )
    return normalize_revised_nodes(result, outline)


def review_narrative_coherence(
    llm: LLM,
    outline: dict[str, Any],
    nodes: list[dict[str, Any]],
    script: str,
) -> dict[str, Any]:
    result = complete_json(
        llm,
        prompts.NARRATIVE_REVIEW_SYSTEM,
        prompts.NARRATIVE_REVIEW_USER.format(
            outline_json=json.dumps(outline, ensure_ascii=False, indent=2),
            nodes_json=json.dumps(nodes, ensure_ascii=False, indent=2),
            script=script,
        ),
        "narrative coherence review",
    )
    return normalize_review(result, default_passed=False)


def revise_nodes_for_narrative(
    llm: LLM,
    outline: dict[str, Any],
    nodes: list[dict[str, Any]],
    issues: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    result = complete_json(
        llm,
        prompts.NARRATIVE_REVISION_SYSTEM,
        prompts.NARRATIVE_REVISION_USER.format(
            outline_json=json.dumps(outline, ensure_ascii=False, indent=2),
            nodes_json=json.dumps(nodes, ensure_ascii=False, indent=2),
            issues_json=json.dumps(issues, ensure_ascii=False, indent=2),
        ),
        "narrative revision",
    )
    return normalize_revised_nodes(result, outline)


def normalize_revised_nodes(result: Any, outline: dict[str, Any]) -> list[dict[str, Any]]:
    revised_nodes = result.get("nodes") if isinstance(result, dict) else result
    if not isinstance(revised_nodes, list):
        raise ValueError("Node revision must return a nodes array.")

    segment_by_id = {segment.get("node_id"): segment for segment in outline.get("segments", [])}
    normalized = []
    for node in revised_nodes:
        segment = segment_by_id.get(node.get("node_id"), {}) if isinstance(node, dict) else {}
        normalized.append(normalize_node(node, segment))
    return normalized


def normalize_review(result: Any, default_passed: bool) -> dict[str, Any]:
    if not isinstance(result, dict):
        raise ValueError("Review must return a JSON object.")
    result.setdefault("passed", default_passed)
    result.setdefault("issues", [])
    return result


def review_quality(
    llm: LLM,
    recall: dict[str, Any],
    profile: dict[str, Any],
    outline: dict[str, Any],
    script: str,
    factuality: dict[str, Any],
    narrative: dict[str, Any],
) -> dict[str, Any]:
    return complete_json(
        llm,
        prompts.REVIEW_SYSTEM,
        prompts.REVIEW_USER.format(
            recall_json=json.dumps(recall, ensure_ascii=False, indent=2),
            profile_json=json.dumps(profile, ensure_ascii=False, indent=2),
            outline_json=json.dumps(outline, ensure_ascii=False, indent=2),
            factuality_json=json.dumps(factuality, ensure_ascii=False, indent=2),
            narrative_json=json.dumps(narrative, ensure_ascii=False, indent=2),
            script=script,
        ),
        "quality review",
    )


def complete_json(llm: LLM, system: str, user: str, label: str) -> Any:
    raw = llm.complete(system, user)
    try:
        return parse_json(raw)
    except json.JSONDecodeError as first_error:
        repaired = llm.complete(
            "You repair invalid JSON. Return valid JSON only. Do not add Markdown or explanation.",
            (
                f"The following {label} output is intended to be JSON but is invalid.\n"
                "Repair syntax only. Preserve all data and field names as much as possible.\n\n"
                f"Invalid JSON text:\n{raw}"
            ),
        )
        try:
            return parse_json(repaired)
        except json.JSONDecodeError as second_error:
            raise ValueError(
                f"{label} returned invalid JSON after one repair attempt: {second_error}"
            ) from first_error


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
