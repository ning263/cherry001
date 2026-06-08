from __future__ import annotations

import argparse
from pathlib import Path

from .mock_llm import MockLLM
from .openai_client import OpenAIClient


FACT_PROBE_SYSTEM = """你现在不是讲书人，而是文学作品事实整理员。

你的任务是整理原著事实，不是生成讲书稿。

必须遵守：
- 不要文学化渲染。
- 不要补写原著没有明确出现的场景、动作、天气、对白。
- 不要把影视剧、电影、游戏、同人改编混入原著。
- 如果不确定，请明确标注“可能不确定”，不要编造。
- 请特别注意地点、人物是否在场、事件发生顺序是否准确。
- 请区分原著明确事实、合理概括、可能不确定的信息。
"""


FACT_PROBE_USER = """请基于金庸原著《{book_name}》，按照 characters、events、timeline 三个部分，尽可能详细地整理这本书的事实资料。

重要要求：

1. 不要写成讲书稿。
2. 不要文学化渲染。
3. 不要补写原著没有明确出现的场景、动作、天气、对白。
4. 如果你不确定某个细节，请标注“可能不确定”，不要编造。
5. 请以原著小说为准，不要混入电视剧、电影、游戏、同人改编情节。
6. 请特别注意地点、人物是否在场、事件发生顺序是否准确。
7. 请区分：
   - 原著明确事实
   - 合理概括
   - 可能不确定的信息

输出结构如下：

# Characters

请列出主要人物。每个人包含：

- name：
- identity：
- relationships：
- core motivation：
- key actions：
- key changes：
- related events：

# Events

请列出关键事件。每个事件包含：

- event_id：
- event_name：
- location：
- approximate_position_in_story：
- characters_present：
- what_happened：
- cause：
- consequence：
- factual_confidence：high / medium / low
- uncertainty_note：

要求事件尽量详细，尤其包括但不限于：

- 张翠山、殷素素、谢逊、冰火岛相关事件
- 张无忌出生与童年
- 返回中原
- 武当山张三丰百岁寿辰
- 张翠山、殷素素之死
- 张无忌身中玄冥神掌
- 蝴蝶谷相关事件
- 朱九真、武青婴、昆仑山相关事件
- 九阳真经
- 乾坤大挪移
- 光明顶
- 成为明教教主
- 赵敏相关关键事件
- 周芷若相关关键事件
- 灵蛇岛
- 屠狮大会
- 结局

# Timeline

请按照故事时间线，从前史到结局，整理完整时间线。

每个节点包含：

- order：
- phase：
- event：
- location：
- characters：
- why_it_matters：
- next_event_link：

最后请额外输出一个部分：

# Possible Risky Facts

列出你认为最容易被模型误写、影视剧混淆、或需要人工核对的事实点。

例如：

- 某事件发生地点是否容易混淆
- 某人物是否真的在场
- 某句对白是否原著明确出现
- 某段情节是否来自影视改编
"""


MOCK_FACT_RESULT = """# Characters

- name：张无忌
- identity：主角，张翠山与殷素素之子
- relationships：张三丰徒孙，谢逊义子
- core motivation：在江湖仇怨中寻找不继续杀戮的可能
- key actions：经历父母之死、身中寒毒、习得九阳神功、光明顶阻止六大派与明教互杀
- key changes：从无力旁观者变成有能力介入江湖冲突的人
- related events：武当山寿宴、玄冥神掌、昆仑山深谷、光明顶

# Events

- event_id：E001
- event_name：张翠山一家返回中原
- location：从冰火岛返回中原，后至武当山
- approximate_position_in_story：前期
- characters_present：张翠山、殷素素、张无忌
- what_happened：张翠山一家离开冰火岛返回中原，引发各派追问谢逊和屠龙刀下落。
- cause：谢逊与屠龙刀牵动江湖旧怨。
- consequence：张翠山、殷素素被卷入武林群雄逼问。
- factual_confidence：high
- uncertainty_note：mock 样例，只用于流程验证。

# Timeline

- order：1
- phase：返回中原
- event：张翠山一家回到中原
- location：中原 / 武当山相关情节
- characters：张翠山、殷素素、张无忌
- why_it_matters：引出父母之死与张无忌的创伤起点。
- next_event_link：武当山张三丰百岁寿辰相关逼问。

# Possible Risky Facts

- 六大派没有去冰火岛逼死张翠山、殷素素。
- 父母之死不能写成冰火岛雪地场景。
"""


def build_fact_probe_prompt(book_name: str) -> str:
    return FACT_PROBE_USER.format(book_name=book_name)


def main() -> None:
    parser = argparse.ArgumentParser(description="Probe a model's factual knowledge of a literary work.")
    parser.add_argument("--book", required=True, help="Book name.")
    parser.add_argument("--model", default=None, help="Optional model override.")
    parser.add_argument("--mock", action="store_true", help="Run without API calls.")
    parser.add_argument("--out", default="", help="Optional Markdown output path.")

    args = parser.parse_args()

    if args.mock:
        result = MOCK_FACT_RESULT
    else:
        llm = OpenAIClient()
        if args.model:
            llm.model = args.model
        result = llm.complete(FACT_PROBE_SYSTEM, build_fact_probe_prompt(args.book))

    if args.out:
        output_path = Path(args.out)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(result, encoding="utf-8")

    print(result)


if __name__ == "__main__":
    main()
