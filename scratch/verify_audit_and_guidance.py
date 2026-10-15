import urllib.request
import json
import sys

# Ensure UTF-8 output
sys.stdout.reconfigure(encoding='utf-8')

# 1. Audit
audit_res = json.loads(urllib.request.urlopen('http://127.0.0.1:8000/api/schemes/coverage-audit').read().decode('utf-8'))
print('Total Schemes in DB:', audit_res['total_schemes'])
print('Coverage Percentage:', audit_res['coverage_percentage'], '%')
print('Fully Supported:', audit_res['fully_supported_schemes'])
print('Unsupported Schemes:', audit_res['unsupported_schemes'])
assert audit_res['coverage_percentage'] == 100.0, 'Coverage should be 100%'

# 2. Check 5 schemes at random for guidance packets
schemes = json.loads(urllib.request.urlopen('http://127.0.0.1:8000/api/schemes/').read().decode('utf-8'))
sample_ids = [schemes[0]['id'], schemes[10]['id'], schemes[25]['id'], schemes[40]['id'], schemes[-1]['id']]
for s_id in sample_ids:
    req_url = f'http://127.0.0.1:8000/api/schemes/{s_id}/guidance?language=hi'
    g = json.loads(urllib.request.urlopen(req_url).read().decode('utf-8'))
    name = g['scheme']['display_name']
    field_cnt = len(g['fields'])
    elig_cnt = len(g['eligibility_requirements'])
    doc_cnt = len(g['document_requirements'])
    print(f'Scheme {s_id} ({name}): {field_cnt} fields, {elig_cnt} eligibility criteria, {doc_cnt} docs')
    assert field_cnt > 0, f'Scheme {s_id} should have form fields'

print('SUCCESS: All API checks passed perfectly!')
