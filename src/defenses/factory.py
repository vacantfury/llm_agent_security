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
  - PIGuard's label scheme (`classifier_safe_label`) against the leolee99/PIGuard model card.
  - passing a constructed `llm` object (not a model-name string) through `PipelineConfig`.
"""

import json
from functools import partial

from agentdojo.agent_pipeline import AgentPipeline, PipelineConfig
from agentdojo.agent_pipeline.base_pipeline_element import BasePipelineElement
from agentdojo.agent_pipeline.basic_elements import InitQuery, SystemMessage
from agentdojo.agent_pipeline.pi_detector import TransformersBasedPIDetector
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


def _tool_output_formatter(tool_output_format: str):
    if tool_output_format == "json":
        return partial(tool_result_to_str, dump_fn=json.dumps)
    return tool_result_to_str


def _classifier_pipeline(
    llm: BasePipelineElement,
    system_message: str,
    *,
    model_name: str,
    safe_label: str,
    threshold: float,
    tool_output_format: str,
    label: str,
) -> AgentPipeline:
    """Mirror AgentDojo's `transformers_pi_detector` branch with a chosen HF classifier model."""
    fmt = _tool_output_formatter(tool_output_format)
    tools_loop = ToolsExecutionLoop(
        [
            ToolsExecutor(fmt),
            TransformersBasedPIDetector(model_name=model_name, safe_label=safe_label, threshold=threshold, mode="message"),
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
    tool_output_format: str = "text",
    piguard_model: str = PIGUARD_MODEL,
    classifier_safe_label: str = "benign",  # VERIFY against leolee99/PIGuard model card at run time
    classifier_threshold: float = 0.5,
    melon_kwargs: dict | None = None,
) -> AgentPipeline:
    """Build an AgentDojo pipeline defended by `defense`, around an already-constructed `llm`."""
    if defense in _SHIPPED_ALIAS:
        config = PipelineConfig(
            llm=llm,
            defense=_SHIPPED_ALIAS[defense],
            system_message=system_message,
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
