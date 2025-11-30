# -*- coding: utf-8 -*-
import os
import subprocess
from pathlib import Path
from urllib.parse import urlparse
import yaml

from config import DEFAULT_JOURNAL


ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "site"
SRC = ROOT / ".scripts" / "src"


def _parse_remote(url: str):
    if url.startswith("git@"):
        path = url.split(":", 1)[1]
    else:
        path = urlparse(url).path.lstrip("/")
    if path.endswith(".git"):
        path = path[:-4]
    owner, repo = path.split("/", 1)
    return owner, repo


def detect_repo_branch():
    owner = os.getenv("SITE_OWNER")
    repo = os.getenv("SITE_REPO")
    branch = os.getenv("SITE_BRANCH")

    gh = os.getenv("GITHUB_REPOSITORY")
    if gh and "/" in gh:
        o, r = gh.split("/", 1)
        if not owner:
            owner = o
        if not repo:
            repo = r
    if not branch:
        branch = os.getenv("SITE_BRANCH") or os.getenv("GITHUB_REF_NAME")

    if not (owner and repo):
        url = subprocess.check_output(
            ["git", "config", "--get", "remote.origin.url"],
            text=True,
            stderr=subprocess.DEVNULL,
            cwd=ROOT,
        ).strip()
        o, r = _parse_remote(url)
        if not owner:
            owner = o
        if not repo:
            repo = r

    if not branch:
        branch = subprocess.check_output(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            text=True,
            stderr=subprocess.DEVNULL,
            cwd=ROOT,
        ).strip()

    if not owner:
        owner = "siran"
    if not repo:
        repo = ROOT.name

    return owner, repo, branch


OWNER, REPO, BRANCH = detect_repo_branch()


def compute_base_url() -> str:
    v = os.getenv("BASE_URL")
    if v:
        return v.rstrip("/")

    if os.getenv("GITHUB_ACTIONS", "").lower() == "true":
        return f"https://{OWNER}.github.io/{REPO}"

    return "http://127.0.0.1:8000"


BASE_URL = compute_base_url()


def write_cname_if_custom(base_url: str) -> None:
    root_cname = ROOT / "CNAME"
    if root_cname.exists():
        OUT.mkdir(parents=True, exist_ok=True)
        root_text = root_cname.read_text(encoding="utf-8")
        OUT.joinpath("CNAME").write_text(root_text, encoding="utf-8")
        return

    host = urlparse(base_url).hostname
    if not host:
        return
    if host.endswith(".github.io"):
        return
    if host in {"localhost", "127.0.0.1"}:
        return

    OUT.mkdir(parents=True, exist_ok=True)
    OUT.joinpath("CNAME").write_text(host + "\n", encoding="utf-8")


def _origin_from_cname() -> str | None:
    for base in (ROOT, OUT):
        cname = base / "CNAME"
        if not cname.exists():
            continue
        lines = cname.read_text(encoding="utf-8").splitlines()
        if not lines:
            continue
        first_line = lines[0].strip()
        if not first_line:
            continue
        if first_line.startswith("http://") or first_line.startswith("https://"):
            return first_line.rstrip("/")
        return f"https://{first_line}".rstrip("/")
    return None


def _canonical_origin_from_provenance() -> str | None:
    prints_dir = ROOT / "prints"
    if not prints_dir.exists():
        return None

    for prov in prints_dir.glob("*/*/*/provenance.yaml"):
        data = yaml.safe_load(prov.read_text(encoding="utf-8")) or {}
        u = (data.get("permalink") or "").strip()
        if not u:
            site_block = (data.get("site") or {})
            u = (
                site_block.get("permalink")
                or site_block.get("html_canonical")
                or ""
            ).strip()
        if not u or not u.startswith("http"):
            continue
        p = urlparse(u)
        if p.scheme and p.netloc:
            return f"{p.scheme}://{p.netloc}"
    return None


def current_origin() -> str:
    origin = (
        _origin_from_cname()
        or _canonical_origin_from_provenance()
        or BASE_URL
    )
    return origin.rstrip("/")
