# SFI-008 — Review Comments

## Design Review: Approved
- ✅ Regex-based HTML anchor parsing is appropriate for the limited HTML in S360 titles
- ✅ `webbrowser.open()` is cross-platform
- ✅ ResourceURIs parsing handles both JSON string and list formats

## Architect Notes
- ✅ No new dependencies — uses stdlib `re`, `webbrowser`, `json`
- ✅ Field grouping into sections improves scannability
- ✅ URL detection doesn't modify underlying data — display-only transformation
