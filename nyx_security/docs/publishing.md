# Publishing nyx-security to PyPI

This guide explains how to publish your nyx-security package to PyPI (Python Package Index) so others can install it using pip.

## Prerequisites

1. Create a PyPI account at [https://pypi.org/account/register/](https://pypi.org/account/register/)
2. Install the required tools:
   ```bash
   pip install build twine
   ```

## One-time Setup

### Create a PyPI API Token

1. Log in to your PyPI account
2. Go to Account Settings → API tokens
3. Create a new API token with the scope "Entire account"
4. Save this token securely - you'll only see it once!

### Configure your credentials

Create or edit the file `~/.pypirc`:

```ini
[pypi]
username = __token__
password = pypi-your-token-here
```

Make sure to replace `pypi-your-token-here` with your actual token.

## Preparing Your Package

Your package should already have the following files:

- `setup.py` - Package metadata and dependencies
- `README.md` - Package description
- `LICENSE` - License information
- Your package code in the `nyx_security` directory

### Create additional files for PyPI

1. Create a `MANIFEST.in` file to include non-Python files:

```
include LICENSE
include README.md
recursive-include docs *.md
```

2. Create a `pyproject.toml` file:

```toml
[build-system]
requires = ["setuptools>=42", "wheel"]
build-backend = "setuptools.build_meta"
```

## Building and Publishing

### Build the package

```bash
python -m build
```

This will create distribution packages in the `dist/` directory.

### Upload to PyPI

```bash
python -m twine upload dist/*
```

You'll be prompted for your username and password. Use `__token__` as the username and your PyPI token as the password.

## Automating with GitHub Actions

You can automate the publishing process using GitHub Actions. Create a file `.github/workflows/publish.yml`:

```yaml
name: Publish to PyPI

on:
  release:
    types: [created]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.x'
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install build twine
    - name: Build and publish
      env:
        TWINE_USERNAME: ${{ secrets.PYPI_USERNAME }}
        TWINE_PASSWORD: ${{ secrets.PYPI_PASSWORD }}
      run: |
        python -m build
        twine upload dist/*
```

Then, in your GitHub repository:

1. Go to Settings → Secrets and variables → Actions
2. Add two secrets:
   - `PYPI_USERNAME`: Set to `__token__`
   - `PYPI_PASSWORD`: Set to your PyPI token

Now, whenever you create a new release in GitHub, it will automatically build and publish your package to PyPI.

## Updating Your Package

To update your package:

1. Update the version number in `setup.py`
2. Make your code changes
3. Build and upload again using the same commands:

```bash
python -m build
python -m twine upload dist/*
```

Or if you're using GitHub Actions, just create a new release.

## Installing Your Published Package

Once published, anyone can install your package using:

```bash
pip install nyx-security
```

## Testing Before Publishing

You can test your package locally before publishing:

```bash
pip install -e .
```

This installs your package in "editable" mode, so you can make changes without reinstalling.

You can also use TestPyPI for testing the publishing process:

```bash
python -m twine upload --repository testpypi dist/*
```

Then install from TestPyPI:

```bash
pip install --index-url https://test.pypi.org/simple/ nyx-security
```