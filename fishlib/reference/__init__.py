"""
Reference data module for fishlib.

Contains industry-standard definitions for:
- Trim levels (A-E)
- Cut styles (center cut, bias, block, etc.)
- Forms (fillet, portion, loin, etc.)
- Skin/bone codes
- Pack styles
- Price tiers

This information codifies fish industry knowledge so that anyone
can understand product attributes without being a fish expert.
"""

# =============================================================================
# TRIM LEVELS (Salmon specific, but applies to similar finfish)
# =============================================================================
TRIM_LEVELS = {
    'A': {
        'name': 'Trim A',
        'description': 'Backbone off, bellybone off',
        'skin': 'on',
        'removed': ['backbone', 'bellybone'],
        'remaining': ['backfin', 'collarbone', 'belly fat', 'belly fins', 'pin bones', 'skin', 'nape', 'tail piece'],
        'foodservice_common': False,
        'typical_use': 'Retail, specialty',
        'relative_price': 'mid-high'
    },
    'B': {
        'name': 'Trim B',
        'description': 'A + backfin off, collarbone off, belly fat off, belly fins off',
        'skin': 'on',
        'removed': ['backbone', 'bellybone', 'backfin', 'collarbone', 'belly fat', 'belly fins'],
        'remaining': ['pin bones', 'skin', 'nape', 'tail piece'],
        'foodservice_common': False,
        'typical_use': 'Retail',
        'relative_price': 'mid'
    },
    'C': {
        'name': 'Trim C',
        'description': 'B + pin bone out',
        'skin': 'on',
        'removed': ['backbone', 'bellybone', 'backfin', 'collarbone', 'belly fat', 'belly fins', 'pin bones'],
        'remaining': ['skin', 'nape', 'tail piece'],
        'foodservice_common': False,
        'typical_use': 'Retail, some foodservice',
        'relative_price': 'mid'
    },
    'D': {
        'name': 'Trim D',
        'description': 'C + back trimmed, tailpiece off, belly membrane off, nape trimmed. FOODSERVICE STANDARD.',
        'skin': 'on',
        'removed': ['backbone', 'bellybone', 'backfin', 'collarbone', 'belly fat', 'belly fins', 'pin bones', 'tail piece', 'belly membrane', 'back fat', 'nape excess'],
        'remaining': ['skin'],
        'foodservice_common': True,
        'typical_use': 'Foodservice - most common for skin-on products',
        'relative_price': 'mid-low'
    },
    'E': {
        'name': 'Trim E', 
        'description': 'D + skin off. Most fully trimmed. FOODSERVICE PREMIUM.',
        'skin': 'off',
        'removed': ['backbone', 'bellybone', 'backfin', 'collarbone', 'belly fat', 'belly fins', 'pin bones', 'tail piece', 'belly membrane', 'back fat', 'nape excess', 'skin'],
        'remaining': [],
        'foodservice_common': True,
        'typical_use': 'Foodservice - premium boneless skinless',
        'relative_price': 'high'
    },
    'FTRIM': {
        'name': 'Full Trim',
        'description': 'Fully trimmed - typically equivalent to Trim E',
        'skin': 'typically off',
        'removed': ['all trim components'],
        'remaining': [],
        'foodservice_common': True,
        'typical_use': 'Foodservice',
        'relative_price': 'high'
    }
}

# Key insight about trim levels
TRIM_KEY_INSIGHT = """
CRITICAL: Trim A through D are ALL SKIN ON. Only Trim E is SKIN OFF.

Foodservice primarily uses:
- Trim D (skin on, fully trimmed) 
- Trim E (skin off, fully trimmed)

Trim A, B, C are more common in retail.

When comparing prices, Trim D vs Trim E represents a significant 
price difference due to skin removal labor.
"""


# =============================================================================
# CUT STYLES (for portions)
# =============================================================================
CUT_STYLES = {
    'CENTER': {
        'name': 'Center Cut',
        'description': 'Portions cut from the center of the fish only. No tail or nape pieces.',
        'characteristics': ['Uniform thickness', 'Consistent shape', 'Best plate presentation'],
        'excludes': ['tail pieces', 'nape pieces', 'collar area'],
        'premium': True,
        'labor_intensity': 'high',
        'relative_price_impact': 'premium over block cut',
        'foodservice_use': 'Fine dining, consistent portion control'
    },
    'BIAS': {
        'name': 'Bias Cut',
        'description': 'Cut at an angle (diagonal) rather than straight across.',
        'characteristics': ['Appears larger on plate', 'Better presentation', 'More surface area'],
        'premium': True,
        'labor_intensity': 'high',
        'relative_price_impact': 'premium over straight cut',
        'foodservice_use': 'Upscale casual, fine dining'
    },
    'BLOCK': {
        'name': 'Block Cut',
        'description': 'Straight cuts through the entire fillet, end to end.',
        'characteristics': ['Includes tail pieces', 'Variable thickness', 'Rectangular shape'],
        'includes': ['tail pieces', 'nape pieces', 'variable shapes'],
        'premium': False,
        'labor_intensity': 'low',
        'relative_price_impact': 'baseline',
        'foodservice_use': 'Casual dining, high volume'
    },
    'RANDOM': {
        'name': 'Random/Irregular',
        'description': 'Mixed pieces of various shapes and sizes.',
        'characteristics': ['Variable shapes', 'May include trim pieces', 'Inconsistent'],
        'premium': False,
        'labor_intensity': 'minimal',
        'relative_price_impact': 'discount vs block cut',
        'foodservice_use': 'Buffet, fish tacos, stir fry, soups'
    }
}

CUT_STYLE_KEY_INSIGHT = """
WHY LABOR MATTERS FOR PRICE:

More precision = More labor = Higher price

Center-cut bias portions cost more because:
1. Skilled cutting at angles
2. Only center pieces used (tails/nape go elsewhere as lower-value products)
3. Consistency requires inspection and sorting

When Circana shows two '6oz salmon portions' at different prices, 
the difference is often cut style - not overpricing.
"""


# =============================================================================
# FORMS
# =============================================================================
FORMS = {
    'FIL': {
        'name': 'Fillet',
        'description': 'Boneless piece cut from the side of the fish',
        'typical_sizes': 'Sold by weight range (2-3#, 3-4#, etc.)',
        'requires': ['trim level', 'skin status'],
        'common_species': ['salmon', 'cod', 'tilapia', 'catfish', 'mahi']
    },
    'PRTN': {
        'name': 'Portion',
        'description': 'Pre-cut piece to exact weight for portion control',
        'typical_sizes': '3oz, 4oz, 5oz, 6oz, 7oz, 8oz, 10oz',
        'requires': ['cut style', 'trim level', 'skin status'],
        'common_species': ['salmon', 'cod', 'mahi', 'tilapia'],
        'note': 'Circana often misclassifies portions as fillets - major PMI gap'
    },
    'LOIN': {
        'name': 'Loin',
        'description': 'Premium center cut from the thickest part of the fillet',
        'characteristics': ['Highest yield', 'Most uniform', 'Premium price'],
        'common_species': ['salmon', 'tuna', 'swordfish', 'mahi']
    },
    'WHL': {
        'name': 'Whole',
        'description': 'Whole fish, may be head on or head off',
        'variants': ['round (as caught)', 'gutted', 'scaled', 'H&G'],
        'common_species': ['branzino', 'trout', 'snapper', 'lobster', 'crab']
    },
    'STEAK': {
        'name': 'Steak',
        'description': 'Cross-section cut through the fish, includes bone',
        'characteristics': ['Bone-in', 'Round shape', 'Good for grilling'],
        'common_species': ['salmon', 'swordfish', 'halibut', 'tuna']
    },
    'H&G': {
        'name': 'Headed & Gutted',
        'description': 'Whole fish with head and viscera removed',
        'common_species': ['salmon', 'cod', 'snapper']
    },
    'TAIL': {
        'name': 'Tail',
        'description': 'Tail section only',
        'common_species': ['lobster', 'monkfish'],
        'note': 'For lobster, this is the primary edible portion sold'
    },
    'CLUSTER': {
        'name': 'Cluster',
        'description': 'Section of legs/claws still connected to body section',
        'common_species': ['crab (snow, king)']
    },
    'MEAT': {
        'name': 'Meat/Picked',
        'description': 'Extracted meat, shell removed',
        'grades': ['jumbo lump', 'lump', 'backfin', 'claw', 'special'],
        'common_species': ['crab', 'lobster']
    }
}


# =============================================================================
# SKIN CODES
# =============================================================================
SKIN_CODES = {
    'SKON': {
        'name': 'Skin On',
        'description': 'Skin intact on the product',
        'trim_implication': 'For salmon: Trim A, B, C, or D',
        'cooking_note': 'Skin helps hold shape during cooking, can be crisped'
    },
    'SKLS': {
        'name': 'Skinless',
        'description': 'Skin has been removed',
        'trim_implication': 'For salmon: Trim E',
        'cooking_note': 'Faster cooking, no skin to remove at service'
    },
    'SKOFF': {
        'name': 'Skin Off',
        'description': 'Same as skinless - skin has been removed',
        'trim_implication': 'For salmon: Trim E',
        'note': 'SKOFF and SKLS are equivalent'
    }
}


# =============================================================================
# BONE CODES
# =============================================================================
BONE_CODES = {
    'BNLS': {
        'name': 'Boneless',
        'description': 'All bones removed',
        'note': 'Standard for foodservice fillets and portions'
    },
    'BIN': {
        'name': 'Bone In',
        'description': 'Bones present (e.g., steaks, whole fish)',
        'common_uses': ['steaks', 'whole fish', 'bone-in chops']
    },
    'PBO': {
        'name': 'Pin Bone Out',
        'description': 'Pin bones specifically removed',
        'note': 'Pin bones are the small intramuscular bones in fillets',
        'common_species': ['salmon', 'trout', 'herring']
    }
}


# =============================================================================
# PACK STYLES
# =============================================================================
PACK_STYLES = {
    'IVP': {
        'name': 'Individually Vacuum Packed',
        'description': 'Each piece vacuum sealed separately',
        'benefits': ['Longer shelf life', 'No freezer burn', 'Easy portioning'],
        'typical_users': 'Foodservice, retail premium'
    },
    'IQF': {
        'name': 'Individually Quick Frozen',
        'description': 'Each piece frozen separately, not stuck together',
        'benefits': ['Easy to separate', 'Use only what you need', 'Maintains quality'],
        'typical_users': 'High volume foodservice'
    },
    'CVP': {
        'name': 'Controlled Vacuum Pack',
        'description': 'Vacuum packed with controlled atmosphere',
        'benefits': ['Extended fresh shelf life', 'No freezing needed'],
        'typical_users': 'Fresh seafood programs'
    },
    'BULK': {
        'name': 'Bulk Pack',
        'description': 'Multiple pieces packed together, may be layer packed',
        'note': 'Lower cost, but pieces may stick together when frozen',
        'typical_users': 'High volume, cost-sensitive'
    },
    'SHL': {
        'name': 'Shatter Pack',
        'description': 'Frozen block that can be broken apart',
        'common_species': ['shrimp', 'small fish'],
        'typical_users': 'High volume operations'
    }
}


# =============================================================================
# PRICE TIERS
# =============================================================================
PRICE_TIERS = {
    'ultra-premium': {
        'description': 'Highest price tier, specialty/luxury items',
        'examples': ['king salmon', 'bluefin tuna', 'king crab', 'stone crab', 'dover sole'],
        'relative_position': 'significantly above mid-tier'
    },
    'premium': {
        'description': 'High quality, above-average pricing',
        'examples': ['sockeye salmon', 'halibut', 'sea bass', 'diver scallops', 'maine lobster'],
        'relative_position': 'above mid-tier'
    },
    'mid': {
        'description': 'Standard foodservice quality',
        'examples': ['atlantic salmon', 'cod', 'mahi', 'snow crab', 'white shrimp'],
        'relative_position': 'baseline'
    },
    'value': {
        'description': 'Cost-effective options',
        'examples': ['keta salmon', 'pollock', 'swai', 'calico scallops', 'jonah crab'],
        'relative_position': 'below mid-tier'
    },
    'economy': {
        'description': 'Lowest cost tier',
        'examples': ['pink salmon', 'tilapia', 'imitation crab'],
        'relative_position': 'significantly below mid-tier'
    }
}


# =============================================================================
# MEAT GRADES (Crab, Lobster)
# =============================================================================
MEAT_GRADES = {
    'JUMBO_LUMP': {
        'name': 'Jumbo Lump',
        'description': 'Largest pieces from the two large muscles connected to swimming legs',
        'characteristics': ['Largest pieces', 'Most visually impressive', 'Minimal shell fragments'],
        'premium': True,
        'typical_use': 'Crab cakes, elegant presentations, garnish',
        'relative_price': 'highest'
    },
    'LUMP': {
        'name': 'Lump',
        'description': 'Broken pieces of jumbo lump and large flakes from body',
        'characteristics': ['Large pieces', 'Good texture', 'Some shell possible'],
        'premium': True,
        'typical_use': 'Crab cakes, salads, stuffings',
        'relative_price': 'high'
    },
    'BACKFIN': {
        'name': 'Backfin',
        'description': 'Smaller pieces of lump mixed with body meat flakes',
        'characteristics': ['Mixed sizes', 'Good flavor', 'More shell fragments'],
        'premium': False,
        'typical_use': 'Crab cakes, dips, casseroles',
        'relative_price': 'mid'
    },
    'SPECIAL': {
        'name': 'Special/Flake',
        'description': 'Small flakes of white body meat',
        'characteristics': ['Small pieces', 'Good for mixing', 'Most shell fragments'],
        'premium': False,
        'typical_use': 'Soups, dips, crab imperial, stuffings',
        'relative_price': 'value'
    },
    'CLAW': {
        'name': 'Claw Meat',
        'description': 'Meat from the claws, darker color, stronger flavor',
        'characteristics': ['Brownish color', 'Stronger flavor', 'Firmer texture'],
        'premium': False,
        'typical_use': 'Soups, dips, crab cakes where color not critical',
        'relative_price': 'value'
    },
    'COCKTAIL_CLAW': {
        'name': 'Cocktail Claw',
        'description': 'Whole claw with shell scored for easy eating',
        'characteristics': ['Shell partially attached', 'Ready to serve', 'Presentation item'],
        'premium': True,
        'typical_use': 'Appetizers, cocktail service, buffets',
        'relative_price': 'mid-high'
    }
}

MEAT_GRADE_KEY_INSIGHT = """
CRAB MEAT GRADE = HUGE PRICE DRIVER

Jumbo lump can be 3-4x the price of claw meat for the same species.
When comparing crab prices, meat grade is as important as species.

Grade hierarchy (highest to lowest value):
1. Jumbo Lump - premium presentations
2. Lump - crab cakes, salads
3. Backfin - mixed applications
4. Special/Flake - soups, dips
5. Claw - strongest flavor, lowest price

A "crab meat" comparison without grade is meaningless.
"""


# =============================================================================
# PREPARATION (Raw vs Cooked vs Smoked)
# =============================================================================
PREPARATION = {
    'RAW': {
        'name': 'Raw',
        'description': 'Uncooked product, requires cooking before consumption',
        'characteristics': ['Needs cooking', 'Longer shelf life frozen', 'Full cooking flexibility'],
        'typical_species': ['shrimp', 'salmon', 'cod', 'lobster tails'],
        'relative_price': 'baseline'
    },
    'COOKED': {
        'name': 'Cooked',
        'description': 'Fully cooked, ready to eat or heat-and-serve',
        'characteristics': ['Ready to eat', 'Shorter shelf life', 'Less cooking flexibility'],
        'typical_species': ['shrimp', 'crab', 'lobster', 'crawfish'],
        'relative_price': 'premium over raw'
    },
    'SMOKED': {
        'name': 'Smoked',
        'description': 'Cured and smoked, distinctive flavor profile',
        'characteristics': ['Distinctive flavor', 'Extended shelf life', 'Ready to eat'],
        'variants': ['cold smoked', 'hot smoked', 'kippered'],
        'typical_species': ['salmon', 'trout', 'whitefish', 'mackerel'],
        'relative_price': 'premium'
    },
    'CURED': {
        'name': 'Cured',
        'description': 'Salt/sugar cured without smoking',
        'characteristics': ['Silky texture', 'No smoke flavor', 'Ready to eat'],
        'variants': ['gravlax', 'lox', 'nova'],
        'typical_species': ['salmon'],
        'relative_price': 'premium'
    }
}

PREPARATION_KEY_INSIGHT = """
RAW vs COOKED = DIFFERENT PRODUCTS

Cooked shrimp costs more than raw due to:
1. Labor (cooking, handling)
2. Yield loss (shrinkage during cooking)
3. Additional processing/QC

When comparing shrimp prices, ALWAYS check preparation.
"16/20 P&D" raw vs cooked can differ by 20-30%.

Smoked/cured products are specialty items with very different
pricing than their raw counterparts.
"""


# =============================================================================
# VALUE-ADDED PROCESSING
# =============================================================================
VALUE_ADDED = {
    'BREADED': {
        'name': 'Breaded/Battered',
        'description': 'Coated with breading or batter for frying',
        'characteristics': ['Ready to fry', 'Standardized portions', 'Extended shelf life'],
        'variants': ['breaded', 'panko crusted', 'beer battered', 'tempura'],
        'typical_species': ['shrimp', 'cod', 'catfish', 'calamari'],
        'relative_price': 'varies - can be premium or value depending on product'
    },
    'STUFFED': {
        'name': 'Stuffed',
        'description': 'Filled with stuffing (often crab or seafood blend)',
        'characteristics': ['Premium presentation', 'Labor intensive', 'Complete entree'],
        'typical_products': ['stuffed shrimp', 'stuffed flounder', 'stuffed lobster tail'],
        'relative_price': 'premium'
    },
    'MARINATED': {
        'name': 'Marinated/Seasoned',
        'description': 'Pre-seasoned or marinated for flavor',
        'characteristics': ['Flavor-enhanced', 'Ready to cook', 'Reduced prep time'],
        'variants': ['teriyaki', 'garlic butter', 'cajun', 'herb', 'citrus'],
        'typical_species': ['salmon', 'shrimp', 'mahi'],
        'relative_price': 'slight premium'
    },
    'GLAZED': {
        'name': 'Glazed',
        'description': 'Coated with glaze (often Asian-inspired)',
        'characteristics': ['Sweet/savory coating', 'Ready to cook', 'Caramelizes when cooked'],
        'variants': ['miso glazed', 'teriyaki glazed', 'honey glazed'],
        'typical_species': ['salmon', 'cod', 'sea bass'],
        'relative_price': 'premium'
    },
    'BLACKENED': {
        'name': 'Blackened',
        'description': 'Coated with Cajun/blackening spice blend',
        'characteristics': ['Spiced coating', 'Cajun style', 'Ready to sear'],
        'typical_species': ['catfish', 'mahi', 'redfish', 'salmon'],
        'relative_price': 'slight premium'
    },
    'FORMED': {
        'name': 'Formed/Shaped',
        'description': 'Ground or minced seafood shaped into patties or cakes',
        'characteristics': ['Portion controlled', 'Uses trim/lesser pieces', 'Consistent shape'],
        'variants': ['crab cakes', 'salmon burgers', 'fish cakes', 'shrimp patties'],
        'typical_species': ['crab', 'salmon', 'cod', 'shrimp'],
        'relative_price': 'varies widely'
    }
}

VALUE_ADDED_KEY_INSIGHT = """
VALUE-ADDED = COMPLETELY DIFFERENT PRODUCT CLASS

Breaded cod portion vs plain cod portion are not comparable.
Value-added products include labor, ingredients, and R&D costs.

When analyzing PMI or market data:
- Separate value-added from plain/raw items
- Don't mix breaded with unbreaded
- Stuffed/marinated are specialty, not commodity

A "salmon portion" in Circana could be plain OR teriyaki-glazed.
Without identifying value-added processing, comparisons are invalid.
"""


# =============================================================================
# SPECIES DATA (loaded from JSON but key facts here)
# =============================================================================
import json
import os

_DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')
_SPECIES_FILE = os.path.join(_DATA_DIR, 'species_aliases.json')

try:
    with open(_SPECIES_FILE, 'r') as f:
        SPECIES_DATA = json.load(f)
except FileNotFoundError:
    SPECIES_DATA = {}


def get_trim_info(level: str) -> dict:
    """Get information about a trim level."""
    return TRIM_LEVELS.get(level.upper(), {})


def get_cut_style_info(style: str) -> dict:
    """Get information about a cut style."""
    return CUT_STYLES.get(style.upper(), {})


def get_form_info(form: str) -> dict:
    """Get information about a form type."""
    return FORMS.get(form.upper(), {})


def is_trim_skin_on(level: str) -> bool:
    """Check if a trim level is skin-on."""
    info = TRIM_LEVELS.get(level.upper(), {})
    return info.get('skin', '').lower() == 'on'


def is_foodservice_trim(level: str) -> bool:
    """Check if a trim level is common in foodservice."""
    info = TRIM_LEVELS.get(level.upper(), {})
    return info.get('foodservice_common', False)


def explain_price_difference(attr1: dict, attr2: dict) -> str:
    """
    Explain why two products might have different prices based on attributes.
    
    Args:
        attr1: First product attributes
        attr2: Second product attributes
        
    Returns:
        Human-readable explanation of price difference factors
    """
    factors = []
    
    # Check trim
    t1 = attr1.get('trim')
    t2 = attr2.get('trim')
    if t1 and t2 and t1 != t2:
        factors.append(f"Trim level: {t1} vs {t2} - different processing levels")
    
    # Check cut style
    c1 = attr1.get('cut_style')
    c2 = attr2.get('cut_style')
    if c1 and c2 and c1 != c2:
        info1 = CUT_STYLES.get(c1, {})
        info2 = CUT_STYLES.get(c2, {})
        if info1.get('premium') != info2.get('premium'):
            factors.append(f"Cut style: {c1} vs {c2} - different labor/precision")
    
    # Check subspecies
    s1 = attr1.get('subspecies')
    s2 = attr2.get('subspecies')
    if s1 and s2 and s1 != s2:
        factors.append(f"Species/variety: {s1} vs {s2} - different market value")
    
    # Check harvest
    h1 = attr1.get('harvest')
    h2 = attr2.get('harvest')
    if h1 and h2 and h1 != h2:
        factors.append(f"Harvest: {h1} vs {h2} - wild typically premium over farmed")
    
    if factors:
        return "Price difference may be justified by:\n- " + "\n- ".join(factors)
    else:
        return "No obvious attribute differences to explain price gap"
