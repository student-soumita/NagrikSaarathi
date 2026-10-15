import json

with open('full_db_urls.json', encoding='utf-8') as f:
    d = json.load(f)

print("=== DOC REQUIREMENTS WITH URL ===")
for doc in d['doc_requirements']:
    print(f"scheme_id={doc['scheme_id']} | {doc['document_code']}: {doc['url']}")

print("\n=== STEPS WITH URL ===")
for st in d['steps']:
    print(f"scheme_id={st['scheme_id']} | {st['step_key']}: {st['url']}")
