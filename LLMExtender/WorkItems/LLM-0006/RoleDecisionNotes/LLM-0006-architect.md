# LLM-0006 — Architect Notes
- Architecture approved. `url_fetcher.py` is a standalone utility — clean separation.
- Client methods delegate to fetcher, no provider coupling.
- Auth token flows through Bearer header — standard pattern.
- httpx handles redirects by default (follow_redirects=True recommended).
- No architectural concerns. Proceed.
