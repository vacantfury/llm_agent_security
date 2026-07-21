"""Defense baselines for the encoded-injection matrix (surface-form vs. behavioral).

`build_defended_pipeline(defense, llm, system_message, ...)` returns an AgentDojo AgentPipeline
defended by the named baseline; `DEFENSES` is the matrix's defense axis; `defense_class` tags each
as surface-form / behavioral for the thesis split.
"""

from .factory import DEFENSES, build_defended_pipeline, defense_class

__all__ = ["DEFENSES", "build_defended_pipeline", "defense_class"]
