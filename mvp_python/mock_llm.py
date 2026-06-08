from __future__ import annotations

import json


class MockLLM:
    def __init__(self) -> None:
        self.factuality_calls = 0

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
            if self.factuality_calls == 1:
                return json.dumps(
                    {
                        "passed": False,
                        "issues": [
                            {
                                "type": "invented_scene_detail",
                                "severity": "high",
                                "text": "节点 N001 加入了 recall 不支持的冰火岛逼问画面。",
                                "node_id": "N001",
                                "suggested_fix": "删除冰火岛逼问，改回武当山百岁寿辰群雄逼问。",
                            }
                        ],
                    },
                    ensure_ascii=False,
                )
            return json.dumps({"passed": True, "issues": []}, ensure_ascii=False)

        if "事实修订器" in system:
            return json.dumps(
                {"nodes": [mock_node_for_id("N001"), mock_node_for_id("N002"), mock_node_for_id("N003")]},
                ensure_ascii=False,
            )

        if "质量审查器" in system:
            return json.dumps(
                {
                    "score": 78,
                    "isUsable": True,
                    "problems": ["样例节点较少，感情线和离开权力中心还需要补足。"],
                    "strengths": ["先过事实审查", "主线明确", "关键场景有因果功能"],
                    "revisionAdvice": ["补充赵敏/周芷若相关节点", "增加结尾开放问题前的回收段"],
                    "checklist": {
                        "hasStoryness": True,
                        "hasScenes": True,
                        "hasCausalContinuity": True,
                        "hasEmotionalContinuity": True,
                        "avoidsPrematureAbstraction": True,
                        "hasCompleteThroughline": False,
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
                "key_actions": ["身中玄冥神掌", "习得九阳神功", "光明顶阻止六大派与明教互杀"],
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
            {
                "event_id": "E003",
                "event_name": "光明顶阻止围攻",
                "location": "光明顶",
                "approximate_position_in_story": "中期",
                "characters_present": ["张无忌", "明教众人", "六大派"],
                "what_happened": "张无忌在光明顶出手化解六大派围攻明教的危机。",
                "cause": "六大派与明教积怨，被成昆等因素推动冲突。",
                "consequence": "张无忌被推举为明教教主。",
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
            {
                "order": 3,
                "phase": "江湖介入",
                "event": "张无忌在光明顶阻止六大派围攻明教",
                "location": "光明顶",
                "characters": ["张无忌", "明教", "六大派"],
                "why_it_matters_factually": "张无忌从旁观者变成介入者。",
                "next_event_link": "成为明教教主",
            },
        ],
        "causal_links": [
            {
                "from_event": "E001",
                "to_event": "E002",
                "causal_explanation": "返回中原使谢逊下落成为群雄逼问焦点。",
                "confidence": "high",
            },
            {
                "from_event": "E002",
                "to_event": "E003",
                "causal_explanation": "父母之死影响张无忌后来对正邪和仇杀的判断。",
                "confidence": "medium",
            },
        ],
        "important_scenes": [
            {
                "scene_id": "S001",
                "scene_name": "武当山百岁寿辰逼问",
                "location": "武当山",
                "characters_present": ["张翠山", "殷素素", "张无忌", "张三丰", "武林群雄"],
                "source_events": ["E002"],
                "factual_summary": "群雄逼问谢逊下落，张翠山、殷素素相继自尽。",
                "do_not_invent": ["不要写成六大派去冰火岛逼死父母", "不要写冰火岛雪地血染场景"],
            },
            {
                "scene_id": "S002",
                "scene_name": "光明顶",
                "location": "光明顶",
                "characters_present": ["张无忌", "明教众人", "六大派"],
                "source_events": ["E003"],
                "factual_summary": "张无忌出手化解六大派围攻明教。",
                "do_not_invent": ["不要把它只写成炫技大战"],
            },
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
        "coreThroughline": "张无忌从武当山上无力旁观父母之死，到光明顶主动阻止互杀。",
        "characters": [
            {
                "name": "张无忌",
                "role": "主角",
                "desireOrWound": "太早看见正义话语也会把人逼到死路。",
                "based_on_recall_facts": ["E002", "E003"],
            }
        ],
        "keyScenes": [
            {
                "name": "武当山百岁寿辰逼问",
                "source_scene_ids": ["S001"],
                "source_event_ids": ["E002"],
                "whyItMatters": "这是张无忌创伤起点。",
                "emotionalPressure": "一个孩子看见父母被江湖逼问逼到绝路。",
            },
            {
                "name": "光明顶",
                "source_scene_ids": ["S002"],
                "source_event_ids": ["E003"],
                "whyItMatters": "张无忌第一次有能力阻止同类冲突。",
                "emotionalPressure": "双方都有理由继续杀下去。",
            },
        ],
        "uncertainty_notes": [],
    }


def mock_outline() -> dict:
    return {
        "openingHook": "这本书不能先讲成升级爽文，因为张无忌最重要的不是赢，而是阻止仇恨继续赢。",
        "segments": [
            {
                "node_id": "N001",
                "title": "武当山上的寿宴",
                "source_scenes": ["S001"],
                "required_facts": ["张翠山一家从冰火岛返回中原", "父母之死发生在武当山相关场合"],
                "causal_context": "返回中原使谢逊下落成为群雄逼问焦点。",
                "emotional_context": "张无忌第一次看见正义话语也会逼死人。",
                "narration_goal": "让用户进入张无忌的创伤起点。",
                "uncertainty_notes": [],
            },
            {
                "node_id": "N002",
                "title": "寒毒与长大",
                "source_scenes": [],
                "required_facts": ["父母之死后张无忌身中玄冥神掌"],
                "causal_context": "父母之死和寒毒让张无忌长期承受上一代仇怨后果。",
                "emotional_context": "痛苦从事件变成持续命运。",
                "narration_goal": "解释寒毒不是简单升级前置。",
                "uncertainty_notes": [],
            },
            {
                "node_id": "N003",
                "title": "光明顶",
                "source_scenes": ["S002"],
                "required_facts": ["张无忌在光明顶化解六大派围攻明教"],
                "causal_context": "张无忌从被动旁观者变成主动介入者。",
                "emotional_context": "他不是为了赢，而是为了让冲突停下。",
                "narration_goal": "把光明顶从爽点改写为阻止悲剧重演的场景。",
                "uncertainty_notes": [],
            },
        ],
        "closingQuestion": "张无忌到底是优柔寡断，还是始终不愿意把人简单处理掉？",
    }


def mock_node(user: str) -> dict:
    current_segment = user.split("当前节点：")[-1]
    if "N002" in current_segment:
        return mock_node_for_id("N002")
    if "N003" in current_segment:
        return mock_node_for_id("N003")
    return mock_node_for_id("N001")


def mock_node_for_id(node_id: str) -> dict:
    nodes = {
        "N001": {
            "node_id": "N001",
            "title": "武当山上的寿宴",
            "source_scenes": ["S001"],
            "required_facts": ["父母之死发生在武当山相关场合"],
            "causal_context": "返回中原使谢逊下落成为群雄逼问焦点。",
            "emotional_context": "张无忌第一次看见正义话语也会逼死人。",
            "narration": "故事真正压住人的地方，不在冰火岛，而在武当山。张翠山和殷素素带着张无忌回到中原，本来是回到师门，也是回到人的世界。可等着他们的，不只是张三丰百岁寿辰的喜气，还有各派对谢逊下落和屠龙刀的逼问。张无忌还小，他未必听得懂每一句江湖话，却能看懂父亲越来越沉的脸色，也能看懂母亲知道退路正在消失。这一场留下的不是父母双亡四个字，而是一个更早的发现：人可以满口公义，同时把别人逼到死路。",
            "uncertainty_notes": [],
        },
        "N002": {
            "node_id": "N002",
            "title": "寒毒与长大",
            "source_scenes": [],
            "required_facts": ["父母之死后张无忌身中玄冥神掌"],
            "causal_context": "父母之死和寒毒让张无忌长期承受上一代仇怨后果。",
            "emotional_context": "痛苦从事件变成持续命运。",
            "narration": "后来，寒毒留在张无忌身体里。这不是一个普通的受伤设定。它像是上一代江湖恩怨真正落到他身上的形状。别人争谢逊，争屠龙刀，争正邪名分，最后每天被寒气折磨的，是一个还没来得及长大的孩子。所以张无忌后来的善良，不是没见过坏人。恰恰相反，他太早知道一件事：很多大人的胜负，最后会变成小孩子身上的痛。",
            "uncertainty_notes": [],
        },
        "N003": {
            "node_id": "N003",
            "title": "光明顶",
            "source_scenes": ["S002"],
            "required_facts": ["张无忌在光明顶化解六大派围攻明教"],
            "causal_context": "张无忌从被动旁观者变成主动介入者。",
            "emotional_context": "他不是为了赢，而是为了让冲突停下。",
            "narration": "到光明顶时，张无忌又一次站在两群互相仇恨的人中间。六大派说自己是除魔卫道，明教这边也背着旧账和恐惧。如果只讲他大战六大派，这场戏就变成了爽点。但真正重要的是：小时候他只能看着父母被逼到绝路，这一次他终于有力量让所有人先停一下。他不是在那里证明自己最强。他是在阻止同一种悲剧，用更大的规模重新发生。",
            "uncertainty_notes": [],
        },
    }
    return nodes[node_id]
