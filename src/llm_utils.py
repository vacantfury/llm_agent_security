"""Minimal placeholder LLM layer for the decoupled, text-only encoder package.

Why this exists: the deterministic text encoders (cipher / homoglyph / code / and the
other rule-based transforms) reference `LLMModel` only as an unused type hint, so this
stub lets the whole package import and run with no LLM dependency and no spend.

The LLM-BASED encoders (set-theory / formal-logic / classical-Chinese / quantum /
semantic-camo / paraphrase) genuinely call a model to encode. They are DEFERRED and
detached from the registry until a real client is wired — the intended path is to reuse
an established client (AgentDojo's LLM classes, or the Anthropic/OpenAI SDK) rather than
re-port the sibling's `llm_utils`. Instantiating the service stubs below raises, so a
deferred encoder fails loudly at call time instead of silently no-op'ing.

Replace this module with the real LLM client at S7 (see text_docs/agent_injection/design.md).
"""

# Unused type-hint alias for the deterministic encoders' constructors.
LLMModel = object

_DEFERRED = (
    "LLM-based encoders (set-theory / formal-logic / classical-Chinese / …) are deferred. "
    "Wire a real LLM client (reuse AgentDojo's LLM classes or an SDK) to enable them — "
    "see src/prompt_transformations/ and text_docs/agent_injection/design.md."
)


class BaseLLMService:  # pragma: no cover - placeholder
    def __init__(self, *args, **kwargs):
        raise NotImplementedError(_DEFERRED)


class LLMServiceFactory:  # pragma: no cover - placeholder
    @staticmethod
    def create(*args, **kwargs):
        raise NotImplementedError(_DEFERRED)
