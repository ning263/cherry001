from __future__ import annotations

import json


class MockLLM:
    def __init__(self) -> None:
        self.factuality_calls = 0
        self.narrative_calls = 0

    def complete(self, system: str, user: str) -> str:
        if "Book Recall 事实整理器" in system:
            return json.dumps(mock_recall(), ensure_ascii=False)

        if "作品画像生成器" in system:
            return json.dumps(mock_profile(), ensure_ascii=False)

        if "讲述骨架生成器" in system:
            return json.dumps(mock_outline(), ensure_ascii=False)

        if "节点正文生成器" in system:
            return json.dumps(mock_node(user), ensure_ascii=False)

        if "事实审查器" in system:
            self.factuality_calls += 1
            return json.dumps({"passed": True, "issues": []}, ensure_ascii=False)

        if "事实修订器" in system:
            return json.dumps({"nodes": [mock_node_for_id("N001"), mock_node_for_id("N002")]}, ensure_ascii=False)

        if "叙事连贯性审查器" in system:
            self.narrative_calls += 1
            if self.narrative_calls == 1:
                return json.dumps(
                    {
                        "passed": False,
                        "issues": [
                            {
                                "type": "missing_transition",
                                "severity": "medium",
                                "text": "节点 N002 进入寒毒时缺少从武当创伤到身体后果的过渡。",
                                "node_id": "N002",
                                "suggested_fix": "补充 opening_bridge，说明父母之死后寒毒成为持续后果。",
                            }
                        ],
                    },
                    ensure_ascii=False,
                )
            return json.dumps({"passed": True, "issues": []}, ensure_ascii=False)

        if "叙事修订器" in system:
            return json.dumps({"nodes": [mock_node_for_id("N001"), mock_node_for_id("N002")]}, ensure_ascii=False)

        if "质量审查器" in system:
            return json.dumps(
                {
                    "score": 84,
                    "isUsable": True,
                    "problems": [],
                    "strengths": ["事实优先", "过渡清晰", "有场景片段", "讲述人点评克制"],
                    "revisionAdvice": [],
                    "checklist": {
                        "hasStoryness": True,
                        "hasScenes": True,
                        "hasCausalContinuity": True,
                        "hasEmotionalContinuity": True,
                        "avoidsPrematureAbstraction": True,
                        "hasNarrativeCoherence": True,
                        "hasCompanionInsight": True,
                        "hasCompleteThroughline": True,
                    },
                },
                ensure_ascii=False,
            )

        return "{}"


def mock_recall() -> dict:
    return {
        "title": "倚天屠龙记",
        "characters": [
            {
                "name": "张无忌",
                "identity": "张翠山与殷素素之子，谢逊义子，后为明教教主",
                "relationships": ["父亲张翠山", "母亲殷素素", "义父谢逊", "太师父张三丰"],
                "core_motivation_facts": ["幼年经历父母之死", "多次试图阻止江湖仇杀扩大"],
                "key_actions": ["身中玄冥神掌", "习得九阳神功"],
                "key_changes": ["从被动承受江湖伤害的人，变成有能力介入冲突的人"],
                "uncertainty_notes": [],
            }
        ],
        "events": [
            {
                "event_id": "E001",
                "event_name": "张翠山一家返回中原",
                "location": "从冰火岛返回中原，后至武当山",
                "approximate_position_in_story": "前期",
                "characters_present": ["张翠山", "殷素素", "张无忌"],
                "what_happened": "张翠山、殷素素带张无忌离开冰火岛返回中原。",
                "cause": "张翠山思念师门，也希望张无忌回到中原。",
                "consequence": "谢逊和屠龙刀下落成为各派逼问焦点。",
                "factual_confidence": "high",
                "uncertainty_notes": [],
            },
            {
                "event_id": "E002",
                "event_name": "武当山百岁寿辰逼问",
                "location": "武当山",
                "approximate_position_in_story": "前期",
                "characters_present": ["张翠山", "殷素素", "张无忌", "张三丰", "武林群雄"],
                "what_happened": "张翠山、殷素素在张三丰百岁寿辰相关场合被逼问谢逊下落，最终相继自尽。",
                "cause": "各派追查谢逊和屠龙刀下落。",
                "consequence": "张无忌成为孤儿，随后身中玄冥神掌。",
                "factual_confidence": "high",
                "uncertainty_notes": [],
            },
        ],
        "timeline": [
            {
                "order": 1,
                "phase": "返回中原",
                "event": "张翠山一家离开冰火岛回中原",
                "location": "冰火岛至中原",
                "characters": ["张翠山", "殷素素", "张无忌"],
                "why_it_matters_factually": "引出武当山逼问。",
                "next_event_link": "武当山百岁寿辰逼问",
            },
            {
                "order": 2,
                "phase": "创伤起点",
                "event": "张翠山、殷素素在武当山相关场合自尽",
                "location": "武当山",
                "characters": ["张翠山", "殷素素", "张无忌"],
                "why_it_matters_factually": "张无忌父母之死。",
                "next_event_link": "张无忌身中玄冥神掌",
            },
        ],
        "causal_links": [
            {
                "from_event": "E001",
                "to_event": "E002",
                "causal_explanation": "返回中原使谢逊下落成为群雄逼问焦点。",
                "confidence": "high",
            }
        ],
        "important_scenes": [
            {
                "scene_id": "S001",
                "scene_name": "武当山百岁寿辰逼问",
                "location": "武当山",
                "characters_present": ["张翠山", "殷素素", "张无忌", "张三丰", "武林群雄"],
                "source_events": ["E002"],
                "factual_summary": "群雄逼问谢逊下落，张翠山、殷素素相继自尽。",
                "do_not_invent": ["不要写成六大派去冰火岛逼死父母"],
            }
        ],
        "risky_facts": [
            {
                "fact": "父母之死地点",
                "risk": "容易误写成冰火岛",
                "correct_version": "张翠山、殷素素之死发生在武当山相关场合。",
            }
        ],
    }


def mock_profile() -> dict:
    return {
        "title": "倚天屠龙记",
        "author": "金庸",
        "genre": "武侠小说",
        "shallowMisread": "一个少年学会神功、成为教主、卷入爱情选择的故事。",
        "archetype": "一个被仇恨推入江湖中心的人，后来尝试阻止仇恨继续扩大。",
        "emotionalPromise": "拥有力量以后，能不能不把力量变成清算。",
        "coreThroughline": "张无忌从武当山上无力旁观父母之死，到后来主动阻止互杀。",
        "characters": [
            {
                "name": "张无忌",
                "role": "主角",
                "desireOrWound": "太早看见正义话语也会把人逼到死路。",
                "based_on_recall_facts": ["E002"],
            }
        ],
        "keyScenes": [
            {
                "name": "武当山百岁寿辰逼问",
                "source_scene_ids": ["S001"],
                "source_event_ids": ["E002"],
                "whyItMatters": "这是张无忌创伤起点。",
                "emotionalPressure": "一个孩子看见父母被江湖逼问逼到绝路。",
            }
        ],
        "uncertainty_notes": [],
    }


def mock_outline() -> dict:
    return {
        "openingHook": "张无忌的故事，先从一次回家讲起。",
        "segments": [
            {
                "node_id": "N001",
                "title": "武当山上的寿宴",
                "entry_context": "张翠山一家离开冰火岛，终于回到中原。",
                "listener_knows": ["张翠山一家曾长期在冰火岛生活", "谢逊和屠龙刀牵动江湖"],
                "new_characters_to_introduce": ["张三丰：张翠山的师父，武当派祖师"],
                "scene_focus": "武当山上，群雄借寿宴逼问谢逊下落。",
                "source_scenes": ["S001"],
                "required_facts": ["父母之死发生在武当山相关场合"],
                "causal_context": "返回中原使谢逊下落成为群雄逼问焦点。",
                "emotional_context": "张无忌第一次看见正义话语也会逼死人。",
                "narration_goal": "让用户进入张无忌的创伤起点。",
                "transition_to_next": "父母之死之后，伤害没有停在那一天。",
                "uncertainty_notes": [],
            },
            {
                "node_id": "N002",
                "title": "寒毒留在身体里",
                "entry_context": "父母之死之后，江湖的伤害继续落到张无忌身上。",
                "listener_knows": ["张无忌已经成为孤儿", "各派逼问与谢逊下落有关"],
                "new_characters_to_introduce": ["玄冥二老：汝阳王府高手，玄冥神掌造成寒毒"],
                "scene_focus": "张无忌身中玄冥神掌，张三丰也难以根治。",
                "source_scenes": [],
                "required_facts": ["父母之死后张无忌身中玄冥神掌"],
                "causal_context": "父母之死和寒毒让张无忌长期承受上一代仇怨后果。",
                "emotional_context": "痛苦从事件变成持续命运。",
                "narration_goal": "解释寒毒不是简单升级前置。",
                "transition_to_next": "当身体里的寒意无法消除，他只能继续寻找活下去的办法。",
                "uncertainty_notes": [],
            },
        ],
        "closingQuestion": "如果一个人太早看见仇恨的代价，他后来还会不会相信简单的胜负？",
    }


def mock_node(user: str) -> dict:
    current_segment = user.split("当前节点：")[-1]
    if "N002" in current_segment:
        return mock_node_for_id("N002")
    return mock_node_for_id("N001")


def mock_node_for_id(node_id: str) -> dict:
    nodes = {
        "N001": {
            "node_id": "N001",
            "title": "武当山上的寿宴",
            "opening_bridge": "张无忌的故事，先从一次回家讲起。",
            "source_scenes": ["S001"],
            "required_facts": ["父母之死发生在武当山相关场合"],
            "causal_context": "返回中原使谢逊下落成为群雄逼问焦点。",
            "emotional_context": "张无忌第一次看见正义话语也会逼死人。",
            "character_intro_notes": ["张三丰是张翠山的师父，也是武当派最重要的精神支柱。"],
            "scene_moment": "地点在武当山。张翠山和殷素素带着张无忌回来，本应是师门重逢，却撞上群雄逼问谢逊下落。",
            "narration": "张无忌还小，他未必听得懂每一句江湖话，但他能看懂父亲的退路正在变窄。张翠山不能出卖义兄，也不愿把风波继续压到武当身上，最终自尽。殷素素随后也选择同死。",
            "companion_insight": "这一场不是简单的父母双亡。它让张无忌第一次看见，正义的名义也可能把人逼到死路。",
            "transition_to_next": "而这场伤害没有停在武当山上，它很快变成了张无忌身体里的寒毒。",
            "uncertainty_notes": [],
        },
        "N002": {
            "node_id": "N002",
            "title": "寒毒留在身体里",
            "opening_bridge": "父母之死之后，江湖的后果继续追上这个孩子。",
            "source_scenes": [],
            "required_facts": ["父母之死后张无忌身中玄冥神掌"],
            "causal_context": "父母之死和寒毒让张无忌长期承受上一代仇怨后果。",
            "emotional_context": "痛苦从事件变成持续命运。",
            "character_intro_notes": ["玄冥二老是造成寒毒的高手，他们把江湖斗争直接压到张无忌身上。"],
            "scene_moment": "张无忌身中玄冥神掌后，连张三丰也只能暂时护住他的性命，不能彻底根除寒毒。",
            "narration": "寒毒不是普通受伤。它让父母之死不只是回忆，而是每天都在身体里发作的现实。别人争谢逊，争屠龙刀，争正邪名分，最后承受后果的，是一个孩子。",
            "companion_insight": "这就是张无忌后来不愿轻易杀人的底色：他太早知道，大人的胜负会变成孩子身上的痛。",
            "transition_to_next": "要活下去，他必须找到一种比寒毒更强的力量。",
            "uncertainty_notes": [],
        },
    }
    return nodes[node_id]
