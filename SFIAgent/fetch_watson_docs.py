#!/usr/bin/env python
"""Fetch Azure Watson documentation from Azure DevOps."""

import requests
from azure.identity import AzureCliCredential

cred = AzureCliCredential()
token = cred.get_token('499b84ac-1321-427f-aa17-267ca6975798/.default')
headers = {
    'Authorization': f'Bearer {token.token}',
    'Content-Type': 'application/json'
}

# Fetch the Watson containerized workloads documentation directly
# Repo: ATW-Documentation, Path: /ATW Docs/AzureWatson/WatsonOnContainerizedWorkloads.md
file_url = 'https://dev.azure.com/msazure/One/_apis/git/repositories/ATW-Documentation/items?path=/ATW%20Docs/AzureWatson/WatsonOnContainerizedWorkloads.md&api-version=7.0'

resp = requests.get(file_url, headers=headers)
print(f'Status: {resp.status_code}')

if resp.status_code == 200:
    print(resp.text)
else:
    print(resp.text[:1000])
