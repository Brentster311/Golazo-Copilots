# SFI-024 — Test Cases

## Story A: Selected-Item ETA in Drill-Down

### TC-A01: Selected ETA button shows count
- **Given**: DetailModal with 13 items, user selects 3
- **When**: Selection changes
- **Then**: Button text contains "3 selected"

### TC-A02: Selected ETA button disabled with no selection
- **Given**: DetailModal with items, no rows selected
- **Then**: Selected-items ETA button is disabled

### TC-A03: Clicking opens ManualEtaReviewDialog with selected items only
- **Given**: 3 of 13 items selected
- **When**: User clicks selected ETA button
- **Then**: ManualEtaReviewDialog receives list of exactly 3 items

### TC-A04: Detail tree refreshes after selected-item ETA save
- **Given**: User edits ETAs for selected items
- **When**: Save completes
- **Then**: Tree rows update + home screen callback fires

## Story B: View Details from Manual Review

### TC-B01: View Details button exists in ManualEtaReviewDialog
- **Given**: ManualEtaReviewDialog showing an item
- **Then**: A button with text containing "View Details" exists

### TC-B02: View Details button opens ItemDetailsModal  
- **Given**: ManualEtaReviewDialog showing an item
- **When**: User clicks "View Details"
- **Then**: ItemDetailsModal is opened for the current item
