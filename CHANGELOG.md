# Changelog

## [0.4.4] - 2026-02-18

### Added — Species (31 → 62 categories)
- **Whiting** — WHITING, SILVER HAKE, MERLUCIUS
- **Hake / Cape Hake** — HAKE, CAPE HAKE, CAPENSIS, CAPE CAPENSIS, MERLUCCIUS CAPENSIS
- **Perch** — 4 subtypes: Yellow Perch, Ocean Perch, European Perch, Pike Perch/Zander (ZNDR, ZANDR)
- **Amberjack / Kanpachi** — AMBERJACK, KANPACHI, KAMPACHI
- **Eel / Unagi** — UNAGI, EEL SMOKED, KABAYAKI, ANAGO
- **Escolar** — ESCOLAR, SAKU BLOCK
- **Arctic Char** — ARCTIC CHAR, ARTIC CHAR, CHAR ARCTIC
- **Cobia** — COBIA
- **Langostino** — LANGOSTINO
- **Pompano** — POMPANO, GOLDEN POMPANO
- **Bluefish** — BLUEFISH
- **Bluegill** — BLUEGILL, BREAM
- **Hogfish** — HOGFISH
- **Cuttlefish** — CUTTLEFISH, SEPIA
- **Sardine** — SARDINE, PILCHARD
- **Herring** — HERRING, ATLANTIC HERRING
- **Croaker** — CROAKER, ATLANTIC CROAKER
- **Milkfish** — MILKFISH, BANGUS
- **Tripletail** — TRIPLETAIL, TRIPLE TAIL
- **Redfish** — REDFISH, RED DRUM (also alias on drum category)
- **Sea Urchin / Uni** — SEA URCHIN, UNI
- **Pangasius** — PANGASIUS, BASA

### Added — Species from v0.4.3 session (previously missing from JSON)
- **Corvina** — CORVINA, COVINA, WEAKFISH
- **Hamachi (Yellowtail)** — HAMACHI, YELLOWTAIL, BURI, Y-T, YT
- **Orange Roughy** — ORANGE ROUGHY, ORNG ROUGHY, ROUGHY
- **Turbot** — TURBOT, Greenland Turbot variant
- **Drum** — RED DRUM, BLACK DRUM
- **Mackerel** — Atlantic, King (KINGFISH), Spanish variants
- **Smelt** — SMELT, CAPELIN as alias
- **Conch** — CONCH, QUEEN CONCH, FRTTR
- **Roe** — TOBIKO, MASAGO, IKURA, Sturgeon CAVIAR, LUMPFISH

### Fixed — Species alias bugs
- `BRONZINI` (with I) added to branzino aliases — was a miss causing all BRONZINI items to fail
- `BRNZNO` added to branzino aliases
- `BAY` removed from scallop aliases → replaced with `BAY SCALLOP` (BAYOU was triggering Bay Scallop)
- `US` and `DOMESTIC` removed from catfish channel aliases (too generic, caused false positives)
- `SEA` removed from scallop sea aliases → replaced with `SEA SCALLOP`

### Added — COO (origin_country) in standard_codes.json
- **Brazil** — BRAZIL, BRAZILIAN, BRA, BRASIL
- **Mauritius** — MAURITIUS, MAURITS, MAURIT, MRT
- **NOR** aliases: NORWG, NORWGN (common truncations in Sysco data)
- **CAN** aliases: CANADN, CANADAIN (common misspellings)
- **USA** aliases: ALSK, ALASKAN, DOMSTC, WILD AK
- **CHL** aliases: CHLN
- **IDN** aliases: INDON
- **SCO** aliases: SCOTCH, SCOTTSH, SCOT
- **ICE** aliases: ICELND, ICELAN
- **GRC** aliases: GRK
- **VNM** aliases: VIETN
- **ECU** aliases: ECUAD
- **PER** aliases: PERUV

### Fixed — COO false positives
- `ENGLAND` removed from GBR aliases — was matching "NEW ENGLAND SEAFOOD MIX" and "N ENGLAND STY"
- `UK` removed from GBR aliases — too short (2 chars), caused false positives

### Performance (validated on 7,123 Sysco items)
- Species match rate: **91.2% → 97.0%** (+418 items)
- COO match rate: **11.9% → 13.8%** (+141 items)
- Status: 0 critical false positives

---

## [0.4.3] - 2025
- Fixed rockfish misclassified as striped bass
- Fixed catfish subspecies (domestic vs imported)
- Resolved 125+ misclassified Sysco items
- Added size bucket matching for competitive analysis

## [0.3.0] - 2025
- Added 45+ species categories
- Added anchovy, whiting, perch, sardine, herring, mackerel, hake, orange roughy, corvina, cobia, langostino, conch, hamachi, pike

## [0.2.0] - 2025
- Enhanced attribute extraction
- Crab meat grade detection (JUMBO_LUMP, LUMP, BACKFIN, SPECIAL, CLAW)
- Preparation status (raw, cooked, smoked, cured)
- Value-added detection (breaded, stuffed, marinated, etc.)

## [0.1.0] - 2025
- Initial release
- Core parser for seafood item descriptions
- Species identification, form, skin, bone, trim, size, pack, storage
- Comparison key generation for price matching
