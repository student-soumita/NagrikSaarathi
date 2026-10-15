import urllib.request
import json

def test_api():
    print("Testing /api/schemes...")
    req = urllib.request.Request('http://127.0.0.1:8000/api/schemes?page=1&page_size=10')
    with urllib.request.urlopen(req) as resp:
        data = json.loads(resp.read().decode())
        print(f"Total schemes in API: {data['total']}")
        for item in data['items']:
            print(f"[{item['id']:02d}] {item['slug'][:24]:24s} | type: {item['application_portal_type']:18s} | src: {item['official_source_url']} | app: {item['official_application_url']}")

    print("\nTesting /api/dashboard/coverage...")
    req_cov = urllib.request.Request('http://127.0.0.1:8000/api/dashboard/coverage')
    with urllib.request.urlopen(req_cov) as resp:
        cov = json.loads(resp.read().decode())
        print(f"Discovered: {cov['total_schemes_discovered']}")
        print(f"Verified sources: {cov['verified_sources_count']}")
        print(f"Missing sources: {cov['missing_sources_count']}")
        print(f"States: {cov['states_represented']}/28, UTs: {cov['uts_represented']}/8")
        sample_state = cov['state_ut_coverage'][0]
        print(f"Sample State: {sample_state['state_name']} | portal: {sample_state.get('official_portal_url')} | services: {sample_state.get('official_services_url')}")

if __name__ == '__main__':
    test_api()
