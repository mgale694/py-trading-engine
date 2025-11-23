# Code Formatting Setup

This project uses **Ruff** for automatic code formatting and linting.

## Quick Setup

```bash
# Install ruff (if not already installed)
uv pip install ruff

# Pre-commit hooks are already set up!
# They will automatically format your code before each commit.
```

## What Happens on Commit

When you run `git commit`, the pre-commit hooks will automatically:

1. **Format your code** with Ruff (fixes spacing, imports, etc.)
2. **Check for common issues** (trailing whitespace, file endings, etc.)
3. **Fix what can be fixed automatically**
4. **Stop the commit if there are issues** that need manual fixing

## Manual Usage

You can also run Ruff manually:

```bash
# Format all code
ruff format .

# Check for issues
ruff check .

# Auto-fix issues
ruff check --fix .

# Run pre-commit hooks manually
pre-commit run --all-files
```

## Configuration

- **ruff.toml** - Ruff configuration (line length: 100, Python 3.9+)
- **.pre-commit-config.yaml** - Pre-commit hooks configuration

## Bypass Hooks (Not Recommended)

If you really need to skip hooks:

```bash
git commit --no-verify
```

But please don't do this unless absolutely necessary!
