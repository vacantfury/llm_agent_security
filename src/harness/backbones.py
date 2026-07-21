"""Build an AgentDojo backbone (a `BasePipelineElement`) from a matrix.yaml backbone spec.

The scaffold axis (design.md §3) picks the *class*, the spec picks the *model*:

  * ``native``   -> the provider's structured tool API: ``OpenAILLM`` / ``AnthropicLLM`` /
    ``GoogleLLM`` / ``CohereLLM``.
  * ``prompted`` -> tool schemas serialized into the prompt: ``PromptingLLM`` (OpenAI-compatible
    client) — also the open-weight path (a vLLM OpenAI-compatible endpoint). AgentDojo only ships
    the prompted scaffold over an OpenAI-style client, so ``prompted`` is supported for the
    ``openai`` and ``vllm`` providers, not ``anthropic``/``google`` (the runner skips those combos).
  * ``react``    -> a built planner->executor element — NOT yet built (design §3.3); listed here so
    the axis name is stable, but `build_backbone` raises ``NotImplementedError`` for it.

We hand-build the LLM object (rather than going through AgentDojo's ``ModelsEnum``) so the
capability sweep can use current-gen snapshots the shipped enum predates; `src/defenses/factory.py`
accepts a pre-built ``llm`` object directly.

NO-SPEND: constructing a provider client is offline (the SDKs only hit the network on a request),
so `build_backbone` — and therefore the runner's ``--dry-run`` pipeline-assembly check — never
spends. A placeholder key is used when the real env var is absent, purely so construction succeeds;
an actual ``.query(...)`` (a real run) still needs a real key.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Any

from agentdojo.agent_pipeline.base_pipeline_element import BasePipelineElement

SCAFFOLDS = ("native", "prompted", "react")  # "react" = design §3.3, not yet built
_PROMPTED_OK = frozenset({"openai", "vllm", "local"})  # providers with an OpenAI-style client
_PLACEHOLDER_KEY = "PLACEHOLDER-no-spend-build"  # lets offline construction succeed without a real key


class BackboneError(ValueError):
    """A backbone/scaffold spec that cannot be built (unknown provider, incompatible scaffold, ...)."""


@dataclass(frozen=True)
class BackboneSpec:
    """One row of matrix.yaml's ``backbones`` list."""

    id: str
    provider: str  # openai | anthropic | google | cohere | vllm | local
    model: str
    capability_rank: int
    default_scaffold: str = "native"
    reasoning_effort: str | None = None
    temperature: float = 0.0
    base_url_env: str | None = None  # vllm/local: env var holding the OpenAI-compatible base URL
    extra: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, d: dict) -> "BackboneSpec":
        known = {f for f in cls.__dataclass_fields__ if f != "extra"}
        kwargs = {k: v for k, v in d.items() if k in known}
        kwargs["extra"] = {k: v for k, v in d.items() if k not in known}
        return cls(**kwargs)

    def resolve_scaffold(self, scaffold: str) -> str:
        """'default' -> this backbone's default_scaffold; else the requested scaffold."""
        return self.default_scaffold if scaffold == "default" else scaffold


def _openai_client(base_url: str | None = None, key_env: str = "OPENAI_API_KEY"):
    import openai  # deferred: no import-time SDK/key dependency

    api_key = os.environ.get(key_env) or os.environ.get("VLLM_API_KEY") or _PLACEHOLDER_KEY
    return openai.OpenAI(api_key=api_key, base_url=base_url) if base_url else openai.OpenAI(api_key=api_key)


def _resolve_base_url(spec: BackboneSpec) -> str:
    if not spec.base_url_env:
        raise BackboneError(f"backbone {spec.id!r} (provider {spec.provider!r}) needs a base_url_env")
    url = os.environ.get(spec.base_url_env)
    if not url:
        # Construction still succeeds against a local default; a real run needs the env var set.
        return "http://localhost:8000/v1"
    return url


def build_backbone(spec: BackboneSpec, scaffold: str = "default") -> BasePipelineElement:
    """Construct the backbone LLM element for ``spec`` under ``scaffold``.

    Raises ``BackboneError`` for an unbuildable combination (so the runner can skip-with-reason),
    and ``NotImplementedError`` for the not-yet-built ``react`` scaffold.
    """
    scaffold = spec.resolve_scaffold(scaffold)
    if scaffold not in SCAFFOLDS:
        raise BackboneError(f"unknown scaffold {scaffold!r}; known: {SCAFFOLDS}")
    if scaffold == "react":
        raise NotImplementedError("the 'react' scaffold (design §3.3) is not built yet")
    if scaffold == "prompted" and spec.provider not in _PROMPTED_OK:
        raise BackboneError(
            f"prompted scaffold needs an OpenAI-style client; provider {spec.provider!r} "
            f"(backbone {spec.id!r}) only supports 'native'"
        )

    provider = spec.provider
    if provider == "openai":
        from agentdojo.agent_pipeline.llms.openai_llm import OpenAILLM
        from agentdojo.agent_pipeline.llms.prompting_llm import PromptingLLM

        client = _openai_client()
        if scaffold == "native":
            return OpenAILLM(client, spec.model, reasoning_effort=spec.reasoning_effort, temperature=spec.temperature)
        return PromptingLLM(client, spec.model, reasoning_effort=spec.reasoning_effort, temperature=spec.temperature)

    if provider in ("vllm", "local"):
        from agentdojo.agent_pipeline.llms.local_llm import LocalLLM
        from agentdojo.agent_pipeline.llms.prompting_llm import PromptingLLM

        client = _openai_client(base_url=_resolve_base_url(spec))
        # LocalLLM = the open-weight prompted path (XML tool-calls parsed out); PromptingLLM if a
        # native-style prompted path over the same OpenAI-compatible endpoint is wanted.
        if scaffold == "prompted":
            return LocalLLM(client, spec.model, temperature=spec.temperature)
        return PromptingLLM(client, spec.model, temperature=spec.temperature)  # scaffold == "native" over vLLM

    if provider == "anthropic":
        import anthropic

        from agentdojo.agent_pipeline.llms.anthropic_llm import AnthropicLLM

        client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY") or _PLACEHOLDER_KEY)
        return AnthropicLLM(client, spec.model, temperature=spec.temperature)

    if provider == "google":
        from google import genai

        from agentdojo.agent_pipeline.llms.google_llm import GoogleLLM

        client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY") or _PLACEHOLDER_KEY)
        return GoogleLLM(spec.model, client=client, temperature=spec.temperature)

    if provider == "cohere":
        import cohere

        from agentdojo.agent_pipeline.llms.cohere_llm import CohereLLM

        client = cohere.Client(api_key=os.environ.get("COHERE_API_KEY") or _PLACEHOLDER_KEY)
        return CohereLLM(client, spec.model, temperature=spec.temperature)

    raise BackboneError(f"unknown provider {provider!r} for backbone {spec.id!r}")
