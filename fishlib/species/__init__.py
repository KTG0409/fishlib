"""Species module for fishlib — convenience accessors over species_aliases.json."""
import json
import os
from typing import Dict, Any, Optional, List, Tuple

_DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
_SPECIES_FILE = os.path.join(_DATA_DIR, 'species_aliases.json')

try:
    with open(_SPECIES_FILE, 'r') as f:
        SPECIES_DATA = json.load(f)
except FileNotFoundError:
    SPECIES_DATA = {}


def get_species_info(category: str, subspecies: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """Return detailed info for a species, or category-level info if no subspecies given."""
    category = category.lower()
    if category not in SPECIES_DATA:
        return None

    cat_data = SPECIES_DATA[category]

    if subspecies:
        subspecies = subspecies.lower()
        if subspecies in cat_data.get('species', {}):
            result = cat_data['species'][subspecies].copy()
            result['category'] = category
            result['subspecies'] = subspecies
            return result

    return {
        'category': category,
        'name': category.title(),
        'species_count': len(cat_data.get('species', {})),
        'forms': cat_data.get('forms', []),
        'has_trim_levels': 'trim_levels' in cat_data,
        'has_count_sizes': 'count_sizes' in cat_data,
    }


def list_species(category: Optional[str] = None) -> List[str]:
    """List all categories, or all subspecies within a given category."""
    if category is None:
        return list(SPECIES_DATA.keys())
    category = category.lower()
    if category in SPECIES_DATA:
        return list(SPECIES_DATA[category].get('species', {}).keys())
    return []


def get_price_tier(category: str, subspecies: Optional[str] = None) -> Optional[str]:
    """Return the price tier string for a species, or None."""
    info = get_species_info(category, subspecies)
    if info:
        return info.get('price_tier')
    return None


def get_price_range(category: str, subspecies: Optional[str] = None) -> Optional[Tuple[float, float]]:
    """Return (low, high) price range tuple if defined on the species, else None."""
    info = get_species_info(category, subspecies)
    if info and 'typical_price_range' in info:
        return tuple(info['typical_price_range'])
    return None


def get_aliases(category: str, subspecies: str) -> List[str]:
    """Return the alias list for a species."""
    info = get_species_info(category, subspecies)
    if info:
        return info.get('aliases', [])
    return []


def get_harvest_type(category: str, subspecies: str) -> Optional[str]:
    """Return 'wild', 'farm', 'both', 'processed', or None."""
    info = get_species_info(category, subspecies)
    if info:
        return info.get('harvest')
    return None


def identify_species(text: str) -> Optional[Dict[str, Optional[str]]]:
    """Lightweight species identifier (parser.parse is more accurate)."""
    text_upper = text.upper()
    for category, cat_data in SPECIES_DATA.items():
        for subspecies, spec_info in cat_data.get('species', {}).items():
            for alias in spec_info.get('aliases', []):
                if alias in text_upper:
                    return {'category': category, 'subspecies': subspecies}
        if category.upper() in text_upper:
            return {'category': category, 'subspecies': None}
    return None
