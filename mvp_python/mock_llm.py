from __future__ import annotations

import json


class MockLLM:
    def __init__(self) -> None:
        self.factuality_calls = 0
        self.narrative_calls = 0
        self.quality_calls = 0

    def complete(self, system: str, user: str) -> str:
        if "Book Recall 事实整理器" in system:
            return json.dumps(mock_recall(), ensure_ascii=False)

        if "作品画像生成器" in system:
            return json.dumps(mock_profile(), ensure_ascii=False)

        if "讲述骨架生成器" in system:
            return json.dumps(mock_outline(), ensure_ascii=False)

        if "Scene Plan 规划器" in system:
            return json.dumps(mock_scene_plan(user), ensure_ascii=False)

        if "节点正文生成器" in system:
            return json.dumps(mock_node(user), ensure_ascii=False)

        if "事实审查器" in system:
            self.factuality_calls += 1
            return json.dumps({"passed": True, "issues": []}, ensure_ascii=False)

        if "事实修订器" in system:
            return json.dumps({"nodes": [mock_node_for_id("N001"), mock_node_for_id("N002")]}, ensure_ascii=False)

        if "叙事连贯性审查器" in system:
            self.narrative_calls += 1
            return json.dumps({"passed": True, "issues": []}, ensure_ascii=False)

        if "叙事修订器" in system:
            return json.dumps({"nodes": [mock_node_for_id("N001"), mock_node_for_id("N002")]}, ensure_ascii=False)

        if "质量审查器" in system:
            self.quality_calls += 1
            if self.quality_calls == 1:
                return json.dumps(
                    {
                        "score": 72,
                        "isUsable": False,
                        "problems": ["节奏略重复，需要压缩首段并保持自然讲述。"],
                        "strengths": ["事实稳定"],
                        "revisionAdvice": ["删掉重复开场，减少解释感。"],
                        "checklist": {
                            "hasStoryness": True,
                            "hasScenes": True,
                            "hasCausalContinuity": True,
                            "hasEmotionalContinuity": True,
                            "avoidsPrematureAbstraction": True,
                            "hasNarrativeCoherence": True,
                            "hasCompanionInsight": True,
                            "avoidsFieldStitching": True,
                            "avoidsRepetition": False,
                            "hasCompleteThroughline": True,
                        },
                    },
                    ensure_ascii=False,
                )
            return json.dumps(
                {
                    "score": 86,
                    "isUsable": True,
                    "problems": [],
                    "strengths": ["自然讲述", "事实优先", "没有字段拼接"],
                    "revisionAdvice": [],
                    "checklist": {
                        "hasStoryness": True,
                        "hasScenes": True,
                        "hasCausalContinuity": True,
                        "hasEmotionalContinuity": True,
                        "avoidsPrematureAbstraction": True,
                        "hasNarrativeCoherence": True,
                        "hasCompanionInsight": True,
                        "avoidsFieldStitching": True,
                        "avoidsRepetition": True,
                        "hasCompleteThroughline": True,
                    },
                },
                ensure_ascii=False,
            )

        if "质量修订器" in system:
            return json.dumps({"nodes": [mock_node_for_id("N001"), mock_node_for_id("N002")]}, ensure_ascii=False)

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


def mock_scene_plan(user: str) -> dict:
    current_segment = user.split("当前 segment：")[-1]
    if "N002" in current_segment:
        return mock_scene_plan_for_id("N002")
    return mock_scene_plan_for_id("N001")


def mock_scene_plan_for_id(node_id: str) -> dict:
    plans = {
        "N001": {
            "node_id": "N001",
            "title": "武当山上的寿宴",
            "where_are_we": "武当山，张三丰百岁寿辰",
            "who_is_present": ["张翠山", "殷素素", "张无忌", "张三丰", "武林群雄"],
            "why_this_scene_happens": "张翠山一家返回中原，各派趁寿宴逼问谢逊下落。",
            "listener_knows_before": ["张翠山一家从冰火岛回到中原", "谢逊和屠龙刀牵动江湖"],
            "new_info_to_introduce": ["张三丰是张翠山的师父，也是张无忌的太师父。"],
            "conflict_or_pressure": "张翠山不能出卖义兄，也不愿把武当拖入风波。",
            "emotional_turn": "回家变成逼问，团聚变成诀别。",
            "insight_after_scene": "这让张无忌第一次看见，正义名义也可能逼死人。",
            "transition_goal": "父母之死没有结束伤害，寒毒继续留在他身上。",
            "uncertainty_notes": [],
        },
        "N002": {
            "node_id": "N002",
            "title": "寒毒留在身体里",
            "where_are_we": "武当山之后，张无忌被寒毒折磨的求医路上",
            "who_is_present": ["张无忌", "张三丰"],
            "why_this_scene_happens": "张无忌身中玄冥神掌，张三丰也不能彻底根治。",
            "listener_knows_before": ["张无忌已经失去父母", "江湖逼问围绕谢逊和屠龙刀"],
            "new_info_to_introduce": ["玄冥二老造成寒毒，是江湖斗争压到张无忌身上的后果。"],
            "conflict_or_pressure": "寒毒让创伤从记忆变成每天发作的身体现实。",
            "emotional_turn": "悲伤变成长期求生。",
            "insight_after_scene": "他后来不愿轻易杀人，和这段经历有关。",
            "transition_goal": "要活下去，他必须找到能压过寒毒的力量。",
            "uncertainty_notes": [],
        },
    }
    return plans[node_id]


def mock_node(user: str) -> dict:
    current_segment = user.split("当前 segment：")[-1]
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
            "character_intro_notes": ["张三丰是张翠山的师父，也是张无忌的太师父。"],
            "scene_moment": "武当山百岁寿辰上，群雄逼问谢逊下落。",
            "narration": "张翠山不能出卖义兄，殷素素也无法把秘密交出去。",
            "companion_insight": "这让张无忌第一次看见，正义名义也可能逼死人。",
            "transition_to_next": "伤害很快变成他身体里的寒毒。",
            "script_text": (
                "张无忌的故事，先从一次回家讲起。张翠山和殷素素带着儿子回到武当山，那里本该是张三丰百岁寿辰，"
                "也是久别师门后的团聚。可各派来人的心思不在祝寿，他们真正想问的是谢逊在哪里，屠龙刀在哪里。"
                "张三丰是张翠山的师父，也是张无忌的太师父，但就算有这样一位宗师在场，张翠山面对的压力也没有消失："
                "他说出谢逊，就是出卖义兄；不说，武当和妻儿都要被卷进这场逼问。最后，张翠山自尽，殷素素也随他而去。"
                "对张无忌来说，这不是一句“父母双亡”能概括的事。他第一次看见，江湖里那些自称正义的人，也能把人逼到死路。"
            ),
            "uncertainty_notes": [],
        },
        "N002": {
            "node_id": "N002",
            "title": "寒毒留在身体里",
            "opening_bridge": "父母之死之后，伤害没有停在武当山上。",
            "source_scenes": [],
            "required_facts": ["父母之死后张无忌身中玄冥神掌"],
            "causal_context": "父母之死和寒毒让张无忌长期承受上一代仇怨后果。",
            "emotional_context": "痛苦从事件变成持续命运。",
            "character_intro_notes": ["玄冥二老造成寒毒，是江湖斗争压到张无忌身上的后果。"],
            "scene_moment": "张三丰只能暂时护住张无忌性命，不能根除寒毒。",
            "narration": "寒毒让父母之死变成每天发作的现实。",
            "companion_insight": "他后来不愿轻易杀人，和这段经历有关。",
            "transition_to_next": "要活下去，他必须找到一种更强的力量。",
            "script_text": (
                "父母之死之后，江湖的后果继续追上这个孩子。张无忌身上还有玄冥神掌留下的寒毒，张三丰能护住他的性命，"
                "却不能把寒毒彻底拔掉。这里要先知道，玄冥二老不是张无忌人生里的路人，他们造成的寒毒，等于把大人之间的争夺"
                "压进了一个孩子的身体里。别人争谢逊，争屠龙刀，争正邪名分，最后每天承受痛的人却是张无忌。"
                "所以寒毒不是简单的受伤设定，它让武当山那天的创伤一直延续下去。也正因为太早知道胜负会变成别人身上的痛，"
                "张无忌后来才很难把杀人当成痛快的答案。要活下去，他必须找到一种比寒毒更强的力量。"
            ),
            "uncertainty_notes": [],
        },
    }
    return nodes[node_id]
