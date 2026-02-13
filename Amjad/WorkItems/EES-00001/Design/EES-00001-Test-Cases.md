# EES-00001 — Test Cases

## Test Case Mapping to Acceptance Criteria

| AC | Test Cases |
|----|------------|
| AC-1: Fact extraction from incident | TC-01, TC-02, TC-03, TC-04 |
| AC-2: User confirm/edit/reject/specialize | TC-05, TC-06, TC-07, TC-08, TC-09, TC-10 |
| AC-3: Incident YAML persistence | TC-11, TC-12 |
| AC-4: Ontology management | TC-13, TC-14, TC-15 |
| AC-5: Rule generation and persistence | TC-16, TC-17, TC-18, TC-19 |
| AC-6: RootCause entity management | TC-20, TC-21, TC-22 |
| AC-7: YAML validity | TC-23 |

---

## Incident Loading & Fact Extraction

### TC-01: Happy path — load incident and extract facts
**Given** a valid free-text incident file at a known path
**When** the system processes the incident
**Then** the LLM is called with the incident text and current ontology, and a list of `Noun(instance).Property operator value` facts is proposed to the user
**Expected:** Facts are displayed in numbered list with `(c/e/r/s)` prompt

### TC-02: Incident file not found
**Given** a path to a non-existent file
**When** the system attempts to load the incident
**Then** the system prints an error message to stderr and exits without modifying any YAML files
**Expected failure message:** "Error: Incident file not found: <path>"

### TC-03: Empty incident file
**Given** an incident file that exists but is empty (0 bytes)
**When** the system attempts to process it
**Then** the system prints an error and exits without calling the LLM or modifying YAML files
**Expected failure message:** "Error: Incident file is empty: <path>"

### TC-04: LLM returns no facts
**Given** a valid incident file
**When** the LLM returns an empty fact list (no extractable facts)
**Then** the system informs the user that no facts were extracted and exits without modifying YAML files
**Expected message:** "No facts extracted from incident. No changes made."

---

## User Confirmation Flow

### TC-05: Confirm a fact
**Given** a proposed fact `Server(*).CPUUsage > 90`
**When** the user enters `c`
**Then** the fact is marked as confirmed with status "confirmed" and included in persistence

### TC-06: Edit a fact
**Given** a proposed fact `App(*).ResponseTime > 10s`
**When** the user enters `e`
**Then** the system prompts for the edited fact text
**When** the user enters `App(*).ResponseTime > 8s`
**Then** the edited fact replaces the original and is marked confirmed

### TC-07: Reject a fact
**Given** a proposed fact `Network(*).Latency > 100ms`
**When** the user enters `r`
**Then** the fact is excluded from rule generation and marked as "rejected" in the incident YAML

### TC-08: Specialize a fact
**Given** a proposed fact `Server(*).CPUUsage > 90`
**When** the user enters `s`
**Then** the system prompts for the instance name
**When** the user enters `WebApp01`
**Then** the fact becomes `Server(WebApp01).CPUUsage > 90` and the user is prompted to confirm or reject it

### TC-09: Edit with invalid format
**Given** a proposed fact
**When** the user enters `e` and provides malformed text (e.g., "blah blah")
**Then** the system rejects the input with a validation error and re-prompts
**Expected failure message:** "Invalid fact format. Expected: Noun(instance).Property operator value"

### TC-10: All facts rejected
**Given** 3 proposed facts
**When** the user rejects all 3
**Then** no rules are generated, no ontology entries added, incident YAML is saved with all facts marked "rejected"
**Expected message:** "All facts rejected. No rules generated."

---

## Incident YAML Persistence

### TC-11: Incident YAML contains source text and confirmed facts
**Given** a confirmed set of facts from an incident
**When** persistence completes
**Then** `incidents/<incident-id>.yaml` exists, is valid YAML, contains the original source text, all confirmed facts with noun/instance/property/operator/value/status, and a timestamp

### TC-12: Rejected facts are recorded
**Given** a mix of confirmed and rejected facts
**When** persistence completes
**Then** the incident YAML contains both confirmed and rejected facts, each with correct status

---

## Ontology Management

### TC-13: New Noun.Property added to ontology
**Given** an empty `ontology.yaml`
**When** a fact `Server(*).CPUUsage > 90` is confirmed
**Then** `ontology.yaml` contains a "Server" noun with a "CPUUsage" property

### TC-14: Existing Noun.Property reused (case-insensitive)
**Given** `ontology.yaml` contains `Server.CPUUsage`
**When** a fact `server(*).cpuusage > 95` is confirmed
**Then** no new entry is added; the existing `Server.CPUUsage` is matched
**And** `ontology.yaml` has exactly one entry for this noun/property pair

### TC-15: Multiple new properties on same noun
**Given** `ontology.yaml` contains `Server.CPUUsage`
**When** facts `Server(*).MemoryFree < 5%` and `Server(*).DiskIO > 80%` are confirmed
**Then** `ontology.yaml` has `Server` with three properties: CPUUsage, MemoryFree, DiskIO

---

## Rule Generation & Persistence

### TC-16: Happy path — rules generated from confirmed facts
**Given** confirmed facts from an incident with an identified root cause
**When** the system generates rules
**Then** at least one rule is persisted to `rules/` as valid YAML with:
  - `rule_id` assigned
  - `status: "CONFIRMED"`
  - `type: "positive"`
  - `sources` containing the incident ID
  - `conditions` with `logic` (AND or OR) and `items`
  - `then` with noun/instance/property/value
  - `because` clause (non-empty string)

### TC-17: Rules use flat AND only (no mixed logic)
**Given** generated rules
**When** inspecting each rule
**Then** every rule's `conditions.logic` is either "AND" or "OR", never mixed

### TC-18: Rules include instance parameter
**Given** a confirmed fact `Server(WebApp01).CPUUsage > 90`
**When** a rule is generated containing this fact
**Then** the rule condition item includes `instance: "WebApp01"`

### TC-19: Single confirmed fact generates a rule
**Given** only one confirmed fact with an identified root cause
**When** the system generates rules
**Then** a valid rule is generated with a single condition item

---

## RootCause Entity Management

### TC-20: New root cause added
**Given** `rootcauses.yaml` is empty or doesn't contain "Resource Exhaustion"
**When** the incident identifies root cause "Resource Exhaustion"
**Then** `rootcauses.yaml` contains an entry with `name: "Resource Exhaustion"` and `action_plan: null`

### TC-21: Existing root cause not duplicated
**Given** `rootcauses.yaml` already contains "Resource Exhaustion"
**When** another incident identifies the same root cause
**Then** `rootcauses.yaml` still has exactly one entry for "Resource Exhaustion"

### TC-22: No root cause identified
**Given** an incident where the user rejects or no root cause is proposed
**When** processing completes
**Then** `rootcauses.yaml` is not modified

---

## YAML Validity

### TC-23: All output files are valid YAML
**Given** any successful processing run
**When** all output files are loaded with a YAML parser
**Then** all parse without errors: `incidents/<id>.yaml`, any new `rules/*.yaml`, `ontology.yaml`, `rootcauses.yaml`

---

## Edge Cases & Error Handling

### TC-24: Concurrent access — ontology file locked
**Given** `ontology.yaml` is locked or read-only
**When** the system attempts to write
**Then** the system reports a clear error and does not corrupt existing files
**Expected failure message:** "Error: Cannot write to ontology.yaml — file is locked or read-only"

### TC-25: LLM API failure
**Given** the LLM API is unreachable or returns an error
**When** the system calls the LLM
**Then** the system prints an error to stderr and exits without modifying any YAML files
**Expected failure message:** "Error: LLM API call failed: <details>"

### TC-26: Very large incident file
**Given** an incident file > 100KB of text
**When** the system attempts to process it
**Then** the system either processes it successfully or rejects it with a clear size warning — no silent truncation

### TC-27: Incident with no new ontology entries
**Given** all proposed and confirmed facts use Noun.Property pairs already in the ontology
**When** processing completes
**Then** ontology.yaml is unchanged (no unnecessary writes)

### TC-28: Second incident adds to existing rules and ontology
**Given** one incident has already been processed (ontology and rules exist)
**When** a second incident is processed with some overlapping and some new Noun.Property pairs
**Then** existing ontology entries are reused, new entries are added, new rules are created with their own IDs, and existing rules are not modified
