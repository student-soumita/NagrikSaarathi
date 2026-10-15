import json
import urllib.request
import urllib.error
import ssl

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

with open('audit_scheme_urls.json', 'r', encoding='utf-8') as f:
    schemes = json.load(f)

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

def check_url(url):
    if not url:
        return "EMPTY", ""
    try:
        req = urllib.request.Request(url, headers=headers, method='HEAD')
        with urllib.request.urlopen(req, timeout=5, context=ctx) as response:
            return response.status, response.url
    except urllib.error.HTTPError as e:
        return e.code, str(e)
    except Exception as e:
        # Retry with GET in case HEAD is rejected (common with gov.in servers)
        try:
            req = urllib.request.Request(url, headers=headers, method='GET')
            with urllib.request.urlopen(req, timeout=5, context=ctx) as response:
                return response.status, response.url
        except Exception as e2:
            return "ERR", str(e2)[:60]

print("Verifying URLs for all 52 schemes...")
results = []
for s in schemes:
    src = s.get('official_source_url')
    app = s.get('official_application_url')
    src_status, src_final = check_url(src) if src else ("NONE", "")
    app_status, app_final = check_url(app) if app else ("NONE", "")
    
    results.append({
        'id': s['id'],
        'slug': s['slug'],
        'state': s['state_code'],
        'src': src,
        'src_status': src_status,
        'app': app,
        'app_status': app_status
    })
    print(f"[{s['id']:2d}] {s['slug'][:24]:24s} | src: {src_status} | app: {app_status}")

with open('url_audit_results.json', 'w', encoding='utf-8') as f:
    json.dump(results, f, indent=2)

print("\nDone! Saved to url_audit_results.json")
