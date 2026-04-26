from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Iterable


@dataclass
class LLMResponse:
    raw_text: str
    input_tokens: int
    output_tokens: int
    model_id: str
    cost_usd: float | None
    latency_ms: int


class LLMProvider(ABC):
    provider_name: str

    @abstractmethod
    def generate(self, messages: list[dict[str, str]], model: str, max_tokens: int, **kwargs: Any) -> LLMResponse:
        raise NotImplementedError

    @abstractmethod
    def stream(self, messages: list[dict[str, str]], model: str, max_tokens: int, **kwargs: Any) -> Iterable[str]:
        raise NotImplementedError
