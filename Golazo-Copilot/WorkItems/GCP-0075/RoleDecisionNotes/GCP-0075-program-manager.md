# GCP-0075 Program Manager Decision Notes

## Decisions

- Preserve the enforced role order: Documenter then Builder.
- Assign non-release documentation review to Documenter without future-role prerequisites.
- Assign release classification, canonical version update, changelog, validation, packaging, commit, and push to Builder.
- Preserve Complete, Express, and Spike role sequences; Builder ownership works in both release-capable profiles.
- Verify packaged defaults and force-bootstrap generated copies with policy tests.

## Success Metric

A release completes with zero mandatory backward role transitions and one consistent version across `pyproject.toml`, changelog, and built metadata.

## Rollout

Ship as packaged instruction, README, and policy-test changes. Existing customized role copies remain untouched unless bootstrap runs with force.
