# SFI-020 — Builder Decision Notes

## Work Item
**SFI-020**: Right-Click KPI Row → Analyze with LLM (Core)

## Git Operations
- Feature branch `SFI-020` created from `SFI-019`
- All files staged and ready for commit

## Build Verification
| Step | Command | Result |
|------|---------|--------|
| Install (dev) | `pip install -e ".[dev]"` | ✅ Installed `openai-2.17.0` + deps |
| Tests | `python -m pytest tests/ -q` | ✅ **180/180 passed** (0.76s) |
| New dependency | `openai>=1.0.0` | Resolved to `openai-2.17.0` |

## New Dependencies Pulled In
| Package | Version | Required By |
|---------|---------|-------------|
| `openai` | 2.17.0 | LLM analysis feature |
| `httpx` | (transitive) | openai SDK |
| `pydantic` | (transitive) | openai SDK |
| `distro` | 1.9.0 | openai SDK |
| `jiter` | 0.13.0 | openai SDK |
| `sniffio` | 1.3.1 | openai SDK |
| `tqdm` | 4.67.3 | openai SDK |

## Build Warnings
- None

## Environment Requirements
- Python ≥ 3.10
- Environment variables for Azure OpenAI (feature-specific, not required for basic app operation)
