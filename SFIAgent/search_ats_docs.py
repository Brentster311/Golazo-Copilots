#!/usr/bin/env python
"""Search for Azure Tenant Security docs."""

import requests
from azure.identity import AzureCliCredential

cred = AzureCliCredential()
token = cred.get_token('499b84ac-1321-427f-aa17-267ca6975798/.default')
headers = {'Authorization': f'Bearer {token.token}', 'Content-Type': 'application/json'}

search_url = 'https://almsearch.dev.azure.com/msazure/_apis/search/codesearchresults?api-version=7.0'
payload = {'searchText': 'Azure Resources Core Security Baseline plaintext secrets remediation', '$top': 30}

resp = requests.post(search_url, headers=headers, json=payload)
if resp.status_code == 200:
    data = resp.json()
    results = data.get('results', [])
    print(f'Found {len(results)} results')
    for r in results[:20]:
        print(f"{r.get('fileName')} - {r.get('repository', {}).get('name')}")
        print(f"  Path: {r.get('path')}")
else:
    print(f"Error: {resp.status_code}")
    print(resp.text)
