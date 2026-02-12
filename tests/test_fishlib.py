"""
Tests for fishlib v0.2.0

Run with: pytest tests/test_fishlib.py -v
"""

import pytest
import fishlib
from fishlib import parser, standards, matcher, species, reference


# =============================================================================
# PARSER TESTS
# =============================================================================

class TestParseBasic:
    """Test basic parsing functionality."""
    
    def test_empty_description(self):
        result = fishlib.parse("")
        assert result.get('error') == 'Empty description'
    
    def test_salmon_full_description(self):
        result = fishlib.parse("SALMON FIL ATL SKON DTRM 6OZ IVP")
        assert result['category'] == 'salmon'
        assert result['subspecies'] == 'atlantic'
        assert result['form'] == 'FIL'
        assert result['skin'] == 'SKON'
        assert result['trim'] == 'D'
        assert result['size'] == '6OZ'
        assert result['pack'] == 'IVP'
    
    def test_cod_atlantic(self):
        result = fishlib.parse("COD FIL ATLANTIC BNLS SKLS 8OZ FRZ")
        assert result['category'] == 'cod'
        assert result['subspecies'] == 'atlantic'
        assert result['form'] == 'FIL'
        assert result['bone'] == 'BNLS'
        assert result['skin'] == 'SKLS'
        assert result['size'] == '8OZ'
        assert result['storage'] == 'FRZ'
    
    def test_lobster_tail(self):
        result = fishlib.parse("LOBSTER TAIL MAINE 8OZ FRZ")
        assert result['category'] == 'lobster'
        assert result['subspecies'] == 'maine'
        assert result['form'] == 'TAIL'
        assert result['size'] == '8OZ'
    
    def test_halibut_steak(self):
        result = fishlib.parse("HALIBUT STEAK PAC WILD 8OZ")
        assert result['category'] == 'halibut'
        assert result['subspecies'] == 'pacific'
        assert result['form'] == 'STEAK'
        assert result['harvest'] == 'WILD'
    
    def test_parse_description_alias(self):
        """parse_description should be identical to parse."""
        r1 = fishlib.parse("SALMON FIL ATL 6OZ")
        r2 = fishlib.parse_description("SALMON FIL ATL 6OZ")
        assert r1 == r2


class TestParseSpecies:
    """Test species extraction edge cases."""
    
    def test_cod_not_salmon_when_cod_in_text(self):
        """COD ATLANTIC should be cod, not salmon (ATL is also a salmon alias)."""
        result = fishlib.parse("COD FIL ATLANTIC")
        assert result['category'] == 'cod'
    
    def test_sablefish_maps_to_black_cod(self):
        """SABLEFISH has no 'COD' in text but should match via alias."""
        result = fishlib.parse("SABLEFISH FIL WILD AK")
        assert result['category'] == 'cod'
        assert result['subspecies'] == 'black'
    
    def test_red_snapper_not_red_salmon(self):
        result = fishlib.parse("SNAPPER RED FIL WILD")
        assert result['category'] == 'snapper'
        assert result['subspecies'] == 'red'
    
    def test_red_salmon_is_sockeye(self):
        result = fishlib.parse("SALMON RED FIL WILD")
        assert result['category'] == 'salmon'
        assert result['subspecies'] == 'sockeye'
    
    def test_mahi_mahi(self):
        result = fishlib.parse("MAHI FIL WILD 6OZ")
        assert result['category'] == 'mahi'
    
    def test_branzino(self):
        result = fishlib.parse("BRANZINO WHL FARM")
        assert result['category'] == 'branzino'
    
    def test_chilean_sea_bass(self):
        result = fishlib.parse("SEA BASS CHILEAN FIL 8OZ")
        assert result['category'] == 'sea_bass'
        assert result['subspecies'] == 'chilean'
    
    def test_new_species_snapper(self):
        result = fishlib.parse("SNAPPER YELLOWTAIL FIL")
        assert result['category'] == 'snapper'
        assert result['subspecies'] == 'yellowtail'
    
    def test_new_species_grouper(self):
        result = fishlib.parse("GROUPER RED FIL WILD")
        assert result['category'] == 'grouper'
        assert result['subspecies'] == 'red'
    
    def test_new_species_monkfish(self):
        result = fishlib.parse("MONKFISH TAIL WILD")
        assert result['category'] == 'monkfish'
    
    def test_new_species_crawfish(self):
        result = fishlib.parse("CRAWFISH TAIL MEAT COOKED")
        assert result['category'] == 'crawfish'


class TestParseSizes:
    """Test size extraction."""
    
    def test_oz_no_space(self):
        result = fishlib.parse("SALMON FIL 6OZ")
        assert result['size'] == '6OZ'
    
    def test_oz_with_space(self):
        result = fishlib.parse("SALMON FIL 6 OZ")
        assert result['size'] == '6OZ'
    
    def test_oz_range(self):
        result = fishlib.parse("SALMON FIL 5-7 OZ")
        assert result['size'] == '5-7OZ'
    
    def test_lb_size(self):
        result = fishlib.parse("SALMON FIL 2 LB")
        assert result['size'] == '2LB'
    
    def test_lb_range(self):
        result = fishlib.parse("SALMON FIL 3-4 LB")
        assert result['size'] == '3-4LB'


class TestParseCount:
    """Test count extraction (shrimp, scallops)."""
    
    def test_slash_count(self):
        result = fishlib.parse("SHRIMP 16/20")
        assert result['count'] == '16/20'
    
    def test_u_count(self):
        result = fishlib.parse("SHRIMP U10")
        assert result['count'] == 'U10'
    
    def test_u_slash_count(self):
        result = fishlib.parse("SCALLOP U/10")
        assert result['count'] == 'U10'


class TestParseBrand:
    """Test brand extraction."""
    
    def test_portico(self):
        result = fishlib.parse("PORTICO SALMON FIL ATL 6OZ")
        assert result['brand'] == 'Portico'
    
    def test_trident(self):
        result = fishlib.parse("TRIDENT POLLOCK FIL")
        assert result['brand'] == 'Trident'


# =============================================================================
# V0.2.0 NEW ATTRIBUTES
# =============================================================================

class TestParseMeatGrade:
    """Test meat grade extraction (new in v0.2.0)."""
    
    def test_jumbo_lump(self):
        result = fishlib.parse("CRAB MEAT JUMBO LUMP BLUE")
        assert result['meat_grade'] == 'JUMBO_LUMP'
    
    def test_claw_meat(self):
        result = fishlib.parse("CRAB CLAW MEAT BLUE")
        assert result['meat_grade'] == 'CLAW'
    
    def test_backfin(self):
        result = fishlib.parse("CRAB MEAT BACKFIN")
        assert result['meat_grade'] == 'BACKFIN'
    
    def test_special(self):
        result = fishlib.parse("CRAB MEAT SPECIAL")
        assert result['meat_grade'] == 'SPECIAL'


class TestParsePreparation:
    """Test preparation extraction (new in v0.2.0)."""
    
    def test_cooked(self):
        result = fishlib.parse("SHRIMP 16/20 COOKED P&D")
        assert result['preparation'] == 'COOKED'
    
    def test_raw(self):
        result = fishlib.parse("SHRIMP 16/20 RAW P&D")
        assert result['preparation'] == 'RAW'
    
    def test_smoked(self):
        result = fishlib.parse("SALMON FIL ATL SMOKED")
        assert result['preparation'] == 'SMOKED'
    
    def test_cured_lox(self):
        result = fishlib.parse("SALMON LOX SLICED")
        assert result['preparation'] == 'CURED'


class TestParseValueAdded:
    """Test value-added extraction (new in v0.2.0)."""
    
    def test_breaded(self):
        result = fishlib.parse("COD FIL BREADED 4OZ")
        assert result['value_added'] == 'BREADED'
    
    def test_panko(self):
        result = fishlib.parse("COD FIL PANKO 4OZ")
        assert result['value_added'] == 'BREADED'
    
    def test_teriyaki_marinated(self):
        result = fishlib.parse("SALMON PRTN TERIYAKI 6OZ")
        assert result['value_added'] == 'MARINATED'
    
    def test_blackened(self):
        result = fishlib.parse("MAHI FIL BLACKENED 6OZ")
        assert result['value_added'] == 'BLACKENED'
    
    def test_stuffed(self):
        result = fishlib.parse("SHRIMP STUFFED CRAB")
        assert result['value_added'] == 'STUFFED'
    
    def test_formed_cakes(self):
        result = fishlib.parse("CRAB CAKES 3OZ")
        assert result['value_added'] == 'FORMED'


# =============================================================================
# STANDARDIZATION TESTS
# =============================================================================

class TestStandardize:
    """Test standardization functions."""
    
    def test_form_fillet(self):
        assert fishlib.standardize_form("FILLET") == "FIL"
    
    def test_form_portion(self):
        assert fishlib.standardize_form("PORTION") == "PRTN"
    
    def test_skin_on(self):
        assert fishlib.standardize_skin("SKIN ON") == "SKON"
    
    def test_skin_less(self):
        assert fishlib.standardize_skin("SKINLESS") == "SKLS"
    
    def test_bone_less(self):
        assert fishlib.standardize_bone("BONELESS") == "BNLS"
    
    def test_trim_d(self):
        assert fishlib.standardize_trim("DTRM") == "D"
    
    def test_trim_e(self):
        assert fishlib.standardize_trim("ETRM") == "E"
    
    def test_harvest_wild(self):
        assert fishlib.standardize_harvest("WILD CAUGHT") == "WILD"
    
    def test_harvest_farm(self):
        assert fishlib.standardize_harvest("FARM RAISED") == "FARM"
    
    def test_storage_frozen(self):
        assert fishlib.standardize_storage("FROZEN") == "FRZ"
    
    def test_meat_grade_jumbo_lump(self):
        assert fishlib.standardize_meat_grade("JUMBO LUMP") == "JUMBO_LUMP"
    
    def test_preparation_cooked(self):
        assert fishlib.standardize_preparation("COOKED") == "COOKED"
    
    def test_preparation_lox(self):
        assert fishlib.standardize_preparation("LOX") == "CURED"
    
    def test_value_added_panko(self):
        assert fishlib.standardize_value_added("PANKO") == "BREADED"
    
    def test_get_standard_code(self):
        assert fishlib.get_standard_code("form", "FILLET") == "FIL"
        assert fishlib.get_standard_code("meat_grade", "JUMBO LUMP") == "JUMBO_LUMP"
    
    def test_list_codes(self):
        codes = fishlib.list_codes("meat_grade")
        assert "JUMBO_LUMP" in codes
        assert "CLAW" in codes
    
    def test_list_codes_preparation(self):
        codes = fishlib.list_codes("preparation")
        assert "RAW" in codes
        assert "COOKED" in codes
        assert "SMOKED" in codes
        assert "CURED" in codes
    
    def test_list_codes_value_added(self):
        codes = fishlib.list_codes("value_added")
        assert "BREADED" in codes
        assert "STUFFED" in codes


# =============================================================================
# MATCHER TESTS
# =============================================================================

class TestMatcher:
    """Test matching and comparison."""
    
    def test_identical_items_match(self):
        result = fishlib.match(
            "SALMON FIL ATL SKON DTRM 6OZ",
            "SALMON FIL ATL SKON DTRM 6OZ"
        )
        assert result['is_comparable'] is True
        assert result['confidence'] >= 0.9
    
    def test_same_item_different_text(self):
        result = fishlib.match(
            "SALMON FIL ATL SKON DTRM 6OZ",
            "SALMON FILLET ATLANTIC SKIN ON D TRIM 6 OZ"
        )
        assert result['is_comparable'] is True
        assert result['confidence'] >= 0.9
    
    def test_different_species_not_comparable(self):
        result = fishlib.match("SALMON FIL ATL 6OZ", "COD FIL ATL 6OZ")
        assert result['is_comparable'] is False
    
    def test_comparison_key_format(self):
        key = fishlib.comparison_key("SALMON FIL ATL SKON DTRM 6OZ")
        assert 'SALMON' in key
        assert '|' in key
    
    def test_comparison_key_includes_new_attrs(self):
        """Comparison key should include meat_grade, preparation, value_added."""
        key = fishlib.comparison_key({
            'category': 'crab',
            'form': 'MEAT',
            'meat_grade': 'JUMBO_LUMP',
            'preparation': 'RAW'
        })
        assert 'JUMBO_LUMP' in key
        assert 'RAW' in key
    
    def test_is_comparable_true(self):
        assert fishlib.is_comparable(
            "SALMON FIL ATL SKON D 6OZ",
            "SALMON FIL ATL SKON D 6OZ"
        ) is True
    
    def test_is_comparable_false(self):
        assert fishlib.is_comparable("SALMON FIL", "COD FIL") is False
    
    def test_find_matches_returns_ranked(self):
        candidates = [
            "SALMON FIL ATL SKON D 6OZ",
            "SALMON FIL ATL SKLS E 6OZ",
            "COD FIL ATL 6OZ",
        ]
        matches = fishlib.find_matches("SALMON FIL ATL SKON D 6OZ", candidates)
        assert len(matches) > 0
        # First match should be the most similar
        assert matches[0]['candidate_index'] == 0
    
    def test_match_score(self):
        score = fishlib.match_score(
            "SALMON FIL ATL SKON D 6OZ",
            "SALMON FIL ATL SKON D 6OZ"
        )
        assert score >= 0.9


# =============================================================================
# SPECIES MODULE TESTS
# =============================================================================

class TestSpeciesModule:
    """Test species module."""
    
    def test_list_categories(self):
        cats = fishlib.species.list_species()
        assert 'salmon' in cats
        assert 'crab' in cats
        assert 'snapper' in cats  # new in v0.2.0
        assert 'grouper' in cats  # new in v0.2.0
    
    def test_list_salmon_species(self):
        spp = fishlib.species.list_species('salmon')
        assert 'atlantic' in spp
        assert 'king' in spp
        assert 'sockeye' in spp
    
    def test_price_tier(self):
        assert fishlib.species.get_price_tier('salmon', 'king') == 'ultra-premium'
        assert fishlib.species.get_price_tier('salmon', 'pink') == 'economy'
        assert fishlib.species.get_price_tier('salmon', 'atlantic') == 'mid'
    
    def test_get_aliases(self):
        aliases = fishlib.species.get_aliases('salmon', 'king')
        assert 'KING' in aliases
        assert 'CHINOOK' in aliases
    
    def test_identify_species(self):
        result = fishlib.species.identify_species("SALMON SOCKEYE FIL WILD")
        assert result['category'] == 'salmon'
        assert result['subspecies'] == 'sockeye'
    
    def test_harvest_type(self):
        assert fishlib.species.get_harvest_type('salmon', 'atlantic') == 'farm'
        assert fishlib.species.get_harvest_type('salmon', 'sockeye') == 'wild'
    
    def test_compare_species_value(self):
        # King > Pink
        assert fishlib.species.compare_species_value(
            ('salmon', 'king'), ('salmon', 'pink')
        ) == 1


# =============================================================================
# REFERENCE MODULE TESTS
# =============================================================================

class TestReferenceModule:
    """Test reference data module."""
    
    def test_trim_a_through_d_skin_on(self):
        """Critical industry knowledge: Trim A-D are all skin on."""
        for level in ['A', 'B', 'C', 'D']:
            assert reference.is_trim_skin_on(level) is True, f"Trim {level} should be skin on"
    
    def test_trim_e_skin_off(self):
        """Critical: Only Trim E is skin off."""
        assert reference.is_trim_skin_on('E') is False
    
    def test_foodservice_trims(self):
        """D and E are foodservice standard."""
        assert reference.is_foodservice_trim('D') is True
        assert reference.is_foodservice_trim('E') is True
        assert reference.is_foodservice_trim('A') is False
    
    def test_trim_levels_exist(self):
        assert 'A' in reference.TRIM_LEVELS
        assert 'E' in reference.TRIM_LEVELS
        assert 'FTRIM' in reference.TRIM_LEVELS
    
    def test_cut_styles_exist(self):
        assert 'CENTER' in reference.CUT_STYLES
        assert 'BIAS' in reference.CUT_STYLES
        assert 'BLOCK' in reference.CUT_STYLES
    
    def test_meat_grades_exist(self):
        assert 'JUMBO_LUMP' in reference.MEAT_GRADES
        assert 'CLAW' in reference.MEAT_GRADES
    
    def test_preparation_exist(self):
        assert 'RAW' in reference.PREPARATION
        assert 'COOKED' in reference.PREPARATION
        assert 'SMOKED' in reference.PREPARATION
        assert 'CURED' in reference.PREPARATION
    
    def test_value_added_exist(self):
        assert 'BREADED' in reference.VALUE_ADDED
        assert 'STUFFED' in reference.VALUE_ADDED
        assert 'MARINATED' in reference.VALUE_ADDED


# =============================================================================
# BATCH PARSING
# =============================================================================

class TestBatchParsing:
    """Test batch operations."""
    
    def test_parse_batch(self):
        descriptions = [
            "SALMON FIL ATL 6OZ",
            "COD FIL PAC 8OZ",
            "SHRIMP 16/20 RAW",
        ]
        results = parser.parse_batch(descriptions)
        assert len(results) == 3
        assert results[0]['category'] == 'salmon'
        assert results[1]['category'] == 'cod'
        assert results[2]['category'] == 'shrimp'


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
