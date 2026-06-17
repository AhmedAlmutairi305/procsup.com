from .base import LLMProvider


class StubProvider(LLMProvider):
    provider_name = "stub"

    def generate(self, messages, model, max_tokens, **kwargs):
        raise NotImplementedError("Provider implementation deferred to phase 2")

    def stream(self, messages, model, max_tokens, **kwargs):
        raise NotImplementedError("Provider implementation deferred to phase 2")
