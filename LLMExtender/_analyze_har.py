"""Analyze key HAR entries for OneNote page fetch."""

import json

with open(r"C:\Users\Brent\Downloads\microsoft.sharepoint.com.har", "r", encoding="utf-8") as f:
    har = json.load(f)

# Entry 26: POST to OneNote.ashx (220KB response)
e = har["log"]["entries"][26]
req = e["request"]
resp = e["response"]

print("=== REQUEST ===")
print(f"URL: {req['url']}")
print(f"Method: {req['method']}")

print("\n--- Request Headers ---")
for h in req["headers"]:
    name = h["name"]
    val = h["value"]
    # Truncate sensitive headers
    if name.lower() in ("cookie",):
        continue
    if name.lower() in ("authorization",) and len(val) > 80:
        val = val[:80] + "..."
    print(f"  {name}: {val}")

# Request body
if req.get("postData"):
    pd = req["postData"]
    mime = pd.get("mimeType", "?")
    text = pd.get("text", "")
    print(f"\n--- Request Body (mimeType: {mime}) ---")
    print(text[:1000])

print("\n=== RESPONSE ===")
print(f"Status: {resp['status']}")
for h in resp["headers"]:
    if h["name"].lower() == "content-type":
        print(f"Content-Type: {h['value']}")

content = resp["content"]
print(f"Size: {content.get('size', 0)}")
text = content.get("text", "")
print(f"Text length: {len(text)}")
print(f"\nPreview:\n{text[:1000]}")

# Also check entry 10 (POST to onenoteframe.aspx)
print("\n\n========================================")
print("=== Entry 10: onenoteframe.aspx POST ===")
e10 = har["log"]["entries"][10]
req10 = e10["request"]
resp10 = e10["response"]
print(f"URL: {req10['url'][:120]}")
print(f"Method: {req10['method']}")
print(f"Status: {resp10['status']}")
print(f"Size: {resp10['content'].get('size', 0)}")

print("\n--- Request Headers (non-cookie) ---")
for h in req10["headers"]:
    if h["name"].lower() in ("cookie",):
        continue
    val = h["value"]
    if len(val) > 100:
        val = val[:100] + "..."
    print(f"  {h['name']}: {val}")

if req10.get("postData"):
    pd = req10["postData"]
    print(f"\n--- Body ({pd.get('mimeType', '?')}) ---")
    print(pd.get("text", "")[:500])
