"""Convenience single-string interface over the PromptTransformation chain.

`encode("some text", "non_llm_cipher", cipher="base64") -> "<encoded>"`. Thin wrapper
over the factory so callers (e.g. the AgentDojo encoded-payload attack) don't have to
build Prompt objects or a step directory by hand.
"""

import tempfile
from pathlib import Path

from .schemas import Prompt
from .transformation_factory import create_transformation


def encode(text: str, transform: str, **kwargs) -> str:
    """Encode `text` with the named (deterministic) transformation; return the string."""
    transformation = create_transformation(transform, **kwargs)
    prompt = Prompt(original=text, encoded=text)
    with tempfile.TemporaryDirectory() as step_dir:
        (out,) = transformation.apply([prompt], Path(step_dir))
    return out.encoded
