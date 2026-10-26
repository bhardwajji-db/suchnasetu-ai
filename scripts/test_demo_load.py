from fastapi.testclient import TestClient
from notice2action.api.server import app

client = TestClient(app)

demos = client.get('/api/demo-library').json()
print(f"Total demos found: {len(demos)}")

txt_demo = next((d for d in demos if d['format'] == 'txt'), None)
pdf_demo = next((d for d in demos if d['format'] == 'pdf'), None)
docx_demo = next((d for d in demos if d['format'] == 'docx'), None)

print("TXT demo:", txt_demo['id'] if txt_demo else None)
print("PDF demo:", pdf_demo['id'] if pdf_demo else None)
print("DOCX demo:", docx_demo['id'] if docx_demo else None)

for d in [txt_demo, pdf_demo, docx_demo]:
    if d:
        did = d['id']
        fmt = d['format']
        resp = client.post(f"/api/demo-library/{did}/load")
        print(f"\n--- Loading {did} ({fmt}) ---")
        print(f"Status: {resp.status_code}")
        if resp.status_code == 200:
            data = resp.json()
            print("Keys returned:", list(data.keys()))
            print("raw_text length:", len(data.get("raw_text", "")))
            print("'text' in data:", "text" in data)
            print("'language' in data:", "language" in data)
            print("source_language:", data.get("source_language"))
            print("First 100 chars of raw_text:", repr(data.get("raw_text", "")[:100]))
        else:
            print("Error detail:", resp.json())
