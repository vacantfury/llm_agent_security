"""AgentDojo integration: backbone construction (scaffolds × providers) and the matrix run driver.

- `backbones.build_backbone` — build an AgentDojo backbone element from a matrix.yaml spec.
- `runner` — enumerate the payload×defense×scaffold×backbone×suite matrix, assemble each defended
  pipeline, and run AgentDojo's action-scored benchmark (with an offline no-spend `--dry-run`).
"""

from src.harness.backbones import BackboneError, BackboneSpec, build_backbone

__all__ = ["BackboneError", "BackboneSpec", "build_backbone"]
