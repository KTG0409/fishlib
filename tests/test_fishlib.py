"""
Tests for fishlib v0.3.0
Run with: pytest tests/test_fishlib.py -v
"""
import pytest
import fishlib
from fishlib import parser, standards, matcher, species, reference

class TestParseBasic:
    def test_empty(self):
        assert fishlib.parse("")['error'] == 'Empty description'
    def test_salmon_full(self):
        r = fishlib.parse("SALMON FIL ATL SKON DTRM 6OZ IVP")
        assert r['category'] == 'salmon' and r['form'] == 'FIL' and r['skin'] == 'SKON' and r['trim'] == 'D'
    def test_cod_atlantic(self):
        r = fishlib.parse("COD FIL ATLANTIC BNLS SKLS 8OZ FRZ")
        assert r['category'] == 'cod' and r['bone'] == 'BNLS'
    def test_lobster_tail(self):
        r = fishlib.parse("LOBSTER TAIL MAINE 8OZ FRZ")
        assert r['category'] == 'lobster' and r['form'] == 'TAIL'

class TestSpeciesEdgeCases:
    def test_cod_not_salmon(self):
        assert fishlib.parse("COD FIL ATLANTIC")['category'] == 'cod'
    def test_sablefish(self):
        r = fishlib.parse("SABLEFISH FIL WILD AK")
        assert r['category'] == 'cod' and r['subspecies'] == 'black'
    def test_red_snapper(self):
        r = fishlib.parse("SNAPPER RED FIL WILD")
        assert r['category'] == 'snapper' and r['subspecies'] == 'red'
    def test_red_salmon(self):
        r = fishlib.parse("SALMON RED FIL WILD")
        assert r['category'] == 'salmon' and r['subspecies'] == 'sockeye'

class TestNewSpecies:
    def test_anchovy(self): assert fishlib.parse("ANCHOVY FILET IN OLIVE OIL")['category'] == 'anchovy'
    def test_whiting(self): assert fishlib.parse("WHITING BTRD PUB STY 2-3OZ")['category'] == 'whiting'
    def test_perch(self): assert fishlib.parse("PERCH FIL YELLOW LAKE")['category'] == 'perch'
    def test_sardine(self): assert fishlib.parse("SARDINE SKLS/BNLS OLIVE OIL")['category'] == 'sardine'
    def test_herring(self): assert fishlib.parse("HERRING IN WINE SAUCE")['category'] == 'herring'
    def test_mackerel(self): assert fishlib.parse("MACKEREL FILET SMKD")['category'] == 'mackerel'
    def test_hake(self): assert fishlib.parse("HAKE PRT TACO CUT 1.75 OZ")['category'] == 'hake'
    def test_cape_hake(self):
        r = fishlib.parse("CAPE HAKE CHD BISCT BRD GF 4OZ")
        assert r['category'] == 'hake' and r['subspecies'] == 'cape'
    def test_orange_roughy(self): assert fishlib.parse("ORANGE ROUGHY FIL 6-8 FRZN")['category'] == 'orange_roughy'
    def test_corvina(self): assert fishlib.parse("CORVINA FIL WILD 6OZ")['category'] == 'corvina'
    def test_cobia(self): assert fishlib.parse("COBIA FIL FARM 8OZ")['category'] == 'cobia'
    def test_langostino(self): assert fishlib.parse("LANGOSTINO TAIL MEAT")['category'] == 'langostino'
    def test_conch(self): assert fishlib.parse("CONCH MEAT TENDERIZE")['category'] == 'conch'
    def test_hamachi(self): assert fishlib.parse("HAMACHI LOIN SASHIMI GRADE")['category'] == 'hamachi'
    def test_pike(self): assert fishlib.parse("PIKE FIL WALLEYE")['category'] == 'pike'
    def test_bronzini(self): assert fishlib.parse("BRONZINI FIL PBO 5-7OZ")['category'] == 'branzino'

class TestBugFixes:
    def test_raw_vs_cooked(self):
        assert fishlib.match('SHRIMP 16/20 RAW', 'SHRIMP 16/20 COOKED')['is_comparable'] is False
    def test_breaded_vs_plain(self):
        assert fishlib.match('COD FIL 6OZ', 'COD FIL BREADED 6OZ')['is_comparable'] is False
    def test_tail_on_not_form(self):
        r = fishlib.parse('SHRIMP 21/25 COOKED P&D TAIL ON')
        assert r['form'] != 'TAIL' and r['shrimp_form'] == 'TAIL_ON'
    def test_pd_detected(self):
        assert fishlib.parse('SHRIMP 16/20 P&D RAW IQF')['shrimp_form'] == 'P&D'
    def test_lobster_tail_ok(self):
        assert fishlib.parse('LOBSTER TAIL MAINE 8OZ')['form'] == 'TAIL'
    def test_lumpfish(self):
        assert fishlib.parse('CAVIAR LUMPFISH BLACK')['meat_grade'] is None

class TestSmashedCodes:
    def test_bnlskl(self): assert fishlib.parse('MAHI MAHI PRTN BNLSKL 6 OZ')['bone'] == 'BNLS'
    def test_skoncan(self): assert fishlib.parse('SALMON ATL FIL 4-5LBSKONCAN FZ')['skin'] == 'SKON'
    def test_ckd_count(self): assert fishlib.parse('SHRIMP WHT P&D TLOF CKD100/150')['preparation'] == 'COOKED'

class TestNewAliases:
    def test_dtrim(self): assert fishlib.parse('SALMON FIL SKON DTRIM CANADA')['trim'] == 'D'
    def test_d_slash_trim(self): assert fishlib.parse('SALMON ATL FIL D/TRIM ARKA')['trim'] == 'D'
    def test_prckd(self): assert fishlib.parse('POLLOCK FLT PRCKD POT CRUN')['preparation'] == 'COOKED'
    def test_smkd(self): assert fishlib.parse('SALMON SMKD SCOTTISH PREM')['preparation'] == 'SMOKED'
    def test_crispanko(self): assert fishlib.parse('COD FIL CRISPANKO 2.5-3.5 OZ')['value_added'] == 'BREADED'
    def test_popcrn(self): assert fishlib.parse('SHRIMP BRD POPCRN TAIL OFF')['value_added'] == 'BREADED'
    def test_saku(self): assert fishlib.parse('TUNA YELLOWFIN 8OZ SAKU BLOCKS')['cut_style'] == 'SAKU'
    def test_xtbias(self): assert fishlib.parse('SALMON PRTN SKON XTBIAS 4OZ')['cut_style'] == 'BIAS'

class TestShrimpForm:
    def test_pd(self): assert fishlib.parse('SHRIMP 16/20 P&D RAW')['shrimp_form'] == 'P&D'
    def test_shell_on(self): assert fishlib.parse('SHRIMP 21/25 SHELL ON')['shrimp_form'] == 'SHELL_ON'
    def test_ez_peel(self): assert fishlib.parse('SHRIMP 16/20 EZ PEEL')['shrimp_form'] == 'TAIL_ON'
    def test_tail_off(self): assert fishlib.parse('SHRIMP 16/20 TAIL OFF CKD')['shrimp_form'] == 'TAIL_OFF'
    def test_tlof(self): assert fishlib.parse('SHRIMP WHT P&D TLOF CKD')['shrimp_form'] == 'TAIL_OFF'
    def test_pud(self): assert fishlib.parse('SHRIMP 21/25 PUD RAW')['shrimp_form'] == 'PUD'

class TestStandardize:
    def test_form(self): assert fishlib.standardize_form("FILLET") == "FIL"
    def test_skin(self): assert fishlib.standardize_skin("SKIN ON") == "SKON"
    def test_trim(self): assert fishlib.standardize_trim("DTRM") == "D"
    def test_meat_grade(self): assert fishlib.standardize_meat_grade("JUMBO LUMP") == "JUMBO_LUMP"
    def test_prep(self): assert fishlib.standardize_preparation("LOX") == "CURED"
    def test_va(self): assert fishlib.standardize_value_added("PANKO") == "BREADED"

class TestMatcher:
    def test_same_item(self):
        r = fishlib.match("SALMON FIL ATL SKON DTRM 6OZ", "SALMON FILLET ATLANTIC SKIN ON D TRIM 6 OZ")
        assert r['is_comparable'] is True and r['confidence'] >= 0.9
    def test_diff_species(self):
        assert fishlib.match("SALMON FIL ATL 6OZ", "COD FIL ATL 6OZ")['is_comparable'] is False
    def test_key_has_shrimp_form(self):
        assert 'P&D' in fishlib.comparison_key(fishlib.parse('SHRIMP 16/20 P&D RAW'))

class TestSpeciesModule:
    def test_45_categories(self): assert len(fishlib.species.list_species()) == 45
    def test_new_cats(self):
        cats = fishlib.species.list_species()
        for c in ['anchovy','whiting','perch','sardine','herring','mackerel',
                   'hake','orange_roughy','corvina','cobia','langostino','conch','hamachi','pike']:
            assert c in cats
    def test_price_tiers(self):
        assert fishlib.species.get_price_tier('salmon', 'king') == 'ultra-premium'

class TestReference:
    def test_trim_skin(self):
        for l in ['A','B','C','D']: assert reference.is_trim_skin_on(l) is True
        assert reference.is_trim_skin_on('E') is False
    def test_foodservice(self):
        assert reference.is_foodservice_trim('D') is True
        assert reference.is_foodservice_trim('A') is False

if __name__ == '__main__':
    pytest.main([__file__, '-v'])
