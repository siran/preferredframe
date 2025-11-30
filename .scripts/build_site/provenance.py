# -*- coding: utf-8 -*-
from pathlib import Path
import re
import yaml

import env
from config import EXCLUDE_NAMES
from gitutil import is_gitignored


def iter_provenance_files():
    for top in env.ROOT.iterdir():
        if not top.is_dir():
            continue
        if top == env.OUT:
            continue
        if top.name in EXCLUDE_NAMES:
            continue
        if top.name.startswith(".") and top.name != ".well-known":
            continue
        for prov in top.glob("**/provenance.yaml"):
            if is_gitignored(prov):
                continue
            yield prov


def hidden_stems_from_provenance(preferred_journal: str) -> set[tuple[str, str]]:
    stems_with_pref: set[tuple[str, str]] = set()
    stems_with_nonpref: set[tuple[str, str]] = set()

    for prov in iter_provenance_files():
        data = yaml.safe_load(prov.read_text(encoding="utf-8")) or {}

        j = (data.get("journal") or "").strip()
        rel_parts = prov.relative_to(env.ROOT).parts
        if len(rel_parts) < 2:
            continue
        top, stem = rel_parts[0], rel_parts[1]
        key = (top, stem)

        if not j:
            continue
        if j == preferred_journal:
            stems_with_pref.add(key)
        else:
            stems_with_nonpref.add(key)

    return {k for k in stems_with_nonpref if k not in stems_with_pref}


def _orcid_url(v: str) -> str:
    v = (v or "").strip()
    if not v:
        return ""
    if v.startswith("http"):
        return v
    m = re.search(r"(\d{4}-\d{4}-\d{4}-\d{3}[0-9Xx])", v)
    return f"https://orcid.org/{m.group(1).upper()}" if m else ""


def normalize_authors(auth_list):
    out = []
    for a in (auth_list or []):
        if isinstance(a, dict):
            nm = (a.get("name") or a.get("full_name") or "").strip()
            oc = _orcid_url(a.get("orcid") or a.get("id") or a.get("orcid_id") or "")
            em = (a.get("email") or "").strip()
        else:
            nm = str(a).strip()
            oc = ""
            em = ""
        if not nm or nm.lower() == "name":
            continue
        item = {"name": nm}
        if oc:
            item["orcid"] = oc
        if em:
            item["email"] = em
        out.append(item)
    return out


def fmt_author(a):
    nm = a.get("name", "").strip()
    oc = _orcid_url(a.get("orcid", "").strip())
    if not nm:
        return ""
    if oc:
        return f'{nm} (<a href="{oc}">ORCID</a>)'
    return nm
