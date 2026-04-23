# TIM-0001 Reference Library

Purpose: store incoming source material now, then generate clean APA-style references for the final project document.

## Folder layout
- `raw/`: pasted notes, copied excerpts, and quick source dumps before cleanup.
- `attachments/`: PDFs, screenshots, exports, or other source artifacts.
- `reference-catalog.yaml`: normalized source metadata (single source of truth).
- `references-apa.md`: finished APA citations derived from the catalog.
- `claims-to-sources.csv`: optional traceability map from document claims to source IDs.

## Workflow
1. Add source text/details to `raw/source-intake.md`.
2. Add or update one record in `reference-catalog.yaml` with a unique `id`.
3. Build and verify the APA entry in `references-apa.md`.
4. Link claims to source IDs in `claims-to-sources.csv` if needed.

## APA notes
- Target style: APA 7th edition.
- Prefer DOI in URL format (`https://doi.org/...`) when available.
- If no date is available, use `(n.d.)`.
- For web pages, include retrieval date only when content is designed to change over time.
