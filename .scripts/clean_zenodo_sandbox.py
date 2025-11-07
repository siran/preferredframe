import os, sys, requests, time

BASE = "https://sandbox.zenodo.org"
LIST_URL = f"{BASE}/api/deposit/depositions"   # <-- YOUR uploads only
TOKEN = os.getenv("ZENODO_SANDBOX_TOKEN")
if not TOKEN:
    print("ERROR: ZENODO_SANDBOX_TOKEN not set"); sys.exit(1)

H = {"Authorization": f"Bearer {TOKEN}"}

def log(title, body=""):
    print(title)
    if body is None: body = ""
    for line in str(body).splitlines():
        print("   ", line)

def get_page(page, size=200):
    params = {"page": page, "size": size}
    log(f"REQUEST: GET {LIST_URL}", f"params={params}")
    r = requests.get(LIST_URL, headers=H, params=params)
    log(f"STATUS: {r.status_code}")
    log("RAW RESPONSE:", r.text)
    r.raise_for_status()
    data = r.json()
    if not isinstance(data, list):
        # older servers may return list; some may wrap—handle both
        data = data.get("hits", {}).get("hits", [])
    return data

def delete_dep(dep_id):
    url = f"{LIST_URL}/{dep_id}"
    log(f"REQUEST: DELETE {url}")
    r = requests.delete(url, headers=H)
    log(f"STATUS: {r.status_code}")
    log("RAW RESPONSE:", r.text)
    return r.status_code

# --- enumerate ALL your depositions (draft + published) with pagination ---
all_deps = []
page = 1
while True:
    try:
        deps = get_page(page)
    except Exception as e:
        log("EXCEPTION (listing):", e); break
    if not deps:
        break
    all_deps.extend(deps)
    page += 1
    time.sleep(0.1)  # be nice

print(f"FOUND: {len(all_deps)} of YOUR depositions")

# --- delete one by one (sandbox permits deletion) ---
failed = 0
for d in all_deps:
    dep_id = d.get("id") or d.get("metadata", {}).get("prereserve_doi", {}).get("recid")
    title = (d.get("metadata") or {}).get("title")
    log("DELETE TARGET:", f"id={dep_id}\ntitle={title}")
    if not dep_id:
        log("SKIP:", "missing deposition id"); continue
    try:
        status = delete_dep(dep_id)
        if status not in (200, 202, 204):
            failed += 1
    except Exception as e:
        failed += 1
        log("EXCEPTION (deleting):", e)

print(f"DONE. Deleted: {len(all_deps)-failed}, Failed: {failed}")
