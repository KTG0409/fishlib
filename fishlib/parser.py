"""
Parser module for fishlib.

Parses seafood item descriptions into structured attribute dictionaries.
Handles messy, inconsistent text from various data sources.
"""

import re
import json
import os
from typing import Dict, Any, Optional, List, Tuple

# Load reference data
_DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')

with open(os.path.join(_DATA_DIR, 'standard_codes.json'), 'r') as f:
    STANDARD_CODES = json.load(f)

with open(os.path.join(_DATA_DIR, 'species_aliases.json'), 'r') as f:
    SPECIES_DATA = json.load(f)


def parse(description: str) -> Dict[str, Any]:
    """
    Parse a seafood item description into structured attributes.
    
    This is the main entry point for parsing. It handles messy text from
    various sources (distributors, Circana, suppliers) and extracts standardized
    attributes.
    
    Args:
        description: The item description to parse
                    e.g., "SALMON FIL ATL SKON DTRM 6OZ IVP"
                    
    Returns:
        Dictionary with extracted attributes:
        {
            'raw': original description,
            'species': detected species name,
            'species_code': standardized species code,
            'category': species category (e.g., 'salmon', 'crab'),
            'subspecies': specific type (e.g., 'atlantic', 'king'),
            'form': form code (FIL, PRTN, LOIN, etc.),
            'skin': skin status (SKON, SKLS, SKOFF),
            'bone': bone status (BNLS, BIN, PBO),
            'trim': trim level (A, B, C, D, E, FTRIM),
            'size': size specification (6OZ, 5-7OZ, etc.),
            'pack': packaging (IVP, IQF, etc.),
            'storage': storage type (FRZ, FRSH, RFRSH),
            'harvest': harvest type (WILD, FARM),
            'origin': country of origin code,
            'cut_style': cut style (CENTER, BIAS, BLOCK),
            'brand': detected brand name,
            'count': count size for shrimp/scallops
        }
        
    Example:
        >>> item = parse("SALMON FIL ATL SKON DTRM 6OZ IVP")
        >>> print(item['species'])
        'Atlantic Salmon'
        >>> print(item['form'])
        'FIL'
        >>> print(item['trim'])
        'D'
    """
    if not description:
        return {'raw': '', 'error': 'Empty description'}
    
    result = {
        'raw': description,
        'species': None,
        'species_code': None,
        'category': None,
        'subspecies': None,
        'form': None,
        'skin': None,
        'bone': None,
        'trim': None,
        'size': None,
        'pack': None,
        'storage': None,
        'harvest': None,
        'origin': None,
        'cut_style': None,
        'brand': None,
        'count': None,
        'meat_grade': None,
        'preparation': None,
        'value_added': None,
        'shrimp_form': None
    }
    
    # Normalize text
    text = description.upper().strip()
    
    # Extract species
    species_info = _extract_species(text)
    if species_info:
        result.update(species_info)
    
    # Extract form
    result['form'] = _extract_form(text)
    
    # Extract shrimp-specific form (P&D, PUD, SHELL_ON, EZ PEEL, etc.)
    result['shrimp_form'] = _extract_shrimp_form(text)
    
    # Extract skin status
    result['skin'] = _extract_attribute(text, 'skin')
    
    # Extract bone status
    result['bone'] = _extract_attribute(text, 'bone')
    
    # Extract trim level
    result['trim'] = _extract_attribute(text, 'trim')
    
    # Extract size
    result['size'] = _extract_size(text)
    
    # Extract packaging
    result['pack'] = _extract_attribute(text, 'pack')
    
    # Extract storage
    result['storage'] = _extract_attribute(text, 'storage')
    
    # Extract harvest type
    result['harvest'] = _extract_attribute(text, 'harvest')
    
    # Extract origin
    result['origin'] = _extract_attribute(text, 'origin_country')
    
    # Extract cut style
    result['cut_style'] = _extract_attribute(text, 'cut_style')
    
    # Extract count (for shrimp, scallops)
    result['count'] = _extract_count(text)
    
    # Extract brand (common brands)
    result['brand'] = _extract_brand(text)
    
    # Extract meat grade (crab, lobster)
    result['meat_grade'] = _extract_attribute(text, 'meat_grade')
    
    # Extract preparation (raw, cooked, smoked, cured)
    result['preparation'] = _extract_attribute(text, 'preparation')
    
    # Extract value-added (breaded, stuffed, marinated, etc.)
    result['value_added'] = _extract_attribute(text, 'value_added')
    
    return result


def parse_description(description: str) -> Dict[str, Any]:
    """
    Alias for parse() - for compatibility with different naming conventions.
    """
    return parse(description)


def _extract_species(text: str) -> Optional[Dict[str, Any]]:
    """
    Extract species information from text.
    
    Uses a priority system to avoid alias collisions:
      1. Category name in text + subspecies alias match (strongest)
      2. Category name in text, no subspecies match (category-level)
      3. Subspecies alias only, no category name (fallback for e.g., 'SABLEFISH')
    
    Within each priority level, longer alias matches win to prevent
    short aliases like 'ATL' from shadowing 'ATLANTIC'.
    
    Returns dict with species, species_code, category, subspecies.
    """
    text_upper = text.upper()
    
    # --- Priority 1: Category name present + subspecies alias ---
    # Collect ALL matches where the category name is in the text,
    # then pick the one with the longest alias match.
    category_plus_alias_matches = []
    category_only_matches = []
    
    for category, cat_data in SPECIES_DATA.items():
        if category.upper() not in text_upper:
            continue
        
        found_subspecies = False
        for subspec, spec_info in cat_data.get('species', {}).items():
            for alias in spec_info.get('aliases', []):
                if alias in text_upper:
                    category_plus_alias_matches.append({
                        'species': spec_info['name'],
                        'species_code': f"{category.upper()}|{subspec.upper()}",
                        'category': category,
                        'subspecies': subspec,
                        '_alias_len': len(alias)
                    })
                    found_subspecies = True
        
        if not found_subspecies:
            category_only_matches.append({
                'species': category.title(),
                'species_code': category.upper(),
                'category': category,
                'subspecies': None
            })
    
    # If we got category+alias matches, return the longest alias match
    if category_plus_alias_matches:
        best = max(category_plus_alias_matches, key=lambda m: m['_alias_len'])
        del best['_alias_len']
        return best
    
    # --- Priority 2: Category name present, no subspecies alias ---
    if category_only_matches:
        return category_only_matches[0]
    
    # --- Priority 3: Alias only, no category name in text ---
    # e.g., "SABLEFISH FIL" has no "COD" in text but SABLEFISH is a cod alias.
    # Collect all, pick the longest alias to minimize false positives.
    alias_only_matches = []
    
    for category, cat_data in SPECIES_DATA.items():
        for subspec, spec_info in cat_data.get('species', {}).items():
            for alias in spec_info.get('aliases', []):
                if len(alias) >= 3 and alias in text_upper:
                    alias_only_matches.append({
                        'species': spec_info['name'],
                        'species_code': f"{category.upper()}|{subspec.upper()}",
                        'category': category,
                        'subspecies': subspec,
                        '_alias_len': len(alias)
                    })
    
    if alias_only_matches:
        best = max(alias_only_matches, key=lambda m: m['_alias_len'])
        del best['_alias_len']
        return best
    
    return None


def _extract_form(text: str) -> Optional[str]:
    """
    Extract form, with special handling for TAIL ON / TAIL OFF.
    
    'TAIL ON' and 'TAIL OFF' are shrimp processing descriptors, NOT form=TAIL.
    Only match TAIL as a form when it's not followed by ON/OFF.
    """
    text_upper = text.upper()
    
    if 'form' not in STANDARD_CODES:
        return None
    
    matches = []
    for code, info in STANDARD_CODES['form'].items():
        for alias in info.get('aliases', []):
            pattern = r'(?:^|[\s/\-_,])' + re.escape(alias) + r'(?:$|[\s/\-_,])'
            if re.search(pattern, text_upper) or text_upper == alias:
                # Special case: TAIL should not match when followed by ON or OFF
                if code == 'TAIL':
                    tail_on_off = re.search(r'(?:^|[\s/\-_,])TAIL\s*(?:ON|OFF)(?:$|[\s/\-_,])', text_upper)
                    if tail_on_off:
                        continue  # Skip - this is "TAIL ON/OFF", not form=TAIL
                matches.append((len(alias), code, alias))
    
    if matches:
        matches.sort(reverse=True, key=lambda x: x[0])
        return matches[0][1]
    
    return None


def _extract_shrimp_form(text: str) -> Optional[str]:
    """
    Extract shrimp-specific processing form (P&D, PUD, SHELL ON, EZ PEEL, TAIL ON/OFF).
    
    These are critical for shrimp pricing but don't map to the standard 'form' codes.
    """
    text_upper = text.upper()
    
    SHRIMP_FORMS = {
        'P&D': [r'P\s*&\s*D', r'P/D', r'PD', r'PEELED\s+(?:&\s+)?DEVEINED'],
        'PUD': [r'PUD', r'P/UD', r'PEELED\s+UNDEVEINED'],
        'SHELL_ON': [r'SHELL\s*ON', r'SHL\s*ON', r'S/ON', r'HEAD\s*OFF\s*SHELL\s*ON', r'HOSO'],
        'TAIL_ON': [r'TAIL\s*ON', r'T/ON', r'EZ\s*PEEL', r'EZPEEL'],
        'TAIL_OFF': [r'TAIL\s*OFF', r'T/OFF', r'TAILLESS'],
        'HEAD_ON': [r'HEAD\s*ON', r'H/ON', r'HOON'],
    }
    
    best_match = None
    best_len = 0
    
    for code, patterns in SHRIMP_FORMS.items():
        for pat in patterns:
            full_pattern = r'(?:^|[\s/\-_,])(' + pat + r')(?:$|[\s/\-_,])'
            m = re.search(full_pattern, text_upper)
            if m:
                match_len = len(m.group(1))
                if match_len > best_len:
                    best_len = match_len
                    best_match = code
    
    return best_match


def _extract_attribute(text: str, category: str) -> Optional[str]:
    """
    Extract a standardized attribute from text.
    """
    if category not in STANDARD_CODES:
        return None
    
    text_upper = text.upper()
    
    # Sort by alias length descending to match longer aliases first
    # Also require word boundaries to avoid partial matches
    matches = []
    for code, info in STANDARD_CODES[category].items():
        for alias in info.get('aliases', []):
            # Check for word boundary match (surrounded by space, start, end, or punctuation)
            pattern = r'(?:^|[\s/\-_,])' + re.escape(alias) + r'(?:$|[\s/\-_,])'
            if re.search(pattern, text_upper) or text_upper == alias:
                matches.append((len(alias), code, alias))
    
    if matches:
        # Return the code with the longest matching alias
        matches.sort(reverse=True, key=lambda x: x[0])
        return matches[0][1]
    
    return None


def _extract_size(text: str) -> Optional[str]:
    """
    Extract size specification from text.
    
    Handles various formats:
    - "6 oz", "6OZ", "6 OZ"
    - "5-7 oz", "5-7OZ"
    - "3-4 lb", "3-4#"
    - "2-3#"
    """
    text_upper = text.upper()
    
    # Pattern for oz sizes
    oz_patterns = [
        r'(\d+(?:\.\d+)?)\s*-\s*(\d+(?:\.\d+)?)\s*(?:OZ|OUNCE)',  # 5-7 oz
        r'(\d+(?:\.\d+)?)\s*(?:OZ|OUNCE)',  # 6 oz
    ]
    
    for pattern in oz_patterns:
        match = re.search(pattern, text_upper)
        if match:
            if len(match.groups()) == 2:
                return f"{match.group(1)}-{match.group(2)}OZ"
            else:
                return f"{match.group(1)}OZ"
    
    # Pattern for lb sizes
    lb_patterns = [
        r'(\d+(?:\.\d+)?)\s*-\s*(\d+(?:\.\d+)?)\s*(?:LB|#|POUND)',  # 3-4 lb
        r'(\d+(?:\.\d+)?)\s*(?:LB|#|POUND)',  # 2 lb
    ]
    
    for pattern in lb_patterns:
        match = re.search(pattern, text_upper)
        if match:
            if len(match.groups()) == 2:
                return f"{match.group(1)}-{match.group(2)}LB"
            else:
                return f"{match.group(1)}LB"
    
    return None


def _extract_count(text: str) -> Optional[str]:
    """
    Extract count size (for shrimp, scallops).
    
    Handles:
    - "16/20", "21/25", "U10", "U/10"
    - "16-20 ct", "21-25 count"
    """
    text_upper = text.upper()
    
    # U-count pattern (under X)
    u_match = re.search(r'U[/-]?(\d+)', text_upper)
    if u_match:
        return f"U{u_match.group(1)}"
    
    # Range count pattern
    count_match = re.search(r'(\d+)\s*[/-]\s*(\d+)(?:\s*CT|\s*COUNT)?', text_upper)
    if count_match:
        return f"{count_match.group(1)}/{count_match.group(2)}"
    
    return None


def _extract_brand(text: str) -> Optional[str]:
    """
    Extract brand name from common foodservice brands.
    """
    COMMON_BRANDS = [
        'PORTICO', 'TRIDENT', 'HIGH LINER', 'HIGHLINER',
        'ICYBAY', 'SEAMAZZ', 'HARBOR BANKS', 'TRUE NORTH', 'SEAFARERS',
        'FISHERY PRODUCTS', 'FPI', 'NETUNO', 'PANAPESCE', 'PANAPESCA',
        'ACME', 'PHILLIPS', 'HANDY', 'TAMPA MAID', 'MRS FRIDAYS',
        'KING & PRINCE', 'CHICKEN OF THE SEA', 'BUMBLE BEE',
        'GORTONS', 'AQUASTAR', 'ICICLE', 'TRIDENT SEAFOODS',
        'OCEAN BEAUTY', 'PACIFIC SEAFOOD', 'CLEARWATER'
    ]
    
    text_upper = text.upper()
    
    for brand in COMMON_BRANDS:
        if brand in text_upper:
            return brand.title()
    
    return None


def parse_batch(descriptions: List[str]) -> List[Dict[str, Any]]:
    """
    Parse multiple descriptions at once.
    
    Args:
        descriptions: List of item descriptions
        
    Returns:
        List of parsed result dictionaries
    """
    return [parse(desc) for desc in descriptions]


def extract_key_attributes(description: str) -> Dict[str, str]:
    """
    Extract only the key attributes needed for matching.
    
    This is a simplified version of parse() that returns only
    the attributes typically used for comparison keys.
    
    Returns:
        Dict with: species, form, skin, bone, size, trim
    """
    result = parse(description)
    
    return {
        'species': result.get('subspecies') or result.get('category'),
        'form': result.get('form'),
        'skin': result.get('skin'),
        'bone': result.get('bone'),
        'size': result.get('size'),
        'trim': result.get('trim'),
        'meat_grade': result.get('meat_grade'),
        'preparation': result.get('preparation'),
        'value_added': result.get('value_added'),
        'shrimp_form': result.get('shrimp_form')
    }
