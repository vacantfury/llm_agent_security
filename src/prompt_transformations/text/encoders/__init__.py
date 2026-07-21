"""
Concrete prompt encoders for transformation.

This package contains implementations of different prompt transformation techniques.
Each encoder is in its own file for easy maintenance and extension.

Text-only, deterministic set: the LLM-based encoders (set-theory / formal-logic /
classical-Chinese / quantum / semantic-camo / paraphrase) are DETACHED here — their
files remain on disk but are not imported/registered until a real LLM client is wired
(see src/llm_utils.py and text_docs/agent_injection/design.md).

To add a new encoder:
1. Create a new file in this directory (e.g., non_llm_my_encoder.py)
2. Create a class inheriting from BaseEncoder
3. Implement the process() method
4. Register a thin wrapper in ../wrappers.py via @register_transformation
"""

# Import concrete (deterministic) encoders
from .non_llm_addition_equation_split_reassemble_encoder import AdditionEquationEncoder
from .non_llm_conditional_probability_encoder import ConditionalProbabilityEncoder
from .non_llm_symbol_injection_encoder import SymbolInjectionEncoder
from .non_llm_baseline_encoder import BaselineEncoder
from .non_llm_artprompt_encoder import ArtPromptEncoder
from .non_llm_homoglyph_encoder import HomoglyphEncoder


# Export all
__all__ = [
    'AdditionEquationEncoder',
    'ConditionalProbabilityEncoder',
    'SymbolInjectionEncoder',
    'BaselineEncoder',
    'ArtPromptEncoder',
    'HomoglyphEncoder',
]
