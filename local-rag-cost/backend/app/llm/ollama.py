import time
import httpx
from .base import LLMProvider, LLMResponse
from ..core.config import settings


class OllamaProvider(LLMProvider):
    provider_name = "ollama"

    def generate(self, messages: list[dict[str, str]], model: str, max_tokens: int, **kwargs) -> LLMResponse:
        started = time.perf_counter()
        prompt = "\n".join(f"{m['role']}: {m['content']}" for m in messages)
        with httpx.Client(timeout=120) as client:
            resp = client.post(
                f"{settings.ollama_base_url}/api/generate",
                json={"model": model, "prompt": prompt, "stream": False, "options": {"num_predict": max_tokens}},
            )
            resp.raise_for_status()
            data = resp.json()

        return LLMResponse(
            raw_text=data.get("response", ""),
            input_tokens=int(data.get("prompt_eval_count", 0)),
            output_tokens=int(data.get("eval_count", 0)),
            model_id=model,
            cost_usd=0.0,
            latency_ms=int((time.perf_counter() - started) * 1000),
        )

    def stream(self, messages, model, max_tokens, **kwargs):
        raise NotImplementedError("Streaming not implemented in phase 1")
