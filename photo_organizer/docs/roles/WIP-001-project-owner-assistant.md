# Project Owner Assistant Notes: WIP-001

## Work Item
WIP-001 - Organize Photos by Date/Time

## Decisions Made

1. **Decomposed original request into two stories**
   - Original request combined organization AND viewing
   - Split into WIP-001 (organize) and WIP-002 (view) for independent delivery

2. **Chose copy over move operation**
   - Preserves original folder structure as backup
   - Safer for users; no data loss risk

3. **Chose YYYY/MM folder structure**
   - Common convention for date-based organization
   - Balances granularity (not too deep) with organization (not too flat)

4. **Chose EXIF with file-date fallback**
   - EXIF is most accurate for "date taken"
   - File modification date is reasonable fallback for photos without EXIF

## Alternatives Considered

| Decision | Alternative | Why Rejected |
|----------|-------------|--------------|
| Copy vs Move | Move files | Risk of data loss; users may want to keep originals |
| YYYY/MM structure | YYYY/MM/DD | Too granular; many empty folders |
| YYYY/MM structure | YYYY only | Not granular enough for large collections |
| EXIF primary | File date only | EXIF is more accurate for actual photo date |

## Tradeoffs Accepted
- Copying uses more disk space than moving
- No handling for videos (can be added in future story)
- No duplicate detection (can be added in future story)

## Known Limitations
- Photos without EXIF and with incorrect file dates will be mis-organized
- Very large collections (100k+ photos) may need progress indication (future enhancement)

## Risks
- LOW: PIL/Pillow dependency for EXIF reading (widely available, well-maintained)
