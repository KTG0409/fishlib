# Changelog

## v0.3.0

### New Species (14 added, 45 categories / 109 species total)
- **Anchovy** - Atlantic, Mediterranean varieties
- **Whiting** - Silver hake
- **Perch** - Yellow perch, Ocean perch
- **Sardine** - Pilchard
- **Herring** - Atlantic, Pacific
- **Mackerel** - Atlantic, Spanish, King
- **Hake** - Generic, Cape hake
- **Orange Roughy** - Deep sea perch
- **Corvina** - Drum, Croaker
- **Cobia** - Lemonfish
- **Langostino** - Langoustine, Squat lobster
- **Conch** - Queen conch
- **Hamachi** - Yellowtail, Japanese amberjack, Kampachi
- **Pike** - Walleye, Northern pike

### Bug Fixes
- **BRONZINI alias** now correctly maps to branzino
- **Raw vs Cooked** shrimp now correctly marked as NOT comparable
- **Breaded vs Plain** now correctly marked as NOT comparable
- **"TAIL ON"** no longer misparses as form=TAIL for shrimp
- **P&D** now detected as shrimp_form attribute
- **LUMPFISH** no longer falsely triggers meat_grade=LUMP
- **Smashed codes** now parsed correctly (BNLSKL, SKONCAN, SKOFFE, CKD100/150, etc.)

### New Aliases and Codes
- **Trim**: DTRIM, D/TRIM, ETRIM, E/TRIM
- **Preparation**: PRCKD (precooked), SMKD (smoked)
- **Value-Added**: CRISPANKO, POPCORN/POPCRN, PUB STYLE
- **Cut Style**: SAKU (Japanese block cut), XTBIAS (extra bias)
- **Form**: PASTE, CLUSTERS (plural)

### Improved Parser
- New smashed-code pre-processor splits concatenated abbreviations
- LUMPFISH false positive protection for meat_grade
- Shrimp form detection: P&D, PUD, SHELL_ON, TAIL_ON, TAIL_OFF, HEAD_ON
- Zero dependencies (pandas removed)

## v0.2.0
- New attributes: meat_grade, preparation, value_added
- 19 new species (snapper, grouper, branzino, sea bass, trout, etc.)
- 15 new origin countries
- Fixed species matching priority system

## v0.1.0
- Initial release
