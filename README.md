# fishlib ðŸŸ

A Python library for parsing, standardizing, and comparing seafood product descriptions in the food industry.

**The Problem:** Seafood product descriptions are messy. The same product can be described a hundred different ways. Comparing prices across distributors, suppliers, or market data requires deep domain knowledge to know if two items are actually comparable.

**The Solution:** `fishlib` parses item descriptions into structured attributes, standardizes them to common codes, and enables apples-to-apples comparisonsâ€”so you don't need to be a fish expert to work with seafood data.

## Installation

```bash
pip install fishlib
```

## Quick Start

```python
import fishlib

# Parse any item description
item = fishlib.parse("SALMON FIL ATL SKON DTRM 6OZ IVP")

print(item)
# {
#     'species': 'Atlantic Salmon',
#     'form': 'FIL',
#     'skin': 'SKON',
#     'bone': 'BNLS',
#     'trim': 'D',
#     'size': '6OZ',
#     'pack': 'IVP',
#     'storage': 'FRZ'
# }

# Get a comparison key for matching
key = fishlib.comparison_key(item)
print(key)
# "SALMON|ATLANTIC|FIL|SKON|BNLS|D|6OZ"

# Check if two items are comparable
distributor_item = "SALMON PORTION ATL BNLS SKLS 6 OZ CENTER CUT"
circana_item = "Portico Salmon Fillet 6 oz Boneless / Skinless"

match = fishlib.match(distributor_item, circana_item)
print(match)
# {
#     'is_match': True,
#     'confidence': 0.85,
#     'differences': ['form: PORTION vs FIL'],
#     'recommendation': 'Comparable with caution - form differs'
# }
```

## Features

### Parse Item Descriptions
Turn messy text into structured data:

```python
fishlib.parse("SALMON SOCKEYE FIL WILD ALASKA SKON 8OZ IQF")
# Returns structured dict with all attributes
```

### New in v0.2.0: Enhanced Attribute Extraction

```python
# Crab meat grade detection
fishlib.parse("CRAB MEAT JUMBO LUMP PASTEURIZED")
# Returns: {'meat_grade': 'JUMBO_LUMP', ...}

# Preparation status (raw, cooked, smoked, cured)
fishlib.parse("SHRIMP 16/20 P&D COOKED")
# Returns: {'preparation': 'COOKED', ...}

# Value-added detection (breaded, stuffed, marinated, etc.)
fishlib.parse("COD FIL PANKO CRUSTED 4OZ")
# Returns: {'value_added': 'BREADED', ...}
```

### Standardize Codes
Consistent codes across any data source:

| Attribute | Codes |
|-----------|-------|
| **Form** | FIL (Fillet), PRTN (Portion), LOIN, WHL (Whole), STEAK, etc. |
| **Skin** | SKON (Skin On), SKLS (Skinless), SKOFF (Skin Off) |
| **Bone** | BNLS (Boneless), BIN (Bone In), PBO (Pin Bone Out) |
| **Trim** | A, B, C, D, E (see Trim Guide) |
| **Pack** | IVP, IQF, CVP, BULK |
| **Storage** | FRZ (Frozen), FRSH (Fresh), RFRSH (Refreshed) |
| **Meat Grade** | JUMBO_LUMP, LUMP, BACKFIN, SPECIAL, CLAW |
| **Preparation** | RAW, COOKED, SMOKED, CURED |
| **Value-Added** | BREADED, STUFFED, MARINATED, GLAZED, BLACKENED, FORMED |

### Species Support
Built-in knowledge for 31 seafood categories and 86 species:

- **Salmon**: Atlantic, King/Chinook, Sockeye, Coho, Keta/Chum, Pink
- **Crab**: King, Snow, Dungeness, Blue, Stone, Jonah, Soft Shell
- **Lobster**: Maine, Canadian, Warm Water
- **Shrimp**: White, Pink, Brown, Tiger, Rock, Royal Red
- **Groundfish**: Cod (Atlantic, Pacific, Black/Sablefish, Ling), Haddock, Pollock
- **Flatfish**: Flounder, Halibut, Sole (Dover, Petrale, Lemon, Rex, Gray)
- **Shellfish**: Scallops (Sea, Bay, Calico), Clams, Oysters, Mussels
- **Snapper**: Red, Yellowtail, Vermilion, Lane, Mangrove, Silk
- **Grouper**: Red, Black, Gag, Yellowedge, Scamp
- **Other Finfish**: Branzino, Sea Bass (Chilean, Black, Striped), Trout, Barramundi, Wahoo, Monkfish, Mahi, Swordfish, Tuna
- **Other Shellfish**: Crawfish, Calamari, Octopus

### Reference Data
Access industry knowledge:

```python
# Salmon trim levels
fishlib.reference.trim_levels('salmon')
# Returns definitions for Trim A-E with skin status

# Species price tiers (relative positioning, not dollar amounts)
fishlib.species.get_price_tier('salmon', 'king')
# Returns: 'ultra-premium'

# Cut style definitions
fishlib.reference.cut_style('center_cut')
# Returns: {'description': 'Portions from center of fish only...', 'premium': True}
```

### Match & Compare
Find comparable items across data sources:

```python
# Simple match
fishlib.is_comparable(item1, item2)  # Returns True/False

# Detailed match with confidence score
fishlib.match(item1, item2)  # Returns match details

# Find best matches in a list
fishlib.find_matches(target_item, list_of_items, threshold=0.8)
```

## Trim Guide (Salmon)

| Trim | Description | Skin |
|------|-------------|------|
| **A** | Backbone off, bellybone off | ON |
| **B** | + Backfin off, collarbone off, belly fat/fins off | ON |
| **C** | + Pin bone out | ON |
| **D** | + Back trimmed, tailpiece off, belly membrane off, nape trimmed | ON |
| **E** | Everything in D + skin removed | OFF |

**Key insight:** Trim A-D are all skin ON. Only Trim E is skin OFF.
**Foodservice standard:** Trim D (skin on) and Trim E (skin off).

## Cut Styles (Portions)

| Style | Description | Value |
|-------|-------------|-------|
| **Center Cut** | From center of fish only, no tails/nape | Premium |
| **Bias** | Cut at angle for better presentation | Premium |
| **Block** | Straight cuts end-to-end, includes tails | Mid |
| **Random** | Mixed pieces, various shapes | Value |

## Why This Exists

In food distribution, comparing prices requires knowing if products are truly comparable. A "6oz salmon fillet" from two different sources might be:

- Center-cut bias portion (premium)
- Block-cut with tail pieces (commodity)

Without the right attributes, price comparisons are meaningless. `fishlib` encodes the domain knowledge needed to make accurate comparisonsâ€”so you don't need 20 years of fish experience to work with seafood data.

## Changelog

### v0.2.0
- **New attributes**: meat_grade, preparation, value_added
- **New species**: Snapper (6), Grouper (5), Branzino, Sea Bass (3), Trout (3), Barramundi, Wahoo, Monkfish, Crawfish
- **New origins**: Faroe Islands, Bangladesh, Myanmar, Philippines, Peru, Argentina, UK, Japan, South Korea, Taiwan, Spain, Portugal, Greece, Turkey, Honduras
- **Fixed**: Species matching now correctly identifies "COD ATLANTIC" as cod (not salmon)
- **Removed**: Hardcoded price ranges (price tiers retained for relative comparisons)

### v0.1.0
- Initial release

## Contributing

Contributions welcome! Areas of interest:

- Additional species and regional variants
- International market terminology
- Packaging and processing codes

## Author

**Karen Morton** - Seafood industry professional with experience in category management and procurement.

Built from years of experience managing seafood categories and the realization that this knowledge should be accessible to everyone, not trapped in experts' heads.

## License

MIT License - Use it, modify it, share it. Just make seafood data better for everyone.
