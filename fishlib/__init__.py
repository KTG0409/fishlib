"""
fishlib - A Python library for parsing, standardizing, and comparing foodservice seafood products.

Created by Karen Morton
License: MIT

THE PROBLEM THIS SOLVES:
You need deep fish knowledge to know if a PMI comparison is accurate. A 6oz salmon 
portion might be $4/lb more than industry - but that's because it's a center-cut 
bias portion vs block-cut with tails. Without the right attributes, it looks like 
you're overpriced when you're comparing apples to oranges.

THE GOAL:
Capture attributes correctly so ANYONE can trust the data without being a fish expert.

v0.4.0 — Freeze Cycle Awareness:
    import fishlib
    
    # Pollock caught in Alaska, processed in China = TWICE FROZEN
    item = fishlib.parse("POLLOCK FIL WILD ALASKA PROCESSED IN CHINA 6OZ IVP")
    print(item['origin_harvest'])    # 'USA'
    print(item['origin_processed'])  # 'CHN'
    print(item['freeze_cycle'])      # 'TWICE'
    
    # Same pollock, processed domestically = SINGLE FROZEN
    item2 = fishlib.parse("POLLOCK FIL WILD ALASKA 6OZ IVP")
    
    # These are NOT comparable for pricing
    result = fishlib.match(item, item2)
    print(result['is_comparable'])   # False
    print(result['recommendation'])
    # 'NOT COMPARABLE - Different freeze cycle (single vs twice-frozen)'
"""

__version__ = "0.4.3"
__author__ = "Karen Morton"
__license__ = "MIT"

from .parser import parse, parse_description
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
    standardize_origin_harvest,
    standardize_origin_processed,
    standardize_size,
    standardize_meat_grade,
    standardize_preparation,
    standardize_value_added,
    get_standard_code,
    list_codes
)
from .matcher import (
    comparison_key,
    match,
    is_comparable,
    find_matches,
    match_score
)
from . import species
from . import reference

__all__ = [
    # Parser functions
    'parse',
    'parse_description',
    
    # Standardization functions
    'standardize_form',
    'standardize_skin',
    'standardize_bone',
    'standardize_trim',
    'standardize_pack',
    'standardize_storage',
    'standardize_cut_style',
    'standardize_harvest',
    'standardize_origin',
    'standardize_origin_harvest',
    'standardize_origin_processed',
    'standardize_size',
    'standardize_meat_grade',
    'standardize_preparation',
    'standardize_value_added',
    'get_standard_code',
    'list_codes',
    
    # Matcher functions
    'comparison_key',
    'match',
    'is_comparable',
    'find_matches',
    'match_score',
    
    # Submodules
    'species',
    'reference',
]
