# GCP-0013: Architect Decision Notes

**Note**: This document was created retroactively to complete the artifact trail.

## Architecture Review

- Version follows standard Python pattern (__version__)
- Exposed in server name for easy discovery
- Included in status response for programmatic access

## Decision

Rather than separate gcp_version tool, version is:
1. In server name (visible in MCP tool listing)
2. In gcp_status response

## Approved

Simple, non-invasive approach.
