# -*- coding: utf-8 -*-

EXCLUDE_NAMES = {
    "site", "venv", ".venv", "env", ".env", "node_modules", ".git",
    "__pycache__", ".mypy_cache", ".pytest_cache", ".ruff_cache", ".cache",
    "Makefile", "index.html", "_staging", "pnpmd.map", "requirements.txt",
    "gpt5push.sh",
}

MIRROR_EXTS = {
    ".md",
    ".markdown",
    ".html",
    ".htm",
    ".yaml",
    ".yml",
    ".pandoc.md",
    ".txt",
}

MD_EXTS = {".md", ".markdown", ".pandoc.md"}

DEFAULT_JOURNAL = "Preferred Frame"
