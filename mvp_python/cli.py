from __future__ import annotations

import argparse
import json
from pathlib import Path

from .mock_llm import MockLLM
from .openai_client import OpenAIClient
from .orchestrator import GenerateOptions, generate_script, save_result


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate an AI Reading Companion MVP script.")
    parser.add_argument("--book", required=True, help="Book name, for example: 倚天屠龙记")
    parser.add_argument("--duration", type=int, default=12, help="Target duration in minutes.")
    parser.add_argument(
        "--mode",
        default="first_encounter",
        choices=["first_encounter", "deep_reading", "discussion_starter"],
        help="Narration mode.",
    )
    parser.add_argument("--note", default="", help="Optional user note.")
    parser.add_argument("--model", default=None, help="Model name. Overrides OPENAI_MODEL or DEEPSEEK_MODEL.")
    parser.add_argument("--mock", action="store_true", help="Run without API calls.")
    parser.add_argument("--out", default="", help="Optional JSON output path.")
    parser.add_argument("--factuality-retries", type=int, default=2, help="Maximum factuality revision retries.")

    args = parser.parse_args()

    if args.mock:
        llm = MockLLM()
    else:
        llm = OpenAIClient()
        if args.model:
            llm.model = args.model

    result = generate_script(
        llm,
        GenerateOptions(
            book_name=args.book,
            duration_minutes=args.duration,
            mode=args.mode,
            user_note=args.note,
            factuality_retries=args.factuality_retries,
        ),
    )

    if args.out:
        save_result(result, Path(args.out))

    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
