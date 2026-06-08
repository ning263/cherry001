from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path


class LLMError(RuntimeError):
    pass


@dataclass
class OpenAIClient:
    model: str = os.environ.get("OPENAI_MODEL", "gpt-4.1")
    api_key: str | None = os.environ.get("OPENAI_API_KEY") or None
    base_url: str = os.environ.get("OPENAI_BASE_URL", "https://api.openai.com/v1")
    provider: str = os.environ.get("LLM_PROVIDER", "openai")

    def __post_init__(self) -> None:
        env_values = load_dotenv_local()
        self.provider = (
            os.environ.get("LLM_PROVIDER") or env_values.get("LLM_PROVIDER") or self.provider
        ).strip().lower()

        if self.provider == "deepseek":
            self.api_key = (
                os.environ.get("DEEPSEEK_API_KEY")
                or env_values.get("DEEPSEEK_API_KEY")
                or self.api_key
                or env_values.get("OPENAI_API_KEY")
            )
            self.model = (
                os.environ.get("DEEPSEEK_MODEL")
                or env_values.get("DEEPSEEK_MODEL")
                or os.environ.get("OPENAI_MODEL")
                or env_values.get("OPENAI_MODEL")
                or "deepseek-v4-flash"
            )
            self.base_url = (
                os.environ.get("DEEPSEEK_BASE_URL")
                or env_values.get("DEEPSEEK_BASE_URL")
                or os.environ.get("OPENAI_BASE_URL")
                or env_values.get("OPENAI_BASE_URL")
                or "https://api.deepseek.com"
            )
            return

        self.api_key = self.api_key or env_values.get("OPENAI_API_KEY")
        self.model = os.environ.get("OPENAI_MODEL") or env_values.get("OPENAI_MODEL") or self.model
        self.base_url = os.environ.get("OPENAI_BASE_URL") or env_values.get("OPENAI_BASE_URL") or self.base_url

    def complete(self, system: str, user: str) -> str:
        if not self.api_key:
            expected_key = "DEEPSEEK_API_KEY" if self.provider == "deepseek" else "OPENAI_API_KEY"
            raise LLMError(f"{expected_key} is not set. Use --mock for an offline dry run.")

        if self.provider == "deepseek":
            return self._complete_chat_completions(system, user, provider_name="DeepSeek")

        return self._complete_openai_responses(system, user)

    def _complete_openai_responses(self, system: str, user: str) -> str:
        payload = {
            "model": self.model,
            "input": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
        }

        request = urllib.request.Request(
            f"{self.base_url.rstrip('/')}/responses",
            data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )

        try:
            with urllib.request.urlopen(request, timeout=180) as response:
                data = json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")
            raise LLMError(f"OpenAI API error {exc.code}: {detail}") from exc
        except urllib.error.URLError as exc:
            raise LLMError(f"OpenAI API request failed: {exc}") from exc

        return extract_response_text(data)

    def _complete_chat_completions(self, system: str, user: str, provider_name: str) -> str:
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
        }

        request = urllib.request.Request(
            f"{self.base_url.rstrip('/')}/chat/completions",
            data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )

        try:
            with urllib.request.urlopen(request, timeout=180) as response:
                data = json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")
            raise LLMError(f"{provider_name} API error {exc.code}: {detail}") from exc
        except urllib.error.URLError as exc:
            raise LLMError(f"{provider_name} API request failed: {exc}") from exc

        return extract_chat_completion_text(data, provider_name)


def extract_response_text(data: dict) -> str:
    if isinstance(data.get("output_text"), str):
        return data["output_text"]

    chunks: list[str] = []
    for item in data.get("output", []):
        for content in item.get("content", []):
            text = content.get("text")
            if isinstance(text, str):
                chunks.append(text)

    if chunks:
        return "\n".join(chunks).strip()

    raise LLMError("OpenAI response did not contain output text.")


def extract_chat_completion_text(data: dict, provider_name: str) -> str:
    choices = data.get("choices")
    if not isinstance(choices, list) or not choices:
        raise LLMError(f"{provider_name} response did not contain choices.")

    message = choices[0].get("message", {})
    content = message.get("content")
    if isinstance(content, str) and content.strip():
        return content.strip()

    raise LLMError(f"{provider_name} response did not contain message content.")


def load_dotenv_local(path: Path | None = None) -> dict[str, str]:
    env_path = path or Path.cwd() / ".env.local"
    if not env_path.exists():
        return {}

    values: dict[str, str] = {}
    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue

        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key:
            values[key] = value

    return values
