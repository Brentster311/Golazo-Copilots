# GCP-0036 — Test Cases

## TC-1: Bootstrap no longer modifies version comment
- Run bootstrap, verify output file's version comment matches source exactly

## TC-2: _get_deployed_version reads new format
- File with `<!-- Last Updated in Golazo Copilot Version: 1.2.3 -->` returns "1.2.3"

## TC-3: Old format returns None
- File with `<!-- Golazo Copilot Version: 1.2.3 -->` returns None (no longer matched)

## TC-4: All source files use new format
- Grep for old format patterns returns zero matches
