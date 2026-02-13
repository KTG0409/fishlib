"""
Parser module for fishlib.

Parses seafood item descriptions into structured attribute dictionaries.
Handles messy, inconsistent text from various data sources.

v0.4.0 changes:
  - Split 'origin' into 'origin_harvest' and 'origin_processed'
  - New 'freeze_cycle' attribute (SINGLE or TWICE) inferred from
    processing country + species category
  - Backward-compatible: 'origin' still populated for legacy use
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


# ---------------------------------------------------------------------------
# Twice-frozen inference constants
# ---------------------------------------------------------------------------

# Asian processing countries where finfish is typically twice-frozen:
# Caught/farmed elsewhere → frozen → shipped to Asia → thawed → processed → refrozen
TWICE_FROZEN_PROCESSING_COUNTRIES = {
    'CHN', 'VNM', 'THA', 'IDN', 'IND', 'BGD', 'MMR', 'PHL',
}

# Species categories that are FINFISH (twice-frozen logic applies)
# Crustaceans, cephalopods, and mollusks are exempt
FINFISH_CATEGORIES = {
    'salmon', 'cod', 'pollock', 'haddock', 'halibut', 'flounder', 'sole',
    'tilapia', 'swai', 'catfish', 'tuna', 'mahi', 'swordfish', 'snapper',
    'grouper', 'branzino', 'sea_bass', 'trout', 'barramundi', 'wahoo',
    'monkfish', 'anchovy', 'whiting', 'perch', 'sardine', 'herring',
    'mackerel', 'hake', 'orange_roughy', 'corvina', 'cobia', 'hamachi',
    'pike', 'rockfish',
}

# Categories EXEMPT from twice-frozen logic
# (crustaceans and cephalopods handle freezing differently)
EXEMPT_CATEGORIES = {
    'shrimp', 'crab', 'lobster', 'crawfish', 'scallop', 'clam',
    'oyster', 'mussel', 'calamari', 'octopus', 'langostino', 'conch',
}


def parse(description: str) -> Dict[str, Any]:
    """
    Parse a seafood item description into structured attributes.
    
    This is the main entry point for parsing. It handles messy text from
    various sources (distributors, Circana, suppliers) and extracts standardized
    attributes.
    
    Args:
        description: The item description to parse
                    e.g., "POLLOCK FIL WILD ALASKA PROC CHINA 6OZ IVP"
                    
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
            'origin': country of origin code (legacy, first detected),
            'origin_harvest': where fish was caught/farmed,
            'origin_processed': where fish was cut/portioned,
            'freeze_cycle': SINGLE or TWICE (finfish only),
            'cut_style': cut style (CENTER, BIAS, BLOCK),
            'brand': detected brand name,
            'count': count size for shrimp/scallops,
            'meat_grade': crab/lobster meat grade,
            'preparation': raw/cooked/smoked/cured,
            'value_added': breaded/stuffed/marinated/etc.
        }
        
    Example:
        >>> item = parse("POLLOCK FIL WILD ALASKA PROCESSED IN CHINA 6OZ")
        >>> print(item['origin_harvest'])
        'USA'
        >>> print(item['origin_processed'])
        'CHN'
        >>> print(item['freeze_cycle'])
        'TWICE'
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
        'size_bucket': None,
        'pack': None,
        'storage': None,
        'harvest': None,
        'origin': None,
        'origin_harvest': None,
        'origin_processed': None,
        'freeze_cycle': None,
        'cut_style': None,
        'brand': None,
        'count': None,
        'meat_grade': None,
        'preparation': None,
        'value_added': None
    }
    
    # Normalize text
    text = description.upper().strip()
    
    # Extract species
    species_info = _extract_species(text)
    if species_info:
        result.update(species_info)
    
    # Extract form
    result['form'] = _extract_attribute(text, 'form')
    
    # Extract skin status
    result['skin'] = _extract_attribute(text, 'skin')
    
    # Extract bone status
    result['bone'] = _extract_attribute(text, 'bone')
    
    # Extract trim level
    result['trim'] = _extract_attribute(text, 'trim')
    
    # Extract size
    result['size'] = _extract_size(text)
    
    # Assign size bucket for comparison matching
    result['size_bucket'] = _assign_size_bucket(result['size'])
    
    # Extract packaging
    result['pack'] = _extract_attribute(text, 'pack')
    
    # Extract storage
    result['storage'] = _extract_attribute(text, 'storage')
    
    # Extract harvest type
    result['harvest'] = _extract_attribute(text, 'harvest')
    
    # Extract origin (harvest + processing)
    origins = _extract_origins(text)
    result['origin_harvest'] = origins.get('harvest')
    result['origin_processed'] = origins.get('processed')
    # Legacy 'origin' field: harvest country if available, else first detected
    result['origin'] = result['origin_harvest'] or result['origin_processed']
    
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
    
    # Infer freeze cycle from processing country + category
    result['freeze_cycle'] = _infer_freeze_cycle(
        category=result.get('category'),
        origin_harvest=result.get('origin_harvest'),
        origin_processed=result.get('origin_processed'),
        storage=result.get('storage'),
    )
    
    return result


def parse_description(description: str) -> Dict[str, Any]:
    """
    Alias for parse() - for compatibility with different naming conventions.
    """
    return parse(description)


# =========================================================================
# ORIGIN EXTRACTION — harvest vs processing country
# =========================================================================

# Patterns that signal "processed in" / "packed in" (the PROCESSING country)
_PROCESSED_PATTERNS = [
    r'(?:PROCESSED|PROC|PACKED|PACKAGED|REPROCESSED|REPROC|CUT|PORTIONED|FILLETED)\s+(?:IN\s+)?',
    r'(?:PROC\s*[/]\s*)',       # PROC/CHINA
    r'(?:PROCESSED\s*[/]\s*)',  # PROCESSED/VIETNAM
    r'(?:PKD\s+(?:IN\s+)?)',    # PKD IN CHINA, PKD CHINA
]

# Patterns that signal "caught in" / "harvested in" / "product of" (the HARVEST country)
_HARVEST_PATTERNS = [
    r'(?:CAUGHT|HARVESTED|FARMED|FARM RAISED|WILD CAUGHT|FISHED|SOURCED|ORIGIN)\s+(?:IN\s+)?',
    r'(?:PRODUCT\s+OF\s+)',                    # PRODUCT OF NORWAY
    r'(?:FROM\s+)',                             # FROM ALASKA
    r'(?:WILD\s+)',                             # WILD ALASKA (harvest indicator)
    r'(?:IMPORTED\s+FROM\s+)',                  # IMPORTED FROM CHILE
]

# Combined pattern: "CAUGHT ... PROCESSED ..." or "PRODUCT OF X PROC Y"
_DUAL_ORIGIN_PATTERN = re.compile(
    r'(?:CAUGHT|HARVESTED|WILD CAUGHT|PRODUCT OF|WILD|FROM|FARMED IN|FARM RAISED IN)\s+(?:IN\s+)?'
    r'(\w[\w\s]*?)'  # harvest country
    r'\s*[,/;]\s*'    # separator
    r'(?:PROCESSED|PROC|PACKED|PACKAGED|CUT|PORTIONED|FILLETED)\s+(?:IN\s+)?'
    r'(\w[\w\s]*)',   # processing country
    re.IGNORECASE
)


def _extract_origins(text: str) -> Dict[str, Optional[str]]:
    """
    Extract harvest country and processing country from text.
    
    Detects patterns like:
      - "WILD ALASKA PROCESSED IN CHINA"
      - "PRODUCT OF USA, PROC/CHINA"  
      - "CAUGHT NORWAY PACKED VIETNAM"
      - "WILD CAUGHT USA PROC CHN"
      - "CHINA" (single origin, could be either)
      - "PRODUCT OF CHILE" (harvest)
      - "PROCESSED IN VIETNAM" (processing)
      
    Returns:
        Dict with 'harvest' and 'processed' keys, values are country codes or None.
    """
    text_upper = text.upper()
    result = {'harvest': None, 'processed': None}
    
    # --- Try dual-origin pattern first (most specific) ---
    dual = _DUAL_ORIGIN_PATTERN.search(text_upper)
    if dual:
        harvest_text = dual.group(1).strip()
        process_text = dual.group(2).strip()
        result['harvest'] = _match_country(harvest_text)
        result['processed'] = _match_country(process_text)
        if result['harvest'] or result['processed']:
            return result
    
    # --- Try explicit processing patterns ---
    for pat in _PROCESSED_PATTERNS:
        m = re.search(pat + r'(\w[\w\s]*?)(?:\s|$|,|/)', text_upper)
        if m:
            code = _match_country(m.group(1).strip())
            if code:
                result['processed'] = code
                break
    
    # --- Try explicit harvest patterns ---
    for pat in _HARVEST_PATTERNS:
        m = re.search(pat + r'(\w[\w\s]*?)(?:\s|$|,|/)', text_upper)
        if m:
            code = _match_country(m.group(1).strip())
            if code:
                # Don't overwrite if we already found it via dual pattern
                if not result['harvest']:
                    result['harvest'] = code
                break
    
    # --- Fallback: single country mention, no context clues ---
    # If we found a processing country but no harvest, or vice versa, 
    # leave the other as None (we don't know).
    # If we found NEITHER, do a simple origin_country lookup as legacy fallback.
    if not result['harvest'] and not result['processed']:
        legacy = _extract_attribute(text_upper, 'origin_country')
        if legacy:
            # No processing/harvest context — treat as harvest origin
            # (legacy behavior, most common meaning of "PRODUCT OF X")
            result['harvest'] = legacy
    
    return result


def _match_country(text: str) -> Optional[str]:
    """
    Match a text fragment to a country code from origin_country standards.
    """
    if not text or 'origin_country' not in STANDARD_CODES:
        return None
    
    text = text.strip().upper()
    
    # Direct code match
    if text in STANDARD_CODES['origin_country']:
        return text
    
    # Alias match — longest alias wins
    best_code = None
    best_len = 0
    for code, info in STANDARD_CODES['origin_country'].items():
        for alias in info.get('aliases', []):
            if alias == text or alias in text:
                if len(alias) > best_len:
                    best_code = code
                    best_len = len(alias)
    
    return best_code


# =========================================================================
# FREEZE CYCLE INFERENCE
# =========================================================================

def _infer_freeze_cycle(category: Optional[str], origin_harvest: Optional[str],
                        origin_processed: Optional[str], storage: Optional[str]) -> Optional[str]:
    """
    Infer single vs twice-frozen based on species category and processing country.
    
    Rules:
      1. Only applies to FINFISH categories (crustaceans/mollusks exempt)
      2. If origin_processed is an Asian processing country → TWICE
      3. If origin_processed matches origin_harvest (or is None) → SINGLE
      4. If we don't have enough data → None (unknown)
      
    The logic:
      - Wild Alaska Pollock caught in USA, processed in China = TWICE FROZEN
        (frozen on boat → shipped to China → thawed → filleted → refrozen)
      - Atlantic Salmon farmed in Norway, processed in Norway = SINGLE
      - Cod caught in Iceland, processed in Iceland = SINGLE
      - Tilapia farmed in China, processed in China = SINGLE (never left)
      
    Note: Fresh products (storage=FRSH) are not frozen at all, so freeze_cycle
    does not apply and returns None.
    """
    # No category? Can't determine
    if not category:
        return None
    
    category_lower = category.lower()
    
    # Exempt categories (crustaceans, mollusks, cephalopods)
    if category_lower in EXEMPT_CATEGORIES:
        return None
    
    # Only finfish
    if category_lower not in FINFISH_CATEGORIES:
        return None
    
    # Fresh product — not frozen, N/A
    if storage == 'FRSH':
        return None
    
    # If we have a processing country, check if it's a twice-frozen origin
    if origin_processed:
        if origin_processed in TWICE_FROZEN_PROCESSING_COUNTRIES:
            # Exception: if harvest AND processing are the same Asian country,
            # it's likely domestically farmed+processed = single frozen
            # e.g., Tilapia farmed in China, processed in China
            if origin_harvest and origin_harvest == origin_processed:
                return 'SINGLE'
            return 'TWICE'
        else:
            return 'SINGLE'
    
    # No processing country info — if we at least have harvest country,
    # we can't determine freeze cycle without knowing where it was processed
    # Exception: if harvest is itself an Asian processing country AND
    # the species is typically exported for processing (like pollock), 
    # we still can't assume — leave as None
    return None


# =========================================================================
# SPECIES EXTRACTION (unchanged from v0.3.0)
# =========================================================================

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
    category_plus_alias_matches = []
    category_only_matches = []
    
    for category, cat_data in SPECIES_DATA.items():
        # Handle underscored category names: sea_bass → "SEA BASS"
        cat_name = category.upper().replace('_', ' ')
        if cat_name not in text_upper:
            continue
        
        found_subspecies = False
        for subspec, spec_info in cat_data.get('species', {}).items():
            for alias in spec_info.get('aliases', []):
                if _alias_in_text(alias, text_upper):
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
                'species': category.replace('_', ' ').title(),
                'species_code': category.upper(),
                'category': category,
                'subspecies': None
            })
    
    if category_plus_alias_matches:
        best = max(category_plus_alias_matches, key=lambda m: m['_alias_len'])
        del best['_alias_len']
        return best
    
    # --- Priority 2: Category name present, no subspecies alias ---
    if category_only_matches:
        return category_only_matches[0]
    
    # --- Priority 3: Alias only, no category name in text ---
    alias_only_matches = []
    
    for category, cat_data in SPECIES_DATA.items():
        for subspec, spec_info in cat_data.get('species', {}).items():
            for alias in spec_info.get('aliases', []):
                if len(alias) >= 4 and _alias_in_text(alias, text_upper):
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


def _alias_in_text(alias: str, text_upper: str) -> bool:
    """
    Check if an alias appears in text with word boundary awareness.
    
    Short aliases (<=4 chars like 'SEA', 'ATL', 'RED') require word boundaries
    to avoid false matches. Longer aliases can match as substrings since they're
    specific enough (e.g., 'SABLEFISH', 'CHILEAN SEA BASS').
    """
    if len(alias) <= 4:
        # Require word boundaries for short aliases
        pattern = r'(?:^|[\s/\-_,])' + re.escape(alias) + r'(?:$|[\s/\-_,])'
        return bool(re.search(pattern, text_upper))
    else:
        return alias in text_upper


def _extract_attribute(text: str, category: str) -> Optional[str]:
    """
    Extract a standardized attribute from text.
    """
    if category not in STANDARD_CODES:
        return None
    
    text_upper = text.upper()
    
    matches = []
    for code, info in STANDARD_CODES[category].items():
        for alias in info.get('aliases', []):
            pattern = r'(?:^|[\s/\-_,])' + re.escape(alias) + r'(?:$|[\s/\-_,])'
            if re.search(pattern, text_upper) or text_upper == alias:
                matches.append((len(alias), code, alias))
    
    if matches:
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
    
    oz_patterns = [
        r'(\d+(?:\.\d+)?)\s*-\s*(\d+(?:\.\d+)?)\s*(?:OZ|OUNCE)',
        r'(\d+(?:\.\d+)?)\s*(?:OZ|OUNCE)',
    ]
    
    for pattern in oz_patterns:
        match = re.search(pattern, text_upper)
        if match:
            if len(match.groups()) == 2:
                return f"{match.group(1)}-{match.group(2)}OZ"
            else:
                return f"{match.group(1)}OZ"
    
    lb_patterns = [
        r'(\d+(?:\.\d+)?)\s*-\s*(\d+(?:\.\d+)?)\s*(?:LB|#|POUND)',
        r'(\d+(?:\.\d+)?)\s*(?:LB|#|POUND)',
    ]
    
    for pattern in lb_patterns:
        match = re.search(pattern, text_upper)
        if match:
            if len(match.groups()) == 2:
                return f"{match.group(1)}-{match.group(2)}LB"
            else:
                return f"{match.group(1)}LB"
    
    return None


# =========================================================================
# SIZE BUCKET ASSIGNMENT
# =========================================================================

# Ounce buckets: lower bound is INCLUSIVE
# A 2oz portion competes with 2-3oz, not 1-2oz
OZ_BUCKETS = [
    (1, 2, '1-2OZ'),
    (2, 3, '2-3OZ'),
    (3, 4, '3-4OZ'),
    (4, 5, '4-5OZ'),
    (5, 6, '5-6OZ'),
    (6, 8, '6-8OZ'),
    (8, 10, '8-10OZ'),
    (10, 12, '10-12OZ'),
    (12, 16, '12-16OZ'),
    (16, 999, '16OZ+'),
]

# Pound buckets
LB_BUCKETS = [
    (0, 1, 'UNDER-1LB'),
    (1, 2, '1-2LB'),
    (2, 3, '2-3LB'),
    (3, 4, '3-4LB'),
    (4, 5, '4-5LB'),
    (5, 7, '5-7LB'),
    (7, 9, '7-9LB'),
    (9, 999, '9LB+'),
]


def _assign_size_bucket(size_str: Optional[str]) -> Optional[str]:
    """
    Assign a standardized size bucket for comparison matching.
    
    Converts exact sizes and ranges into standard competitive buckets
    so that "2OZ" and "2-3OZ" land in the same bucket.
    
    For ranges (e.g., "2-3OZ"), uses the midpoint to assign the bucket.
    For exact sizes (e.g., "8OZ"), uses the value directly.
    
    Args:
        size_str: Standardized size string from _extract_size (e.g., "6OZ", "2-3OZ", "3-4LB")
        
    Returns:
        Bucket string (e.g., "6-8OZ", "2-3OZ", "3-4LB") or None
        
    Examples:
        "2OZ"    → "2-3OZ"
        "2-3OZ"  → "2-3OZ"
        "8OZ"    → "8-10OZ"
        "5-7OZ"  → "6-8OZ"  (midpoint=6)
        "3-4LB"  → "3-4LB"
        "3LB"    → "3-4LB"
    """
    if not size_str:
        return None
    
    size_upper = size_str.upper().strip()
    
    # Determine unit and extract numeric value(s)
    if 'OZ' in size_upper:
        buckets = OZ_BUCKETS
        num_str = size_upper.replace('OZ', '').strip()
    elif 'LB' in size_upper:
        buckets = LB_BUCKETS
        num_str = size_upper.replace('LB', '').strip()
    else:
        return None
    
    # Parse value: range (e.g., "2-3") or exact (e.g., "8")
    try:
        if '-' in num_str:
            parts = num_str.split('-')
            low = float(parts[0])
            high = float(parts[1])
            value = (low + high) / 2  # midpoint
        else:
            value = float(num_str)
    except (ValueError, IndexError):
        return None
    
    # Find matching bucket (lower bound inclusive)
    for lower, upper, label in buckets:
        if lower <= value < upper:
            return label
    
    return None


def _extract_count(text: str) -> Optional[str]:
    """
    Extract count size (for shrimp, scallops).
    
    Handles:
    - "16/20", "21/25", "U10", "U/10"
    - "16-20 ct", "21-25 count"
    """
    text_upper = text.upper()
    
    u_match = re.search(r'U[/-]?(\d+)', text_upper)
    if u_match:
        return f"U{u_match.group(1)}"
    
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
        Dict with: species, form, skin, bone, size, trim, freeze_cycle, etc.
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
        'freeze_cycle': result.get('freeze_cycle'),
    }
