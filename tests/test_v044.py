"""
fishlib v0.4.4 - Validation test suite
Run from repo root: pytest tests/test_v044.py -v
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
import fishlib

def p(desc):
    return fishlib.parse(desc)

# ── SPECIES: previously failing items from real Sysco data ───────────────────

def test_bronzini_spelling():
    assert p("BRONZINI WHL SCALED & GTTD FRZ")['species'] == "Branzino (European Sea Bass)"

def test_bronzino_spelling():
    assert p("FISH FILET BRONZINI FRSH")['species'] == "Branzino (European Sea Bass)"

def test_brnzno_abbrev():
    assert p("SEABASS FIL BRNZNO 6-8 SKON")['species'] == "Branzino (European Sea Bass)"

def test_corvina():
    assert p("CORVINA FILET SKNL/BNLS 8-10OZ")['species'] == "Corvina"

def test_hamachi():
    assert p("HAMACHI FILET SKON 4-5 LB Y-T")['species'] == "Hamachi (Yellowtail)"

def test_hamachi_loin():
    assert p("HAMACHI LOIN FRZN")['species'] == "Hamachi (Yellowtail)"

def test_orange_roughy():
    assert p("ORANGE ROUGHY FIL 6-8OZ")['species'] == "Orange Roughy"

def test_tobiko():
    assert p("CAVIAR TOBIKO BLK")['species'] == "Tobiko (Flying Fish Roe)"

def test_masago():
    assert p("CAVIAR MASAGO ORNG SMELT ROE")['species'] == "Masago (Smelt Roe)"

def test_roe_flyingfish():
    assert p("ROE FLYINGFISH ORG TOBIKO")['species'] == "Tobiko (Flying Fish Roe)"

def test_conch():
    assert p("CONCH FRTTR RAW BTR")['species'] == "Queen Conch"

def test_conch_meat():
    assert p("CONCH MEAT 100% CLEANED")['species'] == "Queen Conch"

def test_smelt():
    assert p("SMELT WHL FRZN")['species'] == "Smelt"

def test_capelin_as_smelt():
    assert p("FISH FOOD CAPELIN")['species'] == "Smelt"

def test_mackerel():
    assert p("MACKEREL FILET HOT SMKD PEPPRD")['species'] is not None

def test_whiting():
    assert p("WHITING FIL 4-6 OZ IQF")['species'] == "Whiting"

def test_hake():
    assert p("HAKE FILLET 6-8OZ SP SKLS/BL")['species'] == "Hake"

def test_cape_hake():
    assert p("CAPE HAKE LOIN 3 OZ")['species'] == "Cape Hake"

def test_capensis():
    assert p("CAPE CAPENSIS FIL 2-4OZ SKLS")['species'] == "Cape Hake"

def test_perch_yellow():
    assert p("PERCH FIL MICHIGAN BFLYD FRZ")['species'] is not None

def test_perch_zander():
    assert p("PIKE PERCH FIL ZANDER 4-6 OZ")['species'] == "Pike Perch (Zander)"

def test_zander():
    assert p("ZANDER FIL 40-60GM IQF")['species'] == "Pike Perch (Zander)"

def test_amberjack_kanpachi():
    assert p("AMBERJACK FIL KANPACHI 8-12 OZ")['species'] == "Kanpachi (Amberjack)"

def test_unagi():
    assert p("UNAGI EEL KABAYAKI 11OZ FRZN")['species'] == "Unagi (Freshwater Eel)"

def test_eel():
    assert p("EEL SMOKED BBQ UNAGI 10 OZ")['species'] == "Unagi (Freshwater Eel)"

def test_escolar():
    assert p("ESCOLAR FIL SAKU BLOCK")['species'] == "Escolar"

def test_arctic_char():
    assert p("CHAR ARCTIC FIL 12-16 OZ FRZN")['species'] == "Arctic Char"

def test_cobia():
    assert p("COBIA FIL 6-8OZ IQF SKOF")['species'] == "Cobia"

def test_langostino():
    assert p("LANGOSTINO IQF MEAT")['species'] == "Langostino"

def test_pompano():
    assert p("POMPANO WHL GOLDEN")['species'] == "Pompano"

def test_redfish():
    assert p("REDFISH FIL 6-8 OZ SKLS")['species'] == "Redfish (Red Drum)"

def test_tripletail():
    assert p("TRIPLETAIL FIL BL/SL 8-16OZ WILD")['species'] == "Tripletail"

def test_sea_urchin():
    assert p("SEA URCHIN UNI BROKEN FRZN")['species'] == "Sea Urchin (Uni)"

def test_sardine():
    assert p("SARDINE WHOLE FRZN")['species'] == "Sardine"

def test_pangasius():
    assert p("PANGASIUS FIL 7-9OZ VIETNAM")['species'] == "Pangasius"

# ── FALSE POSITIVES: these should NOT match fish species ─────────────────────

def test_no_alligator():
    assert p("ALLIGATOR MEAT FRZN BABY BCK R")['species'] is None

def test_no_frog_leg():
    assert p("FROG LEG 4/6 FRZN")['species'] is None

def test_no_seaweed():
    assert p("SALAD SEAWEED CHUCKA WILD VEG")['species'] is None

def test_no_sample():
    assert p("SAMPLE SEAFOOD FRZN")['species'] is None

def test_no_new_england_as_gbr():
    """NEW ENGLAND must not trigger GBR country of origin"""
    result = p("SEAFOOD MIX NEW ENGLAND SKNPK")
    assert result.get('origin') != 'GBR'

def test_no_bayou_as_bay_scallop():
    """BAYOU must not trigger Bay Scallop"""
    result = p("SAUSAGE ALLIGATOR BAYOU")
    assert result.get('species') != 'Bay Scallop'

def test_no_link_as_catfish():
    """SAUSAGE ALLIGATOR LINK must not match catfish via 'US' alias"""
    result = p("SAUSAGE ALLIGATOR LINK 4 OZ")
    assert result.get('species') != 'Channel Catfish'

# ── COO: origin detection ─────────────────────────────────────────────────────

def test_coo_norwg():
    assert p("SALMON FIL BLS/SKLS 4 OZ NORWG")['origin'] == 'NOR'

def test_coo_norw():
    assert p("SALMON NORW PORT IQF 8OZ")['origin'] == 'NOR'

def test_coo_alsk():
    assert p("COD LOIN ALSK 5OZ FRZN")['origin'] == 'USA'

def test_coo_alaskan():
    assert p("SALMON BURGER 4 OZ ALASKAN")['origin'] == 'USA'

def test_coo_canadn():
    assert p("LOBSTER TAIL CANADN 7-8 OZ")['origin'] == 'CAN'

def test_coo_chln():
    assert p("SALMON ATL CHLN DTRM 3-4LB FRZ")['origin'] == 'CHL'

def test_coo_grk():
    assert p("BRONZINI FIL PBO 5-7OZ GRK IQF")['origin'] == 'GRC'

def test_coo_brazil():
    assert p("LOBSTER TAIL BRAZILIAN 5 OZ")['origin'] == 'BRA'

def test_coo_scotch():
    assert p("COD BRD RAW SCOTCH 5 1/3 OZ")['origin'] == 'SCO'

# ── CORE: regression — existing species must still work ──────────────────────

def test_salmon_atlantic():
    r = p("SALMON FIL ATL SKON DTRM 6OZ IVP")
    assert r['species'] == 'Atlantic Salmon'
    assert r['form'] == 'FIL'
    assert r['trim'] == 'D'

def test_shrimp_count():
    r = p("SHRIMP P&D 16/20 IQF")
    assert r['species'] is not None
    assert r['count'] == '16/20'

def test_snow_crab():
    assert p("CRAB CLUSTER SNOW 8-10 OZ")['species'] == 'Snow Crab'

def test_lobster_tail():
    r = p("LOBSTER TAIL 8OZ WARM WATER IQF")
    assert r['species'] is not None
    assert r['form'] == 'TAIL'

def test_version():
    assert fishlib.__version__ == "0.4.4"
