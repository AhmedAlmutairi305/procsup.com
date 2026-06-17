import time
import httpx
from .base import LLMProvider, LLMResponse
from ..core.config import settings


class AnthropicProvider(LLMProvider):
    provider_name = "anthropic"

    def generate(self, messages: list[dict[str, str]], model: str, max_tokens: int, **kwargs) -> LLMResponse:
        if not settings.anthropic_api_key:
            raise RuntimeError("ANTHROPIC_API_KEY is not set")

        started = time.perf_counter()
        body = {
            "model": model,
            "max_tokens": max_tokens,
            "messages": messages,
        }
        with httpx.Client(timeout=60) as client:
            resp = client.post(
                "https://api.anthropic.com/v1/messages",
                json=body,
                headers={
                    "x-api-key": settings.anthropic_api_key,
                    "anthropic-version": "2023-06-01",
                    "content-type": "application/json",
                },
            )
            resp.raise_for_status()
            data = resp.json()

        text = "".join(part.get("text", "") for part in data.get("content", []))
        usage = data.get("usage", {})
        return LLMResponse(
            raw_text=text,
            input_tokens=int(usage.get("input_tokens", 0)),
            output_tokens=int(usage.get("output_tokens", 0)),
            model_id=data.get("model", model),
            cost_usd=None,
            latency_ms=int((time.perf_counter() - started) * 1000),
        )

    def stream(self, messages, model, max_tokens, **kwargs):
        raise NotImplementedError("Streaming not implemented in phase 1")
