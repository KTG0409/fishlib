"""
fishlib test suite — covers all features through v0.4.3

Run: python -m pytest tests/ -v
  or: python tests/test_fishlib.py
"""
import sys
import os

# Allow running directly
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fishlib.parser import parse
from fishlib.matcher import comparison_key, match, is_comparable

passed = 0
failed = 0
errors = []

def test(name, condition, detail=''):
    global passed, failed, errors
    if condition:
        passed += 1
    else:
        failed += 1
        errors.append(f'{name} {detail}')
        print(f'  ❌ {name} {detail}')


# =========================================================================
# v0.1.0 — CORE PARSING
# =========================================================================
print('=' * 70)
print('  v0.1.0 CORE PARSING')
print('=' * 70)

item = parse('SALMON FIL ATL SKON DTRM 6OZ IVP')
test('Salmon species', item['species'] == 'Atlantic Salmon')
test('Salmon form', item['form'] == 'FIL')
test('Salmon skin', item['skin'] == 'SKON')
test('Salmon trim D', item['trim'] == 'D')
test('Salmon size', item['size'] == '6OZ')
test('Salmon pack', item['pack'] == 'IVP')

item = parse('COD FIL ATL BNLS SKLS 4OZ')
test('Cod species', item['species'] == 'Atlantic Cod')
test('Cod bone', item['bone'] == 'BNLS')

item = parse('SHRIMP 16/20 PD TAIL ON')
test('Shrimp category', item['category'] == 'shrimp')
test('Shrimp count', item['count'] == '16/20')

item = parse('SCALLOP SEA U10 DRY')
test('Sea scallop', item['species'] == 'Sea Scallop')

item = parse('LOBSTER TAIL WARM WATER 8OZ')
test('Lobster category', item['category'] == 'lobster')

# Matcher basics
result = match('SALMON FIL ATL 6OZ', 'SALMON FIL ATL 6OZ')
test('Exact match comparable', result['is_comparable'] is True)

result = match('SALMON FIL ATL 6OZ', 'COD FIL ATL 6OZ')
test('Different species blocks', result['is_comparable'] is False)


# =========================================================================
# v0.2.0 — MEAT GRADE, PREPARATION, VALUE-ADDED, NEW SPECIES
# =========================================================================
print()
print('=' * 70)
print('  v0.2.0 MEAT GRADE, PREPARATION, VALUE-ADDED')
print('=' * 70)

item = parse('CRAB MEAT JUMBO LUMP PASTEURIZED')
test('Meat grade jumbo lump', item['meat_grade'] == 'JUMBO_LUMP')

item = parse('SHRIMP 16/20 P&D COOKED')
test('Preparation cooked', item['preparation'] == 'COOKED')

item = parse('COD FIL PANKO CRUSTED 4OZ')
test('Value-added breaded', item['value_added'] == 'BREADED')

item = parse('SALMON FIL SMOKED 4OZ')
test('Preparation smoked', item['preparation'] == 'SMOKED')

# New species from v0.2.0
item = parse('SNAPPER RED FIL 8OZ')
test('Red snapper', item['species'] == 'Red Snapper')

item = parse('GROUPER RED FIL 8OZ')
test('Red grouper', item['species'] == 'Red Grouper')

item = parse('BRANZINO WHL 1LB')
test('Branzino', item['category'] == 'branzino')

item = parse('CHILEAN SEA BASS FIL 8OZ')
test('Chilean sea bass', item['species'] == 'Chilean Sea Bass (Patagonian Toothfish)')

item = parse('TROUT RAINBOW FIL 6OZ')
test('Rainbow trout', item['species'] == 'Rainbow Trout')

item = parse('BARRAMUNDI FIL 6OZ')
test('Barramundi', item['category'] == 'barramundi')

item = parse('WAHOO STEAK 8OZ')
test('Wahoo', item['category'] == 'wahoo')

item = parse('MONKFISH TAIL 8OZ')
test('Monkfish', item['category'] == 'monkfish')

# Species priority: category name beats alias-only
item = parse('COD ATLANTIC FIL 4OZ')
test('COD ATLANTIC = cod not salmon', item['category'] == 'cod')

# Caviar lumpfish should NOT trigger meat_grade=LUMP
item = parse('CAVIAR LUMPFISH 2OZ')
test('Lumpfish no meat grade', item['meat_grade'] is None)


# =========================================================================
# v0.3.0 — 14 NEW SPECIES
# =========================================================================
print()
print('=' * 70)
print('  v0.3.0 NEW SPECIES')
print('=' * 70)

for species, cat in [
    ('ANCHOVY FIL', 'anchovy'), ('WHITING FIL 4OZ', 'whiting'),
    ('PERCH FIL 6OZ', 'perch'), ('SARDINE CANNED', 'sardine'),
    ('HERRING FIL', 'herring'), ('MACKEREL FIL 6OZ', 'mackerel'),
    ('HAKE FIL 4OZ', 'hake'), ('ORANGE ROUGHY FIL 6OZ', 'orange_roughy'),
    ('CORVINA FIL 6OZ', 'corvina'), ('COBIA STEAK 8OZ', 'cobia'),
    ('LANGOSTINO TAIL', 'langostino'), ('CONCH MEAT', 'conch'),
    ('HAMACHI LOIN', 'hamachi'), ('PIKE FIL 6OZ', 'pike'),
]:
    item = parse(species)
    test(f'{species:25s} → {cat}', item['category'] == cat, f'got {item["category"]}')


# =========================================================================
# v0.4.0 — ORIGIN SPLIT + FREEZE CYCLE
# =========================================================================
print()
print('=' * 70)
print('  v0.4.0 ORIGIN SPLIT + FREEZE CYCLE')
print('=' * 70)

# Dual origin
item = parse('POLLOCK FIL WILD ALASKA PROCESSED IN CHINA 6OZ')
test('Dual: harvest=USA', item['origin_harvest'] == 'USA')
test('Dual: processed=CHN', item['origin_processed'] == 'CHN')
test('Dual: freeze=TWICE', item['freeze_cycle'] == 'TWICE')

item = parse('COD FIL PRODUCT OF USA, PROC CHINA 4OZ')
test('Comma dual harvest', item['origin_harvest'] == 'USA')
test('Comma dual processed', item['origin_processed'] == 'CHN')

item = parse('COD LOIN CAUGHT NORWAY/PROCESSED VIETNAM 8OZ')
test('Slash dual: NOR/VNM', item['origin_harvest'] == 'NOR')

# Single origin
item = parse('SALMON FIL PRODUCT OF NORWAY 8OZ')
test('Harvest only NOR', item['origin_harvest'] == 'NOR')

item = parse('POLLOCK FIL PROCESSED IN CHINA 6OZ')
test('Processed only CHN', item['origin_processed'] == 'CHN')
test('Processed only no harvest', item['origin_harvest'] is None)

# Freeze cycle logic
item = parse('TILAPIA FIL PRODUCT OF CHINA, PROCESSED CHINA 5OZ')
test('Tilapia domestic China=SINGLE', item['freeze_cycle'] == 'SINGLE')

item = parse('SHRIMP 16/20 PROCESSED IN CHINA')
test('Shrimp exempt from freeze', item['freeze_cycle'] is None)

item = parse('SALMON FIL FRESH 8OZ')
test('Fresh = no freeze cycle', item['freeze_cycle'] is None)

# Freeze cycle hard block in matcher
result = match(
    parse('POLLOCK FIL WILD ALASKA PROCESSED IN CHINA 6OZ'),
    parse('POLLOCK FIL WILD ALASKA PROCESSED IN USA 6OZ'))
test('Freeze cycle hard block', result['is_comparable'] is False)

# Legacy origin field
item = parse('POLLOCK FIL WILD ALASKA PROCESSED IN CHINA 6OZ')
test('Legacy origin = harvest', item['origin'] == 'USA')


# =========================================================================
# v0.4.2 — SIZE BUCKETS
# =========================================================================
print()
print('=' * 70)
print('  v0.4.2 SIZE BUCKETS')
print('=' * 70)

# Ounce buckets
for size, expected in [
    ('1OZ', '1-2OZ'), ('2OZ', '2-3OZ'), ('3OZ', '3-4OZ'),
    ('4OZ', '4-5OZ'), ('5OZ', '5-6OZ'), ('6OZ', '6-8OZ'),
    ('8OZ', '8-10OZ'), ('10OZ', '10-12OZ'), ('12OZ', '12-16OZ'),
    ('16OZ', '16OZ+'),
]:
    item = parse(f'SALMON FIL {size}')
    test(f'{size} → {expected}', item['size_bucket'] == expected, f'got {item["size_bucket"]}')

# Range buckets
item = parse('SALMON FIL 2-3OZ')
test('2-3OZ range → 2-3OZ', item['size_bucket'] == '2-3OZ')

item = parse('SALMON FIL 5-7OZ')
test('5-7OZ range → 6-8OZ (midpoint=6)', item['size_bucket'] == '6-8OZ')

# Pound buckets
item = parse('SALMON FIL 3LB')
test('3LB → 3-4LB', item['size_bucket'] == '3-4LB')

item = parse('SALMON FIL 3-4LB')
test('3-4LB → 3-4LB', item['size_bucket'] == '3-4LB')

item = parse('SALMON FIL 10LB')
test('10LB → 9LB+', item['size_bucket'] == '9LB+')

# Raw size preserved
item = parse('SALMON FIL 2OZ')
test('Raw size preserved', item['size'] == '2OZ')

# No size = no bucket
item = parse('SALMON FIL ATL')
test('No size → None bucket', item['size_bucket'] is None)

# THE KEY FIX: 2OZ vs 2-3OZ now comparable
result = match('POLLOCK FIL 2OZ', 'POLLOCK FIL 2-3OZ')
test('2OZ vs 2-3OZ COMPARABLE', result['is_comparable'] is True)

result = match('SALMON FIL 8OZ', 'SALMON FIL 8-10OZ')
test('8OZ vs 8-10OZ COMPARABLE', result['is_comparable'] is True)

# Different buckets don't match
result = match('SALMON FIL 4OZ', 'SALMON FIL 8OZ')
test('4OZ vs 8OZ NOT comparable', 'size_bucket' in result['different_attributes'])


# =========================================================================
# v0.4.3 — ROCKFISH, STRIPED BASS, CATFISH, SCALLOP FIXES
# =========================================================================
print()
print('=' * 70)
print('  v0.4.3 ROCKFISH / STRIPED BASS / CATFISH / SCALLOP')
print('=' * 70)

# --- Rockfish is NOT striped bass ---
for desc in [
    'ROCKFISH FIL SKLS BNLS 3-5 OZ', 'ROCKFISH FIL PAC SKLS 8/UP',
    'ROCKFISH WHL RND 1-2LB FRSH', 'ROCKFISH FILET BRD 1-2 HONEY',
    'ROCKFISH FILET FRESH', 'ROCKFISH FIL LL SKIN OFF 5-8 Z',
]:
    item = parse(desc)
    test(f'{desc[:40]:40s} → rockfish', item['category'] == 'rockfish', f'got {item["category"]}')

# --- Striped bass reversed word order ---
for desc in [
    'BASS STRIPED WILD FIL SKON 3-5', 'BASS STRIPED HYBRID FIL',
    'BASS STRIPED WILD WHL', 'BASS STRIPED FIL FARM SKON MEX',
    'BASS STRIPED WHL FRSH 2-4#',
]:
    item = parse(desc)
    test(f'{desc[:40]:40s} → Striped Bass', item['species'] == 'Striped Bass', f'got {item["species"]}')

# Original patterns still work
item = parse('STRIPED BASS FIL 6OZ')
test('STRIPED BASS still works', item['species'] == 'Striped Bass')

item = parse('STRIPER FIL 8OZ')
test('STRIPER still works', item['species'] == 'Striped Bass')

# --- Catfish: domestic vs channel vs blue ---
item = parse('CATFISH FIL SHANK 7-9 OZ USA')
test('CATFISH USA → domestic', item['subspecies'] == 'domestic')
test('CATFISH USA → US Farm-Raised', item['species'] == 'US Farm-Raised Catfish')

item = parse('CATFISH FIL 5-7OZ CHINA')
test('CATFISH CHINA → channel', item['subspecies'] == 'channel')

item = parse('CATFISH FIL 5-7OZ CHI')
test('CATFISH CHI → channel', item['subspecies'] == 'channel')

item = parse('CATFISH FILET CHINESE 7-9 OZ')
test('CATFISH CHINESE → channel', item['subspecies'] == 'channel')

item = parse('CATFISH FIL FARMED FRSH 7-9OZ')
test('CATFISH FARMED → domestic', item['subspecies'] == 'domestic')

item = parse('CATFISH FIL WLD BLUE 6-8OZ BLK')
test('CATFISH WLD BLUE → blue', item['subspecies'] == 'blue')

item = parse('CATFISH FIL 5-7 OZ')
test('CATFISH no origin → None', item['subspecies'] is None)

# --- Scallop SEA false match fix ---
item = parse('BASS SEA FILET STRIPED FRESH')
test('BASS SEA STRIPED ≠ scallop', item['category'] != 'scallop')

item = parse('SCALLOP SEA U10 DRY')
test('SCALLOP SEA still works', item['species'] == 'Sea Scallop')

item = parse('SEA SCALLOP 10/20')
test('SEA SCALLOP works', item['species'] == 'Sea Scallop')

item = parse('DIVER SCALLOP U10')
test('DIVER SCALLOP works', item['species'] == 'Sea Scallop')

item = parse('SCALLOP BAY 40/60')
test('BAY SCALLOP unaffected', item['species'] == 'Bay Scallop')

# --- Pangasius STRIPED should NOT be striped bass ---
item = parse('PANGASIUS STRIPED FIL 7-9 OZ')
test('PANGASIUS STRIPED → swai', item['category'] == 'swai')

item = parse('SWAI FIL 5-7 OZ')
test('SWAI still works', item['category'] == 'swai')


# =========================================================================
# SUMMARY
# =========================================================================
print()
print('=' * 70)
print(f'  TOTAL: {passed} passed, {failed} failed')
print('=' * 70)
if errors:
    print('  FAILURES:')
    for e in errors:
        print(f'    ❌ {e}')
else:
    print('  ✅ ALL TESTS PASSED')


if __name__ == '__main__':
    sys.exit(0 if failed == 0 else 1)
