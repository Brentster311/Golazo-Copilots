# SFI-008 — Design Document

## Summary
Display all available S360 action item fields in the detail modal with clickable hyperlinks for URLs.

## Problem Statement
The detail view showed a subset of fields. Users needed full parity with the S360 web portal, including clickable URLs and ResourceURIs.

## Proposed Approach
- Parse HTML anchor tags via regex (`HTML_ANCHOR_PATTERN`) to extract URLs from titles
- Detect plain URLs in any text field and render as clickable links (blue, underlined)
- Parse `ResourceURIs` field (JSON string or list) into individual clickable links
- Use `webbrowser.open()` to open links in system default browser
- Group fields into sections: status, dates, ownership, service/program, resources

## Test Strategy
- Unit tests for URL extraction, anchor parsing, ResourceURIs parsing
- Tests for detail modal color indicators
