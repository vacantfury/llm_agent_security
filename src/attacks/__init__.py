"""Encoded indirect-injection attacks for AgentDojo.

Importing this package registers the `encoded_<scheme>` attacks into AgentDojo's attack
registry. Point AgentDojo at it with `--module-to-load src.attacks` (CLI) or `import
src.attacks` before `load_attack(...)` (programmatic).
"""

from . import encoded_injection  # noqa: F401  (registers the attacks on import)
