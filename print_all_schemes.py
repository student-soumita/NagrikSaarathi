import json

with open('full_db_urls.json', encoding='utf-8') as f:
    d = json.load(f)

print(f"{'ID':2s} | {'Slug':30s} | {'State':5s} | {'Candidate':9s} | {'Demo':5s} | {'Source URL':40s} | {'App URL'}")
print("-" * 120)
for s in d['schemes']:
    print(f"{s['id']:2d} | {s['slug'][:30]:30s} | {str(s['state_code']):5s} | {str(s['is_candidate']):9s} | {str(s['is_demo']):5s} | {str(s['official_source_url'])[:40]:40s} | {s['official_application_url']}")
