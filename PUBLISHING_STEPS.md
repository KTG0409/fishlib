# fishlib v0.2.0 — Step-by-Step Publishing Walkthrough

## What's in this folder

This is your **complete, ready-to-publish** fishlib project. Here's every file and what it does:

```
fishlib-main/
├── setup.py                        ← Tells PyPI how to install your package
├── MANIFEST.in                     ← NEW: Ensures JSON data files get included in uploads
├── README.md                       ← What people see on PyPI and GitHub
├── CHANGELOG.md                    ← NEW: Version history
├── LICENSE                         ← MIT license
│
├── fishlib/                        ← THIS IS YOUR ACTUAL PACKAGE (what gets installed)
│   ├── __init__.py                 ← Main entry point: "import fishlib"
│   ├── parser.py                   ← UPDATED: Fixed TAIL ON bug + new shrimp_form
│   ├── matcher.py                  ← UPDATED: Fixed raw/cooked + breaded/plain bugs
│   ├── standards.py                ← Standardization functions (unchanged)
│   │
│   ├── data/                       ← JSON reference data
│   │   ├── species_aliases.json    ← All 31 categories, 86 species
│   │   └── standard_codes.json     ← All code definitions
│   │
│   ├── species/
│   │   └── __init__.py             ← Species lookup functions
│   │
│   └── reference/
│       └── __init__.py             ← Industry knowledge (trim levels, cut styles, etc.)
│
└── tests/
    ├── __init__.py                 ← Empty file (makes tests a Python package)
    └── test_fishlib.py             ← NEW: 63 tests
```

### About the `__init__.py` files

Python uses `__init__.py` files to mark folders as packages. Every folder that Python
needs to import from MUST have one. They're not confusing — they're actually doing
different jobs:

- `fishlib/__init__.py` → The main one. Runs when someone does `import fishlib`
- `fishlib/species/__init__.py` → Runs when someone does `from fishlib import species`
- `fishlib/reference/__init__.py` → Runs when someone does `from fishlib import reference`
- `tests/__init__.py` → Empty. Just tells Python "this folder has test files"

---

## Step 1: Replace your local folder

On your Windows machine:

1. Navigate to: `C:\Users\kmor6669\Analysis\Code\fishlib 0.2.0\`
2. **Rename** your current `fishlib-main` folder to `fishlib-main-backup` (just in case)
3. **Copy** this entire `fishlib-main` folder there

Your old `.tar.gz` build file should still be at:
`C:\Users\kmor6669\Analysis\Code\fishlib 0.2.0\fishlib-main\dist\fishlib-0.1.0.tar.gz`

That's fine — we'll create new build files in the next steps.

---

## Step 2: Open WSL and navigate to your project

```bash
cd "/mnt/c/Users/kmor6669/Analysis/Code/fishlib 0.2.0/fishlib-main"
```

Verify you're in the right place:
```bash
ls
```
You should see: `CHANGELOG.md  fishlib/  LICENSE  MANIFEST.in  README.md  setup.py  tests/`

---

## Step 3: Clean old build artifacts

Delete old build files so they don't get mixed in:

```bash
rm -rf dist/ build/ fishlib.egg-info/
```

---

## Step 4: Install/upgrade build tools

```bash
pip install --upgrade build twine --break-system-packages
```

(You need `--break-system-packages` because of your WSL setup.)

---

## Step 5: Build the package

```bash
python -m build
```

This creates two files in a new `dist/` folder:
- `fishlib-0.2.0.tar.gz` (source distribution)
- `fishlib-0.2.0-py3-none-any.whl` (wheel — this is what pip actually installs)

---

## Step 6: Check the build

```bash
twine check dist/*
```

You should see:
```
Checking dist/fishlib-0.2.0.tar.gz: PASSED
Checking dist/fishlib-0.2.0-py3-none-any.whl: PASSED
```

If you get warnings about `long_description`, that's OK. Errors are not OK.

---

## Step 7: Test install locally

Before uploading anywhere, make sure it installs cleanly:

```bash
pip install dist/fishlib-0.2.0-py3-none-any.whl --break-system-packages --force-reinstall
```

Then test it:
```bash
python -c "
import fishlib
print(fishlib.__version__)
r = fishlib.parse('SALMON FIL ATL SKON DTRM 6OZ')
print(r['species'], r['form'], r['trim'])
r = fishlib.parse('SHRIMP 16/20 P&D RAW')
print(r['shrimp_form'])
"
```

Expected output:
```
0.2.0
Atlantic Salmon FIL D
P&D
```

---

## Step 8: Upload to PyPI

You already have your PyPI account and API token from v0.1.0. Use the same token:

```bash
twine upload dist/*
```

It will prompt you:
- **Username:** `__token__`
- **Password:** paste your PyPI API token (starts with `pypi-`)

If you saved your token in a `.pypirc` file, it should just work automatically.

After upload, verify at: https://pypi.org/project/fishlib/

---

## Step 9: Verify the PyPI install works

```bash
pip install fishlib --upgrade --break-system-packages
python -c "import fishlib; print(fishlib.__version__)"
```

Should print: `0.2.0`

---

## Step 10: Push to GitHub

```bash
cd "/mnt/c/Users/kmor6669/Analysis/Code/fishlib 0.2.0/fishlib-main"

# Stage all changes
git add -A

# Check what's being committed
git status

# Commit
git commit -m "v0.2.0: meat grade, preparation, value-added, shrimp forms, bug fixes, 19 new species"

# Tag the release
git tag v0.2.0

# Push code and tag
git push origin main
git push origin v0.2.0
```

After pushing, verify at: https://github.com/KTG0409/fishlib

---

## Step 11 (Optional): Create a GitHub Release

1. Go to https://github.com/KTG0409/fishlib/releases
2. Click **"Create a new release"**
3. Choose tag: `v0.2.0`
4. Title: `v0.2.0 — Meat Grades, Preparation, Value-Added, and Shrimp Forms`
5. Description: Copy the v0.2.0 section from CHANGELOG.md
6. Click **"Publish release"**

---

## Troubleshooting

**"Permission denied" on pip install:**
→ Add `--break-system-packages` flag (WSL/Device Guard issue)

**"File already exists" on twine upload:**
→ You can't re-upload the same version. Bump to 0.2.1 in both
   `fishlib/__init__.py` and `setup.py`, rebuild, and re-upload.

**"Invalid distribution" on twine check:**
→ Make sure `MANIFEST.in` is in the root folder (same level as `setup.py`)

**Git push rejected:**
→ Try `git pull origin main` first, then push again.

**Token expired:**
→ Go to https://pypi.org/manage/account/token/ to create a new one.
