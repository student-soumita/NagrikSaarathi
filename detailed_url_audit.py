import json

with open('audit_scheme_urls.json', 'r', encoding='utf-8') as f:
    schemes = json.load(f)

print(f"Total schemes audited: {len(schemes)}")
issues = []
for s in schemes:
    id_ = s['id']
    slug = s['slug']
    state = s['state_code'] or 'CENTRAL'
    src = s.get('official_source_url') or ''
    app = s.get('official_application_url') or ''
    
    reasons = []
    if not src:
        reasons.append("Missing official_source_url")
    elif not (src.startswith("http://") or src.startswith("https://")):
        reasons.append(f"Invalid URL protocol: {src}")
    elif "example.gov.in" in src or "placeholder" in src:
        reasons.append(f"Placeholder domain: {src}")
        
    if not app:
        reasons.append("Missing official_application_url")
    elif not (app.startswith("http://") or app.startswith("https://")):
        reasons.append(f"Invalid app URL protocol: {app}")
    elif "example.gov.in" in app or "placeholder" in app:
        reasons.append(f"Placeholder app domain: {app}")

    # Check for known dead/outdated or non-specific patterns
    if "cattle-shed" in src or "cattle-shed" in app:
        reasons.append("Fictional / placeholder candidate URL (cattle-shed)")
    if src == "https://goa.gov.in/solar":
        reasons.append("Inaccurate Goa solar rooftop portal (should be https://geda.goa.gov.in or https://pmsuryaghar.gov.in)")
    if "https://chirayuayushmanharyana.in" in src:
        # Check if chirayuayushmanharyana.in is official vs haryana health portal
        pass
    if "focusmeghalaya.org" in src:
        reasons.append("Non-gov.in domain (focusmeghalaya.org) - check official portal")

    print(f"[{id_:02d}] ({state}) {slug}")
    print(f"     Source URL: {src}")
    print(f"     App URL:    {app}")
    if reasons:
        print(f"     [WARNING] ISSUES: {', '.join(reasons)}")
        issues.append((id_, slug, state, reasons))
    print()

print(f"Total schemes with potential URL issues: {len(issues)}")
