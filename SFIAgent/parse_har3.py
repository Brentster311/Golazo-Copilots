#!/usr/bin/env python
"""Parse HAR file for S360 API endpoints."""
import json

har = json.load(open(r'C:\Users\Brent\Downloads\vnext.s360.msftcloudes.com3.har', encoding='utf-8'))
entries = har.get('log', {}).get('entries', [])

print("=" * 80)
print("NEW API ENDPOINTS WITH PAYLOADS")
print("=" * 80)

seen = set()
for e in entries:
    req = e.get('request', {})
    url = req.get('url', '')
    method = req.get('method', '')
    
    if 'api.vnext.s360' not in url:
        continue
    
    path = url.split('?')[0].replace('https://api.vnext.s360.msftcloudes.com', '')
    
    if path in seen:
        continue
    seen.add(path)
    
    print(f"\n{method} {path}")
    
    if method == 'POST':
        post_data = req.get('postData', {})
        text = post_data.get('text', '')
        if text:
            try:
                payload = json.loads(text)
                print(f"Payload: {json.dumps(payload, indent=2)[:500]}")
            except:
                print(f"Raw: {text[:300]}")
