"""
Tests for fishlib v0.4.0 — Origin Split & Freeze Cycle

Tests cover:
  1. Origin extraction (harvest vs processing country)
  2. Freeze cycle inference
  3. Matcher hard block on freeze_cycle mismatch
  4. Pollock-specific scenarios (the real-world use case)
  5. Backward compatibility (legacy 'origin' field)
  6. Edge cases
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from fishlib.parser import parse, _extract_origins, _infer_freeze_cycle, _match_country
from fishlib.matcher import comparison_key, match, is_comparable, explain_difference


# =========================================================================
# 1. ORIGIN EXTRACTION — dual origin patterns
# =========================================================================

class TestOriginExtraction:
    """Test harvest vs processing country detection."""
    
    def test_explicit_dual_origin(self):
        """WILD ALASKA PROCESSED IN CHINA → harvest=USA, processed=CHN"""
        item = parse("POLLOCK FIL WILD ALASKA PROCESSED IN CHINA 6OZ")
        assert item['origin_harvest'] == 'USA'
        assert item['origin_processed'] == 'CHN'
    
    def test_dual_origin_comma_separated(self):
        """PRODUCT OF USA, PROC CHINA"""
        item = parse("COD FIL PRODUCT OF USA, PROC CHINA 4OZ")
        assert item['origin_harvest'] == 'USA'
        assert item['origin_processed'] == 'CHN'
    
    def test_dual_origin_slash_separated(self):
        """CAUGHT NORWAY/PROCESSED VIETNAM"""
        item = parse("COD LOIN CAUGHT NORWAY/PROCESSED VIETNAM 8OZ")
        assert item['origin_harvest'] == 'NOR'
        assert item['origin_processed'] == 'VNM'
    
    def test_wild_caught_proc_abbrev(self):
        """WILD CAUGHT USA PROC CHN"""
        item = parse("POLLOCK FIL WILD CAUGHT USA PROC CHN 6OZ IVP")
        assert item['origin_harvest'] == 'USA'
        assert item['origin_processed'] == 'CHN'
    
    def test_processed_only(self):
        """Only processing country mentioned"""
        item = parse("POLLOCK FIL PROCESSED IN CHINA 6OZ")
        assert item['origin_processed'] == 'CHN'
        assert item['origin_harvest'] is None
    
    def test_harvest_only_product_of(self):
        """PRODUCT OF NORWAY — harvest only"""
        item = parse("SALMON FIL PRODUCT OF NORWAY 8OZ")
        assert item['origin_harvest'] == 'NOR'
        assert item['origin_processed'] is None
    
    def test_harvest_only_wild(self):
        """WILD ALASKA — harvest indicator"""
        item = parse("POLLOCK FIL WILD ALASKA 6OZ")
        assert item['origin_harvest'] == 'USA'
        assert item['origin_processed'] is None
    
    def test_single_country_no_context(self):
        """Just a country name, no harvest/processing context"""
        item = parse("SALMON FIL CHILE 6OZ")
        assert item['origin_harvest'] == 'CHL'
        assert item['origin_processed'] is None
    
    def test_legacy_origin_backward_compat(self):
        """Legacy 'origin' field still populated"""
        item = parse("POLLOCK FIL WILD ALASKA PROCESSED IN CHINA 6OZ")
        assert item['origin'] == 'USA'  # harvest takes priority
    
    def test_legacy_origin_processing_only(self):
        """Legacy 'origin' falls back to processing when no harvest"""
        item = parse("POLLOCK FIL PROCESSED IN CHINA 6OZ")
        assert item['origin'] == 'CHN'
    
    def test_packed_in_pattern(self):
        """PACKED IN VIETNAM"""
        item = parse("COD FIL PACKED IN VIETNAM 4OZ")
        assert item['origin_processed'] == 'VNM'
    
    def test_farmed_in_pattern(self):
        """FARM RAISED IN CHILE"""
        item = parse("SALMON FIL FARM RAISED IN CHILE 6OZ")
        assert item['origin_harvest'] == 'CHL'
    
    def test_no_origin(self):
        """No origin info at all"""
        item = parse("SALMON FIL SKON DTRM 6OZ IVP")
        assert item['origin_harvest'] is None
        assert item['origin_processed'] is None
        assert item['origin'] is None


# =========================================================================
# 2. FREEZE CYCLE INFERENCE
# =========================================================================

class TestFreezeCycle:
    """Test single vs twice-frozen inference."""
    
    # --- Twice-frozen cases ---
    
    def test_pollock_alaska_proc_china(self):
        """Classic twice-frozen: Wild Alaska pollock processed in China"""
        item = parse("POLLOCK FIL WILD ALASKA PROCESSED IN CHINA 6OZ")
        assert item['freeze_cycle'] == 'TWICE'
    
    def test_cod_norway_proc_vietnam(self):
        """Cod caught Norway, processed Vietnam = twice"""
        item = parse("COD FIL CAUGHT NORWAY/PROCESSED VIETNAM 4OZ")
        assert item['freeze_cycle'] == 'TWICE'
    
    def test_pollock_proc_china_no_harvest(self):
        """Processing in China, no harvest info = twice"""
        item = parse("POLLOCK FIL PROCESSED IN CHINA 6OZ")
        assert item['freeze_cycle'] == 'TWICE'
    
    def test_haddock_proc_thailand(self):
        """Haddock processed in Thailand = twice"""
        item = parse("HADDOCK FIL PROCESSED IN THAILAND 4OZ")
        assert item['freeze_cycle'] == 'TWICE'
    
    # --- Single-frozen cases ---
    
    def test_pollock_alaska_no_proc(self):
        """Wild Alaska pollock, no processing country = unknown (None)"""
        item = parse("POLLOCK FIL WILD ALASKA 6OZ")
        # No processing country info → can't determine
        assert item['freeze_cycle'] is None
    
    def test_salmon_norway_proc_norway(self):
        """Farmed Norway, processed Norway = single"""
        item = parse("SALMON FIL PRODUCT OF NORWAY, PROCESSED NORWAY 6OZ")
        assert item['freeze_cycle'] == 'SINGLE'
    
    def test_cod_iceland_proc_iceland(self):
        """Caught Iceland, processed Iceland = single"""
        item = parse("COD FIL CAUGHT ICELAND/PROCESSED ICELAND 4OZ")
        assert item['freeze_cycle'] == 'SINGLE'
    
    def test_pollock_proc_usa(self):
        """Processed in USA = single"""
        item = parse("POLLOCK FIL PROCESSED IN USA 6OZ")
        assert item['freeze_cycle'] == 'SINGLE'
    
    # --- Domestic Asian production (NOT twice-frozen) ---
    
    def test_tilapia_china_proc_china(self):
        """Tilapia farmed AND processed in China = single (never left)"""
        item = parse("TILAPIA FIL PRODUCT OF CHINA, PROCESSED CHINA 5OZ")
        assert item['freeze_cycle'] == 'SINGLE'
    
    def test_swai_vietnam_proc_vietnam(self):
        """Swai farmed AND processed in Vietnam = single"""
        item = parse("SWAI FIL PRODUCT OF VIETNAM, PROCESSED VIETNAM 5OZ")
        assert item['freeze_cycle'] == 'SINGLE'
    
    # --- Exempt categories (crustaceans, mollusks) ---
    
    def test_shrimp_exempt(self):
        """Shrimp is exempt from twice-frozen logic"""
        item = parse("SHRIMP 16/20 P&D PROCESSED IN CHINA")
        assert item['freeze_cycle'] is None
    
    def test_crab_exempt(self):
        """Crab is exempt"""
        item = parse("CRAB MEAT JUMBO LUMP PROCESSED IN CHINA")
        assert item['freeze_cycle'] is None
    
    def test_lobster_exempt(self):
        """Lobster is exempt"""
        item = parse("LOBSTER TAIL PROCESSED IN CHINA 6OZ")
        assert item['freeze_cycle'] is None
    
    def test_scallop_exempt(self):
        """Scallop is exempt"""
        item = parse("SCALLOP SEA U10 PROCESSED IN CHINA")
        assert item['freeze_cycle'] is None
    
    def test_calamari_exempt(self):
        """Calamari is exempt"""
        item = parse("CALAMARI RING PROCESSED IN CHINA")
        assert item['freeze_cycle'] is None
    
    # --- Fresh product ---
    
    def test_fresh_no_freeze_cycle(self):
        """Fresh product = no freeze cycle"""
        item = parse("COD FIL FRESH PRODUCT OF ICELAND 4OZ")
        assert item['freeze_cycle'] is None
    
    # --- No species detected ---
    
    def test_no_species_no_freeze(self):
        """Can't determine freeze cycle without species"""
        item = parse("FIL PROCESSED IN CHINA 6OZ")
        assert item['freeze_cycle'] is None


# =========================================================================
# 3. MATCHER — freeze_cycle as hard block
# =========================================================================

class TestMatcherFreezeCycle:
    """Test that freeze_cycle mismatch blocks comparability."""
    
    def test_same_pollock_different_freeze(self):
        """Same species+form but single vs twice = NOT comparable"""
        # One processed in China (twice), one processed in USA (single)
        item1 = parse("POLLOCK FIL WILD ALASKA PROCESSED IN CHINA 6OZ")
        item2 = parse("POLLOCK FIL WILD ALASKA PROCESSED IN USA 6OZ")
        result = match(item1, item2)
        assert result['is_comparable'] is False
        assert 'freeze_cycle' in result['different_attributes']
        assert 'freeze cycle' in result['recommendation'].lower()
    
    def test_same_freeze_cycle_comparable(self):
        """Both twice-frozen = comparable"""
        item1 = parse("POLLOCK FIL PROCESSED IN CHINA 6OZ")
        item2 = parse("POLLOCK FIL PROCESSED IN VIETNAM 6OZ")
        result = match(item1, item2)
        # Both TWICE — freeze_cycle matches, should be comparable
        assert 'freeze_cycle' in result['matching_attributes']
    
    def test_freeze_cycle_in_comparison_key(self):
        """Freeze cycle appears in comparison key"""
        item = parse("POLLOCK FIL WILD ALASKA PROCESSED IN CHINA 6OZ")
        key = comparison_key(item)
        assert 'TWICE' in key
    
    def test_single_in_comparison_key(self):
        """SINGLE appears in comparison key"""
        item = parse("POLLOCK FIL PROCESSED IN USA 6OZ")
        key = comparison_key(item)
        assert 'SINGLE' in key
    
    def test_is_comparable_blocks_freeze(self):
        """is_comparable() returns False for freeze cycle mismatch"""
        assert is_comparable(
            "POLLOCK FIL PROCESSED IN CHINA 6OZ",
            "POLLOCK FIL PROCESSED IN USA 6OZ"
        ) is False
    
    def test_explain_difference_shows_freeze(self):
        """explain_difference mentions freeze cycle"""
        explanation = explain_difference(
            "POLLOCK FIL PROCESSED IN CHINA 6OZ",
            "POLLOCK FIL PROCESSED IN USA 6OZ"
        )
        assert 'freeze_cycle' in explanation.lower()
    
    def test_missing_freeze_is_not_hard_block(self):
        """If one has freeze_cycle and other is None, it's 'missing' not 'different'"""
        item1 = parse("POLLOCK FIL PROCESSED IN CHINA 6OZ")  # TWICE
        item2 = parse("POLLOCK FIL 6OZ")  # None (no origin info)
        result = match(item1, item2)
        # freeze_cycle should be in missing, not different
        assert 'freeze_cycle' in result['missing_attributes']
        # Missing doesn't hard-block (only different does)
        assert 'freeze_cycle' not in result['different_attributes']


# =========================================================================
# 4. POLLOCK-SPECIFIC SCENARIOS (real-world use case)
# =========================================================================

class TestPollockScenarios:
    """
    Real-world pollock scenarios for the deep dive.
    
    Pollock is THE case study for twice-frozen:
    - Wild caught in Alaska/Russia
    - Shipped frozen to China for processing
    - Thawed, filleted, refrozen
    - Exported back as finished product
    
    The twice-frozen product is fundamentally different in:
    - Quality (moisture loss, texture)
    - Yield (more drip loss when thawed)
    - Price (significantly cheaper)
    """
    
    def test_pollock_alaska_all_domestic(self):
        """100% domestic pollock — single frozen"""
        item = parse("POLLOCK FIL WILD ALASKA PROCESSED IN USA 6OZ IVP")
        assert item['category'] == 'pollock'
        assert item['origin_harvest'] == 'USA'
        assert item['origin_processed'] == 'USA'
        assert item['freeze_cycle'] == 'SINGLE'
    
    def test_pollock_alaska_china_processed(self):
        """Alaska caught, China processed — twice frozen"""
        item = parse("POLLOCK FIL WILD ALASKA PROC CHINA 6OZ IVP")
        assert item['origin_harvest'] == 'USA'
        assert item['origin_processed'] == 'CHN'
        assert item['freeze_cycle'] == 'TWICE'
    
    def test_pollock_russia_china_processed(self):
        """Russia caught, China processed — twice frozen"""
        item = parse("POLLOCK FIL WILD CAUGHT RUSSIA, PROCESSED CHINA 6OZ")
        assert item['origin_harvest'] == 'RUS'
        assert item['origin_processed'] == 'CHN'
        assert item['freeze_cycle'] == 'TWICE'
    
    def test_pollock_single_vs_twice_not_comparable(self):
        """Single-frozen vs twice-frozen pollock are NOT comparable"""
        domestic = "POLLOCK FIL WILD ALASKA PROCESSED USA 6OZ"
        china_proc = "POLLOCK FIL WILD ALASKA PROCESSED CHINA 6OZ"
        result = match(domestic, china_proc)
        assert result['is_comparable'] is False
        assert 'freeze_cycle' in result['different_attributes']
    
    def test_pollock_both_twice_comparable(self):
        """Two twice-frozen pollock products ARE comparable"""
        china = "POLLOCK FIL PROCESSED CHINA 6OZ"
        vietnam = "POLLOCK FIL PROCESSED VIETNAM 6OZ"
        result = match(china, vietnam)
        assert 'freeze_cycle' in result['matching_attributes']
    
    def test_pollock_unknown_vs_twice(self):
        """Unknown freeze vs twice = missing attribute, not hard block"""
        unknown = "POLLOCK FIL 6OZ"  # no origin info
        twice = "POLLOCK FIL PROCESSED CHINA 6OZ"
        result = match(unknown, twice)
        assert 'freeze_cycle' in result['missing_attributes']
        # Not a hard block — but confidence is reduced


# =========================================================================
# 5. BACKWARD COMPATIBILITY
# =========================================================================

class TestBackwardCompat:
    """Ensure v0.3.0 behavior isn't broken."""
    
    def test_basic_parse_still_works(self):
        """Standard parse still returns all expected fields"""
        item = parse("SALMON FIL ATL SKON DTRM 6OZ IVP")
        assert item['species'] == 'Atlantic Salmon'
        assert item['form'] == 'FIL'
        assert item['skin'] == 'SKON'
        assert item['trim'] == 'D'
        assert item['size'] == '6OZ'
        assert item['pack'] == 'IVP'
    
    def test_new_fields_present(self):
        """New fields exist in parse output"""
        item = parse("SALMON FIL ATL 6OZ")
        assert 'origin_harvest' in item
        assert 'origin_processed' in item
        assert 'freeze_cycle' in item
    
    def test_comparison_key_without_freeze(self):
        """Comparison key works when freeze_cycle is None"""
        item = parse("SALMON FIL ATL 6OZ")
        key = comparison_key(item)
        assert 'SALMON' in key
        assert 'TWICE' not in key
        assert 'SINGLE' not in key
    
    def test_species_still_detected(self):
        """All existing species still parse correctly"""
        tests = [
            ("SALMON FIL ATL", 'salmon', 'atlantic'),
            ("COD FIL PACIFIC", 'cod', 'pacific'),
            ("SHRIMP 16/20 WHITE", 'shrimp', 'white'),
            ("CRAB MEAT JUMBO LUMP", 'crab', None),
            ("LOBSTER TAIL MAINE", 'lobster', 'maine'),
            ("POLLOCK FIL ALASKA", 'pollock', 'alaska'),
        ]
        for desc, expected_cat, expected_sub in tests:
            item = parse(desc)
            assert item['category'] == expected_cat, f"Failed: {desc}"
            if expected_sub:
                assert item['subspecies'] == expected_sub, f"Failed subspecies: {desc}"
    
    def test_match_still_works_basic(self):
        """Basic matching still works"""
        result = match("SALMON FIL ATL 6OZ", "SALMON FIL ATL 6OZ")
        assert result['is_comparable'] is True
        assert result['confidence'] >= 0.8
    
    def test_different_species_still_blocks(self):
        """Different species still blocks comparability"""
        result = match("SALMON FIL ATL 6OZ", "COD FIL ATL 6OZ")
        assert result['is_comparable'] is False


# =========================================================================
# 6. EDGE CASES
# =========================================================================

class TestEdgeCases:
    """Edge cases and unusual patterns."""
    
    def test_empty_description(self):
        """Empty string doesn't crash"""
        item = parse("")
        assert item.get('error') == 'Empty description'
    
    def test_no_country_in_processed_phrase(self):
        """'PROCESSED' without a country doesn't crash"""
        item = parse("POLLOCK FIL PROCESSED 6OZ")
        # Should handle gracefully
        assert item['category'] == 'pollock'
    
    def test_multiple_countries(self):
        """Description with multiple country references"""
        item = parse("COD FIL WILD CAUGHT ICELAND PROCESSED IN CHINA 4OZ")
        assert item['origin_harvest'] == 'ICE'
        assert item['origin_processed'] == 'CHN'
        assert item['freeze_cycle'] == 'TWICE'
    
    def test_country_abbreviations(self):
        """Short country abbreviations work"""
        item = parse("POLLOCK FIL PROC CHN 6OZ")
        assert item['origin_processed'] == 'CHN'
    
    def test_salmon_fresh_no_freeze(self):
        """Fresh salmon has no freeze cycle even with processing country"""
        item = parse("SALMON FIL FRESH PRODUCT OF NORWAY, PROCESSED NORWAY 6OZ")
        assert item['freeze_cycle'] is None


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
