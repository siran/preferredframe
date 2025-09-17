#!/usr/bin/env python3
import os, html, datetime, urllib.parse, subprocess
from pathlib import Path
from dataclasses import dataclass

# --- autodetect OWNER, REPO, BRANCH (no manual config) ---
def _parse_remote(url: str):
    try:
        if url.startswith("git@"):
            path = url.split(":", 1)[1]
        else:
            path = urllib.parse.urlparse(url).path.lstrip("/")
        if path.endswith(".git"):
            path = path[:-4]
        owner, repo = path.split("/", 1)
        return owner, repo
    except Exception:
        return None, None

def detect_repo_branch():
    owner = os.getenv("SITE_OWNER")
    repo = os.getenv("SITE_REPO")
    branch = os.getenv("SITE_BRANCH")

    gh = os.getenv("GITHUB_REPOSITORY")  # e.g. "siran/research"
    if gh and "/" in gh:
        o, r = gh.split("/", 1)
        owner = owner or o
        repo = repo or r
    branch = branch or os.getenv("GITHUB_REF_NAME")

    if not (owner and repo):
        try:
            url = subprocess.check_output(
                ["git", "config", "--get", "remote.origin.url"],
                text=True, stderr=subprocess.DEVNULL
            ).strip()
            o, r = _parse_remote(url)
            owner = owner or o
            repo = repo or r
        except Exception:
            pass
    if not branch:
        try:
            branch = subprocess.check_output(
                ["git", "rev-parse", "--abbrev-ref", "HEAD"],
                text=True, stderr=subprocess.DEVNULL
            ).strip()
        except Exception:
            branch = "main"

    if not owner:
        owner = "siran"
    if not repo:
        repo = Path.cwd().name
    return owner, repo, branch

OWNER, REPO, BRANCH = detect_repo_branch()

# --- config ---
ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "site"
EXCLUDE_TOP = {"site", "venv", ".venv", "env", ".env", "node_modules", ".git",
               "__pycache__", ".mypy_cache", ".pytest_cache", ".ruff_cache", ".cache"}

def rel(p: Path) -> Path:
    return p.relative_to(ROOT)

def raw_url(path_from_root: Path) -> str:
    return f"https://raw.githubusercontent.com/{OWNER}/{REPO}/{BRANCH}/{urllib.parse.quote(path_from_root.as_posix())}"

def blob_url(path_from_root: Path) -> str:
    return f"https://github.com/{OWNER}/{REPO}/blob/{BRANCH}/{urllib.parse.quote(path_from_root.as_posix())}"

@dataclass
class Item:
    name: str
    is_dir: bool
    mtime: float
    path: Path

INDEX_STYLE = """<style>
html,body{background:#fff;color:#111;margin:0;font:16px/1.55 system-ui,Segoe UI,Roboto,Helvetica,Arial,sans-serif}
main{max-width:960px;margin:2rem auto;padding:0 1rem}
h1{margin:.2rem 0 0;font-weight:650}
.sub{color:#666;font-size:.95rem;margin:.25rem 0 1rem}
.list{list-style:none;margin:0;padding:0}
.row{display:flex;align-items:center;gap:.75rem;padding:.55rem .6rem;border:1px solid #e5e7eb;border-radius:.55rem;margin:.4rem 0}
.row:hover{background:#f8fafc}
.icon{width:1.25rem;text-align:center}
.name{flex:1;min-width:240px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.meta{display:flex;gap:1rem;color:#666;font-size:.92rem}
.badges{display:flex;gap:.35rem;flex-wrap:wrap}
.badge{font-size:.86rem;border:1px solid #e5e7eb;background:#fff;color:inherit;border-radius:.5rem;padding:.15rem .4rem;text-decoration:none}
.crumbs a{color:inherit;text-decoration:none}
footer{margin:3rem 0 2rem;color:#666;font-size:.9rem}
</style>"""

def fmt_local(ts: float) -> str:
    return datetime.datetime.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M")

def write_index(dir_abs: Path, items: list[Item]):
    rel_dir = rel(dir_abs) if dir_abs != ROOT else Path()
    out_dir = OUT / rel_dir
    out_dir.mkdir(parents=True, exist_ok=True)

    # Breadcrumbs
    depth = len(rel_dir.parts)
    to_root = "./" if depth == 0 else "../" * depth
    crumbs = [f'<span class="crumbs"><a href="{to_root}">Home</a>']
    parts = list(rel_dir.parts)
    for i, p in enumerate(parts):
        up = "../" * (len(parts) - i - 1) or "./"
        crumbs.append(f' / <a href="{up}">{html.escape(p)}</a>')
    crumbs.append("</span>")

    title = (rel_dir.name or f"{REPO} index")
    subtitle = f'{ "".join(crumbs) }'

    items_sorted = sorted(items, key=lambda e: (not e.is_dir, e.name.lower()))
    rows = []
    for it in items_sorted:
        icon = "📁" if it.is_dir else "📄"
        if it.is_dir:
            href = (rel(it.path).name + "/") if rel_dir.parts else (rel(it.path).as_posix() + "/")
            link = f'<a href="{href}">{html.escape(it.name)}</a>'
            meta = f'<span>dir</span>'
        else:
            p_rel = rel(it.path)
            link = (f'{html.escape(it.name)} '
                    f'<span class="badges">'
                    f'<a class="badge" href="{blob_url(p_rel)}">github</a> '
                    f'<a class="badge" href="{raw_url(p_rel)}">raw</a>'
                    f'</span>')
            meta = f'<span>file</span><span>modified {html.escape(fmt_local(it.mtime))}</span>'
        rows.append(
            f'<li class="row">'
            f'<span class="icon">{icon}</span>'
            f'<div class="name">{link}</div>'
            f'<div class="meta">{meta}</div>'
            f'</li>'
        )

    html_doc = f"""<!doctype html>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{html.escape(title)}</title>
<link rel="icon" href="data:,">
{INDEX_STYLE}
<main>
  <h1>{html.escape(title)}</h1>
  <div class="sub">{subtitle}</div>
  <ul class="list">
{''.join(rows)}
  </ul>
  <footer>© {datetime.datetime.now().year} {OWNER} • Built from {OWNER}/{REPO}@{BRANCH}</footer>
</main>
"""
    (out_dir / "index.html").write_text(html_doc, encoding="utf-8")

def prune_dirs(root: str, dirnames: list[str]):
    keep = []
    for d in dirnames:
        if d in EXCLUDE_TOP: continue
        if d.startswith(".") and d != ".well-known": continue
        if (Path(root) / d / "pyvenv.cfg").exists(): continue
        keep.append(d)
    dirnames[:] = keep

def main():
    OUT.mkdir(exist_ok=True)
    (OUT / ".nojekyll").write_text("", encoding="utf-8")

    for dirpath, dirnames, filenames in os.walk(ROOT):
        if Path(dirpath) == OUT:
            dirnames.clear()
            continue
        if dirpath != str(ROOT):
            first = Path(dirpath).relative_to(ROOT).parts[0]
            if first in EXCLUDE_TOP:
                dirnames.clear()
                continue
            if (Path(dirpath) / "pyvenv.cfg").exists():
                dirnames.clear()
                continue
        prune_dirs(dirpath, dirnames)

        d = Path(dirpath)
        items: list[Item] = []

        for p in sorted([x for x in d.iterdir() if x.is_dir()], key=lambda x: x.name.lower()):
            if p.name in EXCLUDE_TOP: continue
            if p.name.startswith(".") and p.name != ".well-known": continue
            if (p / "pyvenv.cfg").exists(): continue
            mtime = p.stat().st_mtime
            items.append(Item(name=p.name, is_dir=True, mtime=mtime, path=p))

        for p in sorted([x for x in d.iterdir() if x.is_file() and not x.name.startswith(".")], key=lambda x: x.name.lower()):
            mtime = p.stat().st_mtime
            items.append(Item(name=p.name, is_dir=False, mtime=mtime, path=p))

        write_index(d, items)

if __name__ == "__main__":
    main()
