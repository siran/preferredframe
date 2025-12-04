# pnpmd_util.py

import re
import subprocess
import sys
import time
from pathlib import Path
from typing import List, Tuple


def echo_cmd(cmd_list: List[str]):
    print("+", " ".join(_quote(x) for x in cmd_list), flush=True)


def _quote(s: str) -> str:
    import shlex
    return shlex.quote(s)


def run_visible(cmd_list: List[str], *, timeout: int = 0) -> int:
    echo_cmd(cmd_list)
    start = time.time()
    import subprocess as sp
    try:
        p = sp.Popen(cmd_list)
        while True:
            if p.poll() is not None:
                return p.returncode
            if timeout and time.time() - start > timeout:
                try:
                    p.terminate()
                    time.sleep(0.5)
                    p.kill()
                except Exception:
                    pass
                return 124
            time.sleep(0.1)
    except KeyboardInterrupt:
        try:
            p.kill()
        except Exception:
            pass
        return 130
    except Exception:
        return 1


def die(msg: str, code: int = 1):
    print(f"ERROR: {msg}")
    sys.exit(code)


def discover_md_in_cwd() -> Path:
    cwd = Path.cwd()
    cands = [
        p for p in cwd.iterdir()
        if p.is_file()
        and p.suffix.lower() == ".md"
        and not p.name.startswith(".")
        and not re.search(r"\.[A-Za-z0-9_-]+\.md$", p.name)
    ]
    if len(cands) == 1:
        return cands[0]
    if not cands:
        die("No .md in current directory.")
    die("Ambiguous .md in CWD:\n" + "\n".join(f" - {p.name}" for p in sorted(cands)))


def find_repo_root(start: Path) -> Path:
    try:
        top = subprocess.check_output(
            ["git", "rev-parse", "--show-toplevel"],
            cwd=start,
            text=True,
            stderr=subprocess.DEVNULL,
        ).strip()
        if top:
            return Path(top)
    except Exception:
        pass
    cur = start
    while True:
        if (cur / "pnpmd.map").exists():
            return cur
        if cur.parent == cur:
            break
        cur = cur.parent
    die("pnpmd.map not found in repo root or ancestors")


def _trim_ascii(s: str, *, left: bool = True, right: bool = True) -> str:
    if left:
        s = re.sub(r"^[ \t]+", "", s)
    if right:
        s = re.sub(r"[ \t]+$", "", s)
    return s


def load_map(map_path: Path) -> List[Tuple[str, str, bool]]:
    if not map_path.exists():
        die(f"Map file not found: {map_path}")
    out: List[Tuple[str, str, bool]] = []
    for raw in map_path.read_text(encoding="utf-8").splitlines():
        if not raw or raw.lstrip().startswith("#") or "=" not in raw:
            continue
        lhs, rhs = raw.split("=", 1)
        lhs = _trim_ascii(lhs)
        rhs = _trim_ascii(rhs)
        if lhs == "":
            continue
        is_regex = lhs.startswith("/") and lhs.endswith("/") and len(lhs) >= 2
        out.append((lhs, rhs, is_regex))
    return out


def title_from_book_yaml(path: Path) -> str:
    """
    Try to extract the main title from a Pandoc-style book YAML.
    Falls back to the filename stem if it can't.
    """
    txt = path.read_text(encoding="utf-8")
    # Prefer "type: main / text: ..."
    m = re.search(r"type:\s*main\s*\n\s*text:\s*(.+)", txt)
    if m:
        return m.group(1).strip().strip('"\'')
    # Fallback: a simple scalar "title: ..."
    m2 = re.search(r"^\s*title\s*:\s*(.+)$", txt, re.MULTILINE)
    if m2:
        return m2.group(1).strip().strip('"\'')
    return path.stem
