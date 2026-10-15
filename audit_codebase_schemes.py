import json
from backend.app.services.scheme_ingestion_service import NATIONWIDE_REGISTRY_SCHEMES
from backend.app.seed_pan_india_schemes import SCHEMES_CATALOGUE
from backend.app.seed import DEMO_FIELDS

print(f"NATIONWIDE_REGISTRY_SCHEMES count: {len(NATIONWIDE_REGISTRY_SCHEMES)}")
print(f"SCHEMES_CATALOGUE count: {len(SCHEMES_CATALOGUE)}")

registry_slugs = {s["slug"]: s for s in NATIONWIDE_REGISTRY_SCHEMES}
seed_slugs = {s["slug"]: s for s in SCHEMES_CATALOGUE}

all_slugs = set(registry_slugs.keys()).union(set(seed_slugs.keys()))
print(f"Total unique slugs across codebase: {len(all_slugs)}")

suspicious_urls = []
for slug in sorted(all_slugs):
    reg = registry_slugs.get(slug, {})
    sd = seed_slugs.get(slug, {})
    
    src = reg.get("official_source_url") or sd.get("official_source_url") or ""
    app = reg.get("official_application_url") or sd.get("official_application_url") or ""
    
    # check if gov.in or nic.in
    is_src_gov = any(src.endswith(d) or f"{d}/" in src for d in [".gov.in", ".nic.in", ".in"])
    is_app_gov = any(app.endswith(d) or f"{d}/" in app for d in [".gov.in", ".nic.in", ".in"]) if app else True
    
    print(f"{slug[:32]:32s} | src: {src[:40]:40s} | app: {app[:40]}")
    if not is_src_gov or not is_app_gov or "example" in src or "cattle" in src or "solar" in src:
        suspicious_urls.append((slug, src, app))

print(f"\nSuspicious/Non-standard URLs found: {len(suspicious_urls)}")
for item in suspicious_urls:
    print(f" - {item[0]}: src='{item[1]}' app='{item[2]}'")
