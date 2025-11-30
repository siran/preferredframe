# -*- coding: utf-8 -*-
from datetime import datetime, date
import re


def _to_datetime(obj) -> datetime | None:
    if isinstance(obj, datetime):
        return obj
    if isinstance(obj, date):
        return datetime.combine(obj, datetime.min.time())
    if isinstance(obj, str):
        s = obj.strip()
        for fmt in ("%Y-%m-%d", "%Y-%m", "%Y"):
            try:
                return datetime.strptime(s, fmt)
            except Exception:
                pass
    return None


def month_year(d) -> str:
    dt = _to_datetime(d)
    if not dt:
        return str(d) if d is not None else ""
    return dt.strftime("%B %Y")


def scholar_date(x) -> str:
    if isinstance(x, datetime):
        return x.strftime("%Y/%m/%d")
    if isinstance(x, date):
        return x.strftime("%Y/%m/%d")
    if isinstance(x, str):
        s = x.strip()
        if not s:
            return ""
        if re.fullmatch(r"\d{4}-\d{2}-\d{2}", s):
            y, m, d = s.split("-")
            return f"{y}/{m}/{d}"
        if re.fullmatch(r"\d{4}-\d{2}", s):
            y, m = s.split("-")
            return f"{y}/{m}"
        if re.fullmatch(r"\d{4}", s):
            return s
        return s.replace("-", "/")
    return ""


def iso_date_str(x) -> str:
    if isinstance(x, datetime):
        return x.date().isoformat()
    if isinstance(x, date):
        return x.isoformat()
    if isinstance(x, str):
        return x.strip()
    return str(x) if x else ""
