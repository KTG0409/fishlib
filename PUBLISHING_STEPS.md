# fishlib Publishing Workflow

## Prerequisites
- WSL environment (Ubuntu) — required for building on Windows with Device Guard
- PyPI account with API token
- GitHub account with PAT (personal access token)

## Publishing Steps

### 1. Update Version
```bash
cd "/mnt/c/Users/kmort/OneDrive/Documents/libraries/fishlib-main"
sed -i 's/version="OLD"/version="NEW"/' setup.py
sed -i 's/__version__ = "OLD"/__version__ = "NEW"/' fishlib/__init__.py
```

### 2. Check the Fish
```bash
head -1 README.md
# Should show: # fishlib 🐟
# If garbled: sed -i '1s/.*/# fishlib 🐟/' README.md
```

### 3. Build
```bash
rm -rf dist/ build/ *.egg-info fishlib.egg-info
python3 -m build
twine check dist/*
```

### 4. Test Install
```bash
pip install dist/fishlib-X.Y.Z-py3-none-any.whl --break-system-packages --force-reinstall
python3 -c "import fishlib; print(fishlib.__version__)"
```

### 5. Upload to PyPI
```bash
twine upload dist/*
```

### 6. Push to GitHub
```bash
cd "/mnt/c/Users/kmort/OneDrive/Documents/libraries"
rm -rf git-temp
git clone https://github.com/KTG0409/fishlib.git git-temp
cp -r fishlib-main/* git-temp/
cd git-temp
head -1 README.md  # Check the fish!
git add -A
git commit -m "vX.Y.Z: description of changes"
git tag vX.Y.Z
git push origin main && git push origin vX.Y.Z
cd ..
rm -rf git-temp
```

## Troubleshooting

### Fish emoji garbled after build
```bash
head -1 README.md
# If you see ðŸŸ instead of 🐟:
sed -i '1s/.*/# fishlib 🐟/' README.md
```

### Cached .pyc files causing old code to run
```bash
find fishlib/ -name "*.pyc" -delete
find fishlib/ -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null
pip install dist/fishlib-X.Y.Z-py3-none-any.whl --break-system-packages --force-reinstall
```

### OneDrive renames git-temp folder
```bash
# Check for renamed folder
ls "/mnt/c/Users/kmort/OneDrive/Documents/libraries/" | grep git
# Remove it and reclone
rm -rf "/mnt/c/Users/kmort/OneDrive/Documents/libraries/git-temp*"
```
