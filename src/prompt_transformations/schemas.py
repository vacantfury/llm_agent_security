"""Minimal local Prompt carrier for the decoupled text-encoder payload package.

Decoupled from the sibling repo's `src.experiment.schemas.Prompt` (a richer pydantic
model carrying image fields + provenance for the full VLM pipeline). This repo is
text-only for now, so only the fields the text encoders actually read/write are kept:
they read `.encoded` and write via `.model_copy(update={"encoded": ..., "encoding": ...})`.
`id`/`original` default to "" so a single ad-hoc string can be wrapped for one-off use.
"""

from pydantic import BaseModel


class Prompt(BaseModel):
    id: str = ""
    original: str = ""
    encoded: str
    encoding: str = ""
