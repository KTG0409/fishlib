# fishlib 🐟

A Python library for parsing, standardizing, and comparing seafood product descriptions in foodservice.

**The Problem:** Seafood product descriptions are messy. The same product can be described a hundred different ways. Comparing prices across distributors, suppliers, or market data requires deep domain knowledge to know if two items are actually comparable.

**The Solution:** `fishlib` parses item descriptions into structured attributes, standardizes them to common codes, and enables apples-to-apples comparisons — so you don't need to be a fish expert to work with seafood data.

## What's New in 0.6.4

- **Fixed:** Bare `WALLEYE` no longer false-matches Alaska Pollock (new dedicated `walleye` and `pike` categories)
- **Fixed:** Bare-letter trim codes (`A`, `B`, `C`, `D`, `E`) now recognized with word-boundary safety
- **Fixed:** Squid `TUBES` no longer misclassified as rings — new `TUBE` form code added
- **Added 16 new categories:** trout, sea_bass, branzino, snapper, grouper, monkfish, mackerel, walleye, pike, perch, barramundi, hamachi, rockfish, roe, crawfish, conch
- **Expanded oyster:** added Kumamoto, European Flat (Belon), and Olympia species
- **Cleaner schema:** removed duplicate codes (`SKOFF` folded into `SKLS`, `MRNTD` kept only in `value_added`, meat-grade `CLAW` renamed to `CLAW_MEAT` to disambiguate from form)
- **Zero dependencies:** `pandas` removed from install requirements (never actually imported in library code)

**Coverage:** 38 categories, 109 species/subspecies, 411 aliases.

## Installation

```bash
pip install fishlib
```

## Quick Start

```python
import fishlib

# Parse any item description
item = fishlib.parse("SALMON FIL ATL SKON D 6OZ IVP")

print(item['category'])       # 'salmon'
print(item['subspecies'])     # 'atlantic'
print(item['form'])           # 'FIL'
print(item['skin'])           # 'SKON'
print(item['trim'])           # 'D'
print(item['size'])           # '6OZ'
print(item['pack'])           # 'IVP'

# Get a comparison key for matching
key = fishlib.comparison_key(item)
# "SALMON|ATLANTIC|FIL|SKON|D|6OZ"

# Check if two items are comparable
result = fishlib.match(
    "SALMON PRTN ATL BNLS SKLS 6 OZ CENTER CUT",
    "Portico Salmon Fillet 6 oz Boneless / Skinless",
)
print(result['is_comparable'])        # True
print(result['confidence'])           # e.g., 0.85
print(result['different_attributes']) # ['form']
print(result['recommendation'])       # human-readable summary
```

## Features

### Parse Item Descriptions

Turn messy text into structured data:

```python
fishlib.parse("POLLOCK FIL WILD ALASKA PROCESSED CHINA 6OZ IVP")
# {
#   'category': 'pollock', 'subspecies': 'alaska',
#   'form': 'FIL', 'size': '6OZ', 'pack': 'IVP',
#   'origin_harvest': 'USA', 'origin_processed': 'CHN',
#   'freeze_cycle': 'TWICE',   # finfish processed in Asia ⇒ twice frozen
#   ...
# }
```

### Standardized Codes

| Attribute | Codes |
|-----------|-------|
| **Form** | FIL (Fillet), PRTN (Portion), LOIN, WHL (Whole), STEAK, TAIL, TUBE, RING, CLUSTER, LEG, CLAW, MEAT, H&G, PD, PUD, HLSO, EZPL, ... |
| **Skin** | SKON (Skin On), SKLS (Skinless) |
| **Bone** | BNLS (Boneless), BIN (Bone In), PBO (Pin Bone Out) |
| **Trim** | A, B, C, D, E, FTRIM — bare letter or TRIM-D / DTRM variants |
| **Pack** | IVP, IQF, CVP, BULK, SHL, TRAY |
| **Storage** | FRZ (Frozen), FRSH (Fresh), RFRSH (Refreshed) |
| **Harvest** | WILD, FARM |
| **Preparation** | RAW, CKD, SMKD, CURED |
| **Value-added** | BRDD, STFD, MRNTD, SSNDD, POF |

### Origin & Freeze Cycle

```python
# origin split into harvest (where caught/farmed) and processed (where cut/portioned)
item['origin_harvest']     # 'USA'  — caught in Alaska
item['origin_processed']   # 'CHN'  — portioned in China
item['freeze_cycle']       # 'TWICE' — inferred from Asian processing of finfish

# origin is also populated for legacy single-field use
item['origin']             # 'USA'
```

### Species Coverage

38 categories across parent groups:

- **Finfish:** salmon, tuna, mahi, swordfish, sea_bass, branzino, snapper, grouper, monkfish, mackerel, barramundi, hamachi, rockfish
- **Groundfish:** cod (incl. black cod/sablefish), haddock, pollock
- **Flatfish:** halibut, flounder, sole
- **Freshwater:** tilapia, swai (pangasius/basa/tra), catfish, trout, walleye, pike, perch
- **Crustacean:** crab, lobster, shrimp, crawfish
- **Mollusk:** scallop, clam, oyster, mussel, calamari, octopus, conch
- **Roe:** ikura, tobiko, masago, caviar, uni

### Trim Guide (Salmon)

| Trim | Description | Skin |
|------|-------------|------|
| **A** | Backbone off, bellybone off | ON |
| **B** | A + backfin off, collarbone off, belly fat/fins off | ON |
| **C** | B + pin bone out | ON |
| **D** | C + back trimmed, tailpiece off, belly membrane off, nape trimmed | ON |
| **E** | D + skin removed | OFF |

**Foodservice standard:** Trim D (skin on) and Trim E (skin off).

### Cut Styles (Portions)

| Style | Description | Value |
|-------|-------------|-------|
| **Center Cut** | From center of fish only, no tails/nape | Premium |
| **Bias** | Cut at angle for better presentation | Premium |
| **Block** | Straight cuts end-to-end, includes tails | Mid |
| **Random** | Mixed pieces, various shapes | Value |

### Match & Compare

```python
fishlib.is_comparable(item1, item2)              # True / False
fishlib.match(item1, item2)                      # full match dict
fishlib.find_matches(target, candidates, threshold=0.8)
fishlib.explain_difference(item1, item2)         # human-readable explanation
```

### Reference Data

```python
from fishlib import reference

reference.trim_levels('salmon')       # Trim A–E definitions
reference.is_trim_skin_on('D')        # True  (trim D is skin-on)
reference.cut_style('CENTER')         # {'description': ..., 'premium': True}
reference.price_tier('salmon', 'king')  # {'tier': 'ultra-premium'}
```

## Why This Exists

In foodservice distribution, comparing prices requires knowing if products are truly comparable. A "6oz salmon fillet" from two different sources might be:

- Center-cut bias portion at $12/lb (premium)
- Block-cut with tail pieces at $8/lb (commodity)

Without the right attributes, price comparisons are meaningless. `fishlib` encodes the domain knowledge needed to make accurate comparisons — so you don't need 20 years of fish experience to work with seafood data.

## Contributing

Contributions welcome. Areas of interest:

- Additional species and regional variants
- International market terminology
- Packaging and processing codes
- Price reference data

## Author

**Karen Morton** — seafood industry professional with 20+ years of experience in category management and procurement. Built from years of experience managing seafood categories and the realization that this knowledge should be accessible to everyone, not trapped in experts' heads.

## Acknowledgments

Developed with assistance from [Claude](https://claude.ai) (Anthropic) for code scaffolding, refactoring, test harness construction, and documentation. All seafood domain knowledge — species classification, trim logic, cut styles, freeze-cycle inference rules, alias curation, and design decisions — comes from the author's 20+ years in foodservice category management.

## License

MIT License — use it, modify it, share it. Just make seafood data better for everyone.
