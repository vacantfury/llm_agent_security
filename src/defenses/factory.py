"""Assemble AgentDojo agent pipelines with our defense baselines — one uniform seam for the matrix.

Reuses AgentDojo's `AgentPipeline.from_config` for the shipped defenses (none / tool_filter /
spotlighting_with_delimiting / repeat_user_prompt) and hand-builds the two extra baselines that
AgentDojo doesn't ship the way we want:

  * **PIGuard** (`li-etal-2025-piguard`, ACL'25) — the *published* surface-form classifier baseline,
    in place of the non-published ProtectAI DeBERTa artifact AgentDojo ships. Same `TransformersBasedPIDetector`
    seam, different HF model.
  * **MELON** (`zhu2025melon`, ICML'25) — the *behavioral* resistant baseline; the element is ported in
    `src/defenses/melon.py` (imported lazily so this module loads before/while that port lands).

`protectai_deberta` is kept as the non-published AgentDojo default, for comparison only.
See text_docs/agent_injection/design.md §5.

RUN-TIME items to confirm when we first construct these (build-time fetch / spend, not import):
  - PIGuard's label scheme (`classifier_safe_label`) — VERIFIED 2026-07-22 on cluster: the model emits
    labels `benign` / `injection`, so `classifier_safe_label="benign"` is correct. (leolee99/PIGuard
    ships custom model code -> loaded via `_TrustedTransformersPIDetector`, below.)
  - passing a constructed `llm` object (not a model-name string) through `PipelineConfig`.
"""

import json
from functools import partial
from typing import Literal

from agentdojo.agent_pipeline import AgentPipeline, PipelineConfig
from agentdojo.agent_pipeline.base_pipeline_element import BasePipelineElement
from agentdojo.agent_pipeline.basic_elements import InitQuery, SystemMessage
from agentdojo.agent_pipeline.pi_detector import (
    PromptInjectionDetector,
    TransformersBasedPIDetector,
)
from agentdojo.agent_pipeline.tool_execution import (
    ToolsExecutionLoop,
    ToolsExecutor,
    tool_result_to_str,
)

# HF model ids.
PIGUARD_MODEL = "leolee99/PIGuard"  # published (ACL'25) — our surface-form classifier baseline
PROTECTAI_MODEL = "protectai/deberta-v3-base-prompt-injection-v2"  # non-published AgentDojo default (comparison)

# Defense-class tags — the surface-form vs. behavioral split (lit review §3 / design §5).
SURFACE_FORM = frozenset({"spotlighting_with_delimiting", "tool_filter", "piguard", "protectai_deberta"})
BEHAVIORAL = frozenset({"melon"})  # + datasentinel when wired

# Shipped defenses handled by AgentDojo from_config; value = the name from_config expects.
_SHIPPED_ALIAS: dict[str, str | None] = {
    "none": None,
    "tool_filter": "tool_filter",
    "spotlighting_with_delimiting": "spotlighting_with_delimiting",
    "repeat_user_prompt": "repeat_user_prompt",
    "protectai_deberta": "transformers_pi_detector",
}

# The matrix's defense axis (headline set). datasentinel is an optional stretch add.
DEFENSES = ["none", "spotlighting_with_delimiting", "tool_filter", "piguard", "melon", "protectai_deberta"]


def _tool_output_formatter(tool_output_format: str | None):
    if tool_output_format == "json":
        return partial(tool_result_to_str, dump_fn=json.dumps)
    return tool_result_to_str


class _TrustedTransformersPIDetector(TransformersBasedPIDetector):
    """``TransformersBasedPIDetector`` that loads the HF classifier with ``trust_remote_code=True``.

    Some published classifier repos ship custom model code (``leolee99/PIGuard``, ACL'25) that
    ``transformers.pipeline`` refuses to run without ``trust_remote_code=True`` — the stock detector
    never passes it, so every PIGuard cell would silently *skip* (verified: the dry-run reported all
    9 piguard cells skipped on a ValueError until this landed). We replicate the parent ``__init__``
    and add only that flag — calling ``super().__init__`` would build the pipeline WITHOUT the flag
    and raise before we could rebuild. ``trust_remote_code=True`` executes code FROM the model repo;
    acceptable for a pinned, published research artifact on a research cluster — never point this at
    an untrusted model id."""

    def __init__(
        self,
        model_name: str,
        safe_label: str,
        threshold: float = 0.5,
        mode: Literal["message", "full_conversation"] = "message",
        raise_on_injection: bool = False,
    ) -> None:
        PromptInjectionDetector.__init__(self, mode=mode, raise_on_injection=raise_on_injection)
        import torch
        from transformers import pipeline

        self.model_name = model_name
        self.safe_label = safe_label
        self.threshold = threshold
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.pipeline = pipeline(
            "text-classification", model=self.model_name, device=device, trust_remote_code=True
        )


def _classifier_pipeline(
    llm: BasePipelineElement,
    system_message: str,
    *,
    model_name: str,
    safe_label: str,
    threshold: float,
    tool_output_format: str | None,
    label: str,
    trust_remote_code: bool = False,
) -> AgentPipeline:
    """Mirror AgentDojo's `transformers_pi_detector` branch with a chosen HF classifier model.

    ``trust_remote_code`` selects the trusted-loading subclass (needed for PIGuard; see above)."""
    fmt = _tool_output_formatter(tool_output_format)
    detector_cls = _TrustedTransformersPIDetector if trust_remote_code else TransformersBasedPIDetector
    tools_loop = ToolsExecutionLoop(
        [
            ToolsExecutor(fmt),
            detector_cls(model_name=model_name, safe_label=safe_label, threshold=threshold, mode="message"),
            llm,
        ]
    )
    pipeline = AgentPipeline([SystemMessage(system_message), InitQuery(), llm, tools_loop])
    pipeline.name = f"{getattr(llm, 'name', 'llm')}-{label}"
    return pipeline


def build_defended_pipeline(
    defense: str,
    llm: BasePipelineElement,
    system_message: str,
    *,
    tool_output_format: Literal["yaml", "json"] | None = None,
    piguard_model: str = PIGUARD_MODEL,
    classifier_safe_label: str = "benign",  # VERIFIED 2026-07-22 on cluster (labels: benign / injection)
    classifier_threshold: float = 0.5,
    melon_kwargs: dict | None = None,
) -> AgentPipeline:
    """Build an AgentDojo pipeline defended by `defense`, around an already-constructed `llm`."""
    if defense in _SHIPPED_ALIAS:
        # `llm` is a pre-built element, so from_config takes the `else config.llm` branch and never
        # reads `model_id`/`system_message_name` (both required PipelineConfig fields, hence None).
        config = PipelineConfig(
            llm=llm,
            model_id=None,
            defense=_SHIPPED_ALIAS[defense],
            system_message=system_message,
            system_message_name=None,
            tool_output_format=tool_output_format,
        )
        return AgentPipeline.from_config(config)

    if defense == "piguard":
        return _classifier_pipeline(
            llm,
            system_message,
            model_name=piguard_model,
            safe_label=classifier_safe_label,
            threshold=classifier_threshold,
            tool_output_format=tool_output_format,
            label="piguard",
            trust_remote_code=True,  # leolee99/PIGuard ships custom model code (see _TrustedTransformersPIDetector)
        )

    if defense == "melon":
        from .melon import MELON  # lazy: ported in src/defenses/melon.py

        fmt = _tool_output_formatter(tool_output_format)
        tools_loop = ToolsExecutionLoop([ToolsExecutor(fmt), MELON(**(melon_kwargs or {})), llm])
        pipeline = AgentPipeline([SystemMessage(system_message), InitQuery(), llm, tools_loop])
        pipeline.name = f"{getattr(llm, 'name', 'llm')}-melon"
        return pipeline

    raise ValueError(f"Unknown defense {defense!r}. Known: {DEFENSES}")


def defense_class(defense: str) -> str:
    """'surface-form' | 'behavioral' | 'none' — for the thesis split in reporting."""
    if defense == "none":
        return "none"
    if defense in BEHAVIORAL:
        return "behavioral"
    if defense in SURFACE_FORM:
        return "surface-form"
    return "unknown"
