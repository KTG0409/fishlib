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
    
    Args:
        description: The item description to parse
                    e.g., "SALMON FIL ATL SKON DTRM 6OZ IVP"
                    
    Returns:
        Dictionary with extracted attributes.
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
    
    # Pre-process: split common smashed-together codes
    expanded = _expand_smashed_codes(text)
    
    # Extract species
    species_info = _extract_species(text)
    if species_info:
        result.update(species_info)
    
    # Extract form (with TAIL ON/OFF protection)
    result['form'] = _extract_form(expanded)
    
    # Extract shrimp-specific form (P&D, PUD, SHELL ON, EZ PEEL, etc.)
    result['shrimp_form'] = _extract_shrimp_form(expanded)
    
    # Extract skin status
    result['skin'] = _extract_attribute(expanded, 'skin')
    
    # Extract bone status
    result['bone'] = _extract_attribute(expanded, 'bone')
    
    # Extract trim level
    result['trim'] = _extract_attribute(expanded, 'trim')
    
    # Extract size
    result['size'] = _extract_size(text)
    
    # Extract packaging
    result['pack'] = _extract_attribute(expanded, 'pack')
    
    # Extract storage
    result['storage'] = _extract_attribute(expanded, 'storage')
    
    # Extract harvest type
    result['harvest'] = _extract_attribute(expanded, 'harvest')
    
    # Extract origin
    result['origin'] = _extract_attribute(expanded, 'origin_country')
    
    # Extract cut style
    result['cut_style'] = _extract_attribute(expanded, 'cut_style')
    
    # Extract count (for shrimp, scallops)
    result['count'] = _extract_count(text)
    
    # Extract brand
    result['brand'] = _extract_brand(text)
    
    # Extract meat grade (with LUMPFISH protection)
    result['meat_grade'] = _extract_meat_grade(expanded, text)
    
    # Extract preparation (raw, cooked, smoked, cured)
    result['preparation'] = _extract_attribute(expanded, 'preparation')
    
    # Extract value-added (breaded, stuffed, marinated, etc.)
    result['value_added'] = _extract_attribute(expanded, 'value_added')
    
    return result


def parse_description(description: str) -> Dict[str, Any]:
    """Alias for parse() - for compatibility."""
    return parse(description)


def _expand_smashed_codes(text: str) -> str:
    """
    Expand common smashed-together abbreviations found in real data.
    
    Examples:
        '4-5LBSKONCAN' -> '4-5LB SKON CAN'
        'BNLSKL'       -> 'BNLS SKL'
        'BNLSSKLS'     -> 'BNLS SKLS'
        'SKLSBNLS'     -> 'SKLS BNLS'
        'CKD100/150'   -> 'CKD 100/150'
    """
    t = text
    
    # Size units smashed to skin codes (4-5LBSKON -> 4-5LB SKON)
    t = re.sub(r'(LB|OZ|#)(SKON|SKLS|SKOFF)', r'\1 \2', t)
    
    # Skin+Bone combos (order matters - longer first)
    t = re.sub(r'BNLSSKLS', 'BNLS SKLS', t)
    t = re.sub(r'BNLSKLSS', 'BNLS SKLS', t)
    t = re.sub(r'BNLSKLS', 'BNLS SKLS', t)
    t = re.sub(r'BNLSKL\b', 'BNLS SKL', t)
    t = re.sub(r'SKLSBNLS', 'SKLS BNLS', t)
    t = re.sub(r'SKONCAN', 'SKON CAN', t)
    t = re.sub(r'SKOFFE', 'SKOFF E', t)
    
    # Skin smashed to following text (FILSKON, #1SKON)
    t = re.sub(r'(?<=\w)(SKON|SKLS|SKOFF)(?=\w)', r' \1 ', t)
    t = re.sub(r'(?<=\d)(SKON|SKLS|SKOFF)', r' \1', t)
    
    # Bone smashed to following text
    t = re.sub(r'(?<=\w)(BNLS|PBO)(?=[A-Z])', r' \1 ', t)
    
    # CKD/PRCKD smashed to counts
    t = re.sub(r'(CKD|PRCKD)(\d)', r'\1 \2', t)
    
    # Size smashed to following text
    t = re.sub(r'(\w)(\d+-\d+)\s*Z\b', r'\1 \2OZ', t)
    
    # FRZNN typo
    t = re.sub(r'FRZNN', 'FRZN', t)
    
    # B/LES -> BNLS
    t = re.sub(r'B/LES\b', 'BNLS', t)
    
    # Clean up double spaces
    t = re.sub(r'\s+', ' ', t).strip()
    
    return t


def _extract_species(text: str) -> Optional[Dict[str, Any]]:
    """
    Extract species information from text.
    
    Uses a priority system to avoid alias collisions:
      1. Category name in text + subspecies alias match (strongest)
      2. Category name in text, no subspecies match (category-level)
      3. Subspecies alias only, no category name (fallback)
    
    Within each priority level, longer alias matches win.
    """
    text_upper = text.upper()
    
    category_plus_alias_matches = []
    category_only_matches = []
    
    for category, cat_data in SPECIES_DATA.items():
        # Normalize category name for matching (orange_roughy -> ORANGE ROUGHY)
        cat_name = category.upper().replace('_', ' ')
        if cat_name not in text_upper:
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
                'species': category.replace('_', ' ').title(),
                'species_code': category.upper(),
                'category': category,
                'subspecies': None
            })
    
    if category_plus_alias_matches:
        best = max(category_plus_alias_matches, key=lambda m: m['_alias_len'])
        del best['_alias_len']
        return best
    
    if category_only_matches:
        return category_only_matches[0]
    
    # Priority 3: Alias only, no category name in text
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
    """
    text_upper = text.upper()
    
    if 'form' not in STANDARD_CODES:
        return None
    
    matches = []
    for code, info in STANDARD_CODES['form'].items():
        for alias in info.get('aliases', []):
            pattern = r'(?:^|[\s/\-_,])' + re.escape(alias) + r'(?:$|[\s/\-_,])'
            if re.search(pattern, text_upper) or text_upper == alias:
                if code == 'TAIL':
                    tail_on_off = re.search(r'(?:^|[\s/\-_,])TAIL\s*(?:ON|OFF)(?:$|[\s/\-_,])', text_upper)
                    if tail_on_off:
                        continue
                matches.append((len(alias), code, alias))
    
    if matches:
        matches.sort(reverse=True, key=lambda x: x[0])
        return matches[0][1]
    
    return None


def _extract_shrimp_form(text: str) -> Optional[str]:
    """
    Extract shrimp-specific processing form.
    """
    text_upper = text.upper()
    
    SHRIMP_FORMS = {
        'P&D': [r'P\s*&\s*D', r'P/D', r'PD(?!\w)', r'PEELED\s+(?:&\s+)?DEVEINED'],
        'PUD': [r'PUD', r'P/UD', r'PEELED\s+UNDEVEINED'],
        'SHELL_ON': [r'SHELL\s*ON', r'SHL\s*ON', r'S/ON', r'HEAD\s*OFF\s*SHELL\s*ON', r'HOSO'],
        'TAIL_ON': [r'TAIL\s*ON', r'T/ON', r'EZ\s*PEEL', r'EZPEEL', r'TAILON'],
        'TAIL_OFF': [r'TAIL\s*OFF', r'T/OFF', r'TAILLESS', r'TLOF', r'TAILOFF'],
        'HEAD_ON': [r'HEAD\s*ON', r'H/ON', r'HOON', r'HDON'],
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
    """Extract a standardized attribute from text."""
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


def _extract_meat_grade(expanded_text: str, original_text: str) -> Optional[str]:
    """
    Extract meat grade with protection against false positives.
    
    'LUMPFISH' is a species name, not meat grade 'LUMP'.
    """
    text_upper = original_text.upper()
    
    if 'LUMPFISH' in text_upper:
        if 'meat_grade' not in STANDARD_CODES:
            return None
        matches = []
        for code, info in STANDARD_CODES['meat_grade'].items():
            if code == 'LUMP':
                continue
            for alias in info.get('aliases', []):
                if 'LUMP' in alias and 'JUMBO' not in alias:
                    continue
                pattern = r'(?:^|[\s/\-_,])' + re.escape(alias) + r'(?:$|[\s/\-_,])'
                if re.search(pattern, expanded_text.upper()) or expanded_text.upper() == alias:
                    matches.append((len(alias), code, alias))
        if matches:
            matches.sort(reverse=True, key=lambda x: x[0])
            return matches[0][1]
        return None
    
    return _extract_attribute(expanded_text, 'meat_grade')


def _extract_size(text: str) -> Optional[str]:
    """Extract size specification from text."""
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


def _extract_count(text: str) -> Optional[str]:
    """Extract count size (for shrimp, scallops)."""
    text_upper = text.upper()
    
    u_match = re.search(r'U[/-]?(\d+)', text_upper)
    if u_match:
        return f"U{u_match.group(1)}"
    
    count_match = re.search(r'(\d+)\s*[/-]\s*(\d+)(?:\s*CT|\s*COUNT)?', text_upper)
    if count_match:
        return f"{count_match.group(1)}/{count_match.group(2)}"
    
    return None


def _extract_brand(text: str) -> Optional[str]:
    """Extract brand name from common foodservice brands."""
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
    """Parse multiple descriptions at once."""
    return [parse(desc) for desc in descriptions]


def extract_key_attributes(description: str) -> Dict[str, str]:
    """Extract only the key attributes needed for matching."""
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
