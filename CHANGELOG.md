# Changelog

All notable changes to fishlib will be documented in this file.

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
