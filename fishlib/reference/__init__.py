"""Reference data: trim levels, cut styles, price tiers, and convenience lookups."""
import json
import os
from typing import Dict, Any, Optional, Tuple

_DATA = os.path.join(os.path.dirname(__file__), '..', 'data', 'species_aliases.json')

with open(_DATA, 'r') as _f:
    _SPECIES_DATA = json.load(_f)


# Trim levels live on the salmon entry in the JSON (only salmon uses A–E)
TRIM_LEVELS: Dict[str, Dict[str, Any]] = _SPECIES_DATA.get('salmon', {}).get('trim_levels', {})


# Cut styles for portions
CUT_STYLES: Dict[str, Dict[str, Any]] = {
    'CENTER': {
        'description': 'Portions from center of fish only, no tails or nape',
        'premium': True,
    },
    'BIAS': {
        'description': 'Cut at an angle for better plate presentation',
        'premium': True,
    },
    'BLOCK': {
        'description': 'Straight cuts end-to-end; includes tails',
        'premium': False,
    },
    'RANDOM': {
        'description': 'Mixed pieces, various shapes and sizes',
        'premium': False,
    },
}


def trim_levels(species: str = 'salmon') -> Dict[str, Dict[str, Any]]:
    """Return the trim-level definitions for a species (currently salmon only)."""
    return _SPECIES_DATA.get(species.lower(), {}).get('trim_levels', {})


def is_trim_skin_on(trim: str) -> bool:
    """Return True if the given trim code has skin on (A-D for salmon); False for E."""
    info = TRIM_LEVELS.get(trim, {})
    return info.get('skin') == 'on'


def cut_style(name: str) -> Optional[Dict[str, Any]]:
    """Look up a cut-style definition by name (case-insensitive)."""
    return CUT_STYLES.get(name.upper())


def price_tier(category: str, subspecies: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """Return {'tier': ...} for the given species, or None."""
    cat = _SPECIES_DATA.get(category.lower())
    if not cat:
        return None
    if subspecies:
        sp = cat.get('species', {}).get(subspecies.lower())
        if sp and 'price_tier' in sp:
            return {'tier': sp['price_tier']}
    return None
