# GCP-0050 — Domain Expert Notes

## Domain: LLM Instruction Prompting
- Instruction-following in Copilot works best with: clear section headers, imperative language, short numbered lists, examples
- Prompts >200 lines show diminishing instruction adherence
- The 150-line target is well within the reliable range

## Domain: VS Code Copilot runSubagent
- `runSubagent` takes a `prompt` parameter (string) and `description` (short)
- Subagent gets a fresh context — no shared conversation history
- Subagent returns a single message — it cannot interact with the user
- Available in VS Code Copilot Chat; not available in all environments

## No External Domain Expertise Required
This is a documentation change using established Copilot capabilities.
