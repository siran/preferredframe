# -*- coding: utf-8 -*-
import subprocess
from pathlib import Path

import env


def load_gitignored_paths() -> set[Path]:
    out = subprocess.check_output(
        ["git", "ls-files", "-i", "--exclude-standard", "--others", "--directory"],
        cwd=env.ROOT,
        text=True,
        stderr=subprocess.DEVNULL,
    )
    paths: set[Path] = set()
    for line in out.splitlines():
        line = line.strip()
        if not line:
            continue
        p = (env.ROOT / line.rstrip("/")).resolve()
        paths.add(p)
    return paths


GITIGNORED_PATHS = load_gitignored_paths()


def is_gitignored(path: Path) -> bool:
    p = path.resolve()
    for ign in GITIGNORED_PATHS:
        try:
            p.relative_to(ign)
            return True
        except ValueError:
            continue
    return False
