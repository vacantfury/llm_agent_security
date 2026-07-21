"""
Thin PromptTransformation wrappers around legacy BaseEncoder implementations.

Each class is a 3-line subclass that:
  - declares its canonical type_name (registry key)
  - points at its legacy encoder class

The factory registers each one via @register_transformation.

Text-only, deterministic set. The LLM-based transformations (llm_set_theory,
llm_formal_logic, llm_quantum_mechanics, llm_classical_language, llm_semantic_camo,
llm_paraphrase) are DETACHED until a real LLM client is wired — re-add their
@register_transformation blocks then (encoder files remain on disk; see
src/llm_utils.py and text_docs/agent_injection/design.md).
"""
from src.prompt_transformations.transformation_factory import register_transformation
from .base_transformation import TextEncoderTransformation
from .encoders.non_llm_baseline_encoder import BaselineEncoder
from .encoders.non_llm_addition_equation_split_reassemble_encoder import (
    AdditionEquationEncoder,
)
from .encoders.non_llm_conditional_probability_encoder import (
    ConditionalProbabilityEncoder,
)
from .encoders.non_llm_symbol_injection_encoder import SymbolInjectionEncoder
from .encoders.non_llm_artprompt_encoder import ArtPromptEncoder
from .encoders.non_llm_homoglyph_encoder import HomoglyphEncoder
from .encoders.non_llm_cipher_encoder import CipherEncoder
from .encoders.non_llm_best_of_n_encoder import BestOfNEncoder


@register_transformation
class BaselineTransformation(TextEncoderTransformation):
    type_name = "non_llm_baseline"
    encoder_class = BaselineEncoder


@register_transformation
class ArtPromptTransformation(TextEncoderTransformation):
    type_name = "non_llm_artprompt"
    encoder_class = ArtPromptEncoder


@register_transformation
class HomoglyphTransformation(TextEncoderTransformation):
    type_name = "non_llm_homoglyph"
    encoder_class = HomoglyphEncoder


@register_transformation
class CipherTransformation(TextEncoderTransformation):
    type_name = "non_llm_cipher"
    encoder_class = CipherEncoder


@register_transformation
class BestOfNTransformation(TextEncoderTransformation):
    type_name = "non_llm_best_of_n"
    encoder_class = BestOfNEncoder


@register_transformation
class AdditionEquationTransformation(TextEncoderTransformation):
    type_name = "non_llm_addition_equation_split_reassemble"
    encoder_class = AdditionEquationEncoder


@register_transformation
class ConditionalProbabilityTransformation(TextEncoderTransformation):
    type_name = "non_llm_conditional_probability"
    encoder_class = ConditionalProbabilityEncoder


@register_transformation
class SymbolInjectionTransformation(TextEncoderTransformation):
    type_name = "non_llm_symbol_injection"
    encoder_class = SymbolInjectionEncoder
