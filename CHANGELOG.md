# Changelog
All notable changes to fishlib will be documented in this file.

## [0.4.4] - 2026-02-19
### Fixed
- **Walleye misclassification**: Walleye (a freshwater lake fish) was incorrectly an alias for Alaska Pollock — now correctly classified as pike/walleye (59 Sysco items fixed)
- **Priority 3 false matches**: Generic words like CHILEAN, DOMESTIC, RED, BLUE, ATLANTIC, etc. could match species without the category name in text (e.g., "ABALONE CHILEAN" → Chilean Sea Bass). Now uses a **whitelist** — only specific, unambiguous aliases (SABLEFISH, VANNAMEI, STRIPER, etc.) can match without the category name present
- **Pollock aliases**: Removed ALASKA/ALASKAN from pollock subspecies aliases (too generic, caused false matches)
- **Cod aliases**: Moved TRUE COD to Pacific Cod, removed GRAY COD
- **Calamari/Octopus**: Category corrected from "Mollusk" to "Cephalopod"

### Added
- **Ocean Trout**: New subspecies under trout (separated from steelhead)
- **Pike restructured**: Walleye Pike and Northern Pike as proper subspecies with full alias sets
- **Branzino aliases**: BRANZINI, EURO BASS added
- **Atlantic Pollock**: SAITHE alias added
- **P3 whitelist system**: Explicit whitelist of ~100 aliases safe for Priority 3 matching; all others require category name in text

### Changed
- **Trout**: Removed salmon trim levels (A-E don't apply to trout), added DRSD form

## [0.4.3] - 2026-02-18
### Fixed
- **Rockfish misclassification**: Pacific rockfish (Sebastes) was incorrectly tagged as Striped Bass — now its own `rockfish` category with 13 aliases (60 Sysco items fixed)
- **Striped bass missed**: Reversed word order "BASS STRIPED" now correctly parses (65 Sysco items fixed)
- **Catfish restructured**: Subspecies split into `domestic` (US farm-raised), `channel` (imported China/Vietnam), and `blue` (wild blue catfish)
- **Scallop false match**: Standalone "SEA" alias removed from Priority 3 matching (min alias length raised to 4 chars) — prevents "BASS SEA FILET STRIPED" from matching as Sea Scallop

### Added
- New species category: `rockfish` (Pacific Rockfish / Sebastes) with aliases for common varieties (bocaccio, canary, vermilion, widow, yelloweye, etc.)
- Catfish subspecies: `domestic`, `channel`, `blue` with origin-aware classification
- Striped bass aliases: "BASS STRIPED", "HYBRID BASS" for reversed word order

## [0.4.2] - 2026-02-18
### Added
- **Size bucket matching**: New `size_bucket` field maps exact sizes and ranges into standard foodservice competitive buckets
- Ounce buckets: 1-2OZ through 16OZ+
- Pound buckets: UNDER-1LB through 9LB+
- `2OZ` and `2-3OZ` now land in the same bucket → comparable for PMI matching
- Matcher uses `size_bucket` instead of raw `size` for comparison_key and matching
- Raw `size` field preserved for exact specifications

## [0.4.1] - 2026-02-12
### Fixed
- README fish emoji (🐟) garbled during build — fixed line 1 encoding

## [0.4.0] - 2026-02-12
### Added
- **Origin split**: `origin_harvest` (where caught/farmed) and `origin_processed` (where cut/portioned)
- Dual-origin parsing: "WILD ALASKA PROCESSED IN CHINA" → harvest=USA, processed=CHN
- Patterns: "PRODUCT OF X, PROC Y", "CAUGHT X/PROCESSED Y", "PACKED IN Y"
- **Freeze cycle inference**: `freeze_cycle` field (SINGLE, TWICE, or None)
  - Finfish + Asian processing country → TWICE (twice-frozen)
  - Exception: harvest=processing country (e.g., tilapia farmed+processed in China) → SINGLE
  - Crustaceans, mollusks, cephalopods → exempt (None)
  - Fresh products → None
- Freeze cycle mismatch is a HARD BLOCK on comparability in matcher
- Legacy `origin` field preserved (harvest priority, fallback to processed)
- New standardization: `standardize_origin_harvest()`, `standardize_origin_processed()`

## [0.3.0] - 2026-02-10
### Added
- **14 new species categories**: Anchovy, Whiting, Perch, Sardine, Herring, Mackerel, Hake, Orange Roughy, Corvina, Cobia, Langostino, Conch, Hamachi, Pike
- Fixed BRONZINI alias → BRANZINO

## [0.2.0] - 2026-02-06
### Added
- **New attributes**: `meat_grade`, `preparation`, `value_added` parsing and standardization
- **New species** (19 added):
  - Snapper: Red, Yellowtail, Vermilion, Lane, Mangrove, Silk
  - Grouper: Red, Black, Gag, Yellowedge, Scamp
  - Branzino, Sea Bass (Chilean, Black, Striped)
  - Trout (Rainbow, Steelhead, Brook), Barramundi, Wahoo, Monkfish, Crawfish
- **New origins** (15 added): Faroe Islands, Bangladesh, Myanmar, Philippines, Peru, Argentina, UK, Japan, South Korea, Taiwan, Spain, Portugal, Greece, Turkey, Honduras
- **New standardization functions**: `standardize_meat_grade()`, `standardize_preparation()`, `standardize_value_added()`
- **New standard codes**: meat_grade (6 grades), preparation (4 types), value_added (7 types)
- **Reference data**: Meat grade definitions, preparation types, value-added processing types with industry insights
- **Matcher improvements**: comparison_key and match now include meat_grade, preparation, and value_added
### Fixed
- Species matching: "COD ATLANTIC" now correctly identifies as cod, not salmon
- Species priority system: category name in text takes precedence over alias-only matches
- Longer alias matches now preferred over shorter ones to prevent false positives
### Changed
- Removed hardcoded price ranges (price tiers retained for relative comparisons)
- Species extraction uses three-tier priority system for better accuracy

## [0.1.0] - 2025-12-XX
### Added
- Initial release
- Parser for seafood item descriptions
- Standardization for form, skin, bone, trim, pack, storage, cut_style, harvest, origin
- Species support for: Salmon, Crab, Lobster, Shrimp, Cod, Haddock, Pollock, Halibut, Flounder, Sole, Tilapia, Swai, Catfish, Scallop, Tuna, Mahi, Swordfish, Calamari, Octopus, Clam, Oyster, Mussel
- Matcher module with comparison_key, match, is_comparable, find_matches
- Reference data for trim levels, cut styles, forms, skin/bone codes, pack styles, price tiers
- Species module with price tiers, aliases, harvest types
