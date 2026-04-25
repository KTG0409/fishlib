"""fishlib — parse, standardize, and compare seafood product descriptions."""

__version__ = "0.6.4"
__author__ = "Karen Morton"

from .parser import parse, parse_batch, extract_key_attributes
from .matcher import (
    comparison_key,
    match,
    is_comparable,
    match_score,
    find_matches,
    explain_difference,
)
from .standards import (
    standardize_form,
    standardize_skin,
    standardize_bone,
    standardize_trim,
    standardize_pack,
    standardize_storage,
    standardize_cut_style,
    standardize_harvest,
    standardize_origin,
    standardize_size,
    get_standard_code,
    get_code_info,
    list_codes,
)

__all__ = [
    "__version__",
    "parse",
    "parse_batch",
    "extract_key_attributes",
    "comparison_key",
    "match",
    "is_comparable",
    "match_score",
    "find_matches",
    "explain_difference",
    "standardize_form",
    "standardize_skin",
    "standardize_bone",
    "standardize_trim",
    "standardize_pack",
    "standardize_storage",
    "standardize_cut_style",
    "standardize_harvest",
    "standardize_origin",
    "standardize_size",
    "get_standard_code",
    "get_code_info",
    "list_codes",
]
