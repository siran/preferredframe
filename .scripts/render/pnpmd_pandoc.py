# pnpmd_pandoc.py

from pathlib import Path
from typing import List

from pnpmd_util import run_visible


def render_pdf(
    in_tmp: Path,
    out_tmp: Path,
    meta_args: List[str],
    shift_args: List[str],
    common_args: List[str],
    timeout: int,
) -> int:
    cmd = [
        "docker",
        "run",
        "--rm",
        "--mount",
        f"type=bind,source={str(in_tmp.parent)},target=/data",
        "-w",
        "/data",
        "pandoc/extra",
        "--standalone",
        *common_args,
        *shift_args,
        *meta_args,
        "--filter",
        "pandoc-crossref",
        "in.md",
        "-o",
        out_tmp.name,
    ]
    return run_visible(cmd, timeout=timeout)


def render_html(
    in_tmp: Path,
    out_tmp: Path,
    meta_args: List[str],
    shift_args: List[str],
    common_args: List[str],
    timeout: int,
) -> int:
    cmd = [
        "docker",
        "run",
        "--rm",
        "--mount",
        f"type=bind,source={str(in_tmp.parent)},target=/data",
        "-w",
        "/data",
        "pandoc/extra",
        "--standalone",
        *common_args,
        *shift_args,
        *meta_args,
        "--filter",
        "pandoc-crossref",
        "in.md",
        "-t",
        "html5",
        "-o",
        out_tmp.name,
    ]
    return run_visible(cmd, timeout=timeout)


def render_epub(
    in_tmp: Path,
    out_tmp: Path,
    meta_args: List[str],
    shift_args: List[str],
    common_args: List[str],
    timeout: int,
) -> int:
    cmd = [
        "docker",
        "run",
        "--rm",
        "--mount",
        f"type=bind,source={str(in_tmp.parent)},target=/data",
        "-w",
        "/data",
        "pandoc/extra",
        "--standalone",
        *common_args,
        *shift_args,
        *meta_args,
        "--filter",
        "pandoc-crossref",
        "in.md",
        "-t",
        "epub3",
        "-o",
        out_tmp.name,
    ]
    return run_visible(cmd, timeout=timeout)
