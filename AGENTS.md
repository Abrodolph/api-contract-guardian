# AGENTS.md

This file provides guidance to agents when working with code in this repository.

## Project Overview

API Contract Guardian — automated API governance tool that detects breaking changes between OpenAPI spec versions. Built for IBM Bob hackathon.

## Stack

- Python 3.x
- FastAPI (mock API)
- MCP (Model Context Protocol) server
- Bob Shell with custom modes

## Critical Non-Obvious Patterns

### Eval Harness Behavior

- `engine/eval/run_eval.py` **swaps** `mock-api/openapi.json` per test case, then **always restores** from `openapi_baseline.json` in finally block
- If interrupted, run `python engine/eval/restore_spec.py` to manually restore baseline
- BOB_PATH hardcoded to `C:/Users/saini/AppData/Roaming/npm/bob.cmd` — update for different systems
- Requires `BOBSHELL_API_KEY` in `.env` at repo root (not in subdirectories)

### MCP Server Registration

- MCP server path in `.bob/mcp.json` is **absolute** (`c:/Personal/Code/api-contract-guardian/mcp-server/server.py`)
- Must update this path when cloning to different location
- Server runs via stdio, not HTTP

### Verdict Extraction Strategy

- `run_eval.py` uses **three fallback strategies** to extract verdict from Bob output:
  1. JSON between `---output---` markers
  2. Any `{` character followed by valid JSON with `"verdict"` key
  3. Bare verdict word on its own line
- This is **not standard** — most tools expect single extraction method

### Consumer Call Site Detection

- `find_call_sites` in `mcp-server/server.py` searches for pattern: `(data|item|raw|response|u|inv|payload)["field_name"]`
- Variable names `u` and `inv` are **hardcoded** based on mock consumer code patterns
- Adding new consumers may require updating this regex pattern

### Blast Radius Schema Constraint

- `blast_radius.consumers` **must be array of objects** with `name` and `call_sites` keys
- **Never** simplify to flat string array — this breaks schema validation
- `total_call_sites` must equal sum of all `call_sites` entries across consumers
- For SAFE/REVIEW verdicts: use `{"consumers": [], "total_call_sites": 0}` (not null)

## Running Tests

```bash
# Run full eval harness (18 cases)
cd engine/eval
python run_eval.py

# Restore spec after interruption
python engine/eval/restore_spec.py

# Run mock API server
cd mock-api
uvicorn app.main:app --reload

# Test MCP server tools
cd mcp-server
python test_tools.py
```

## Bob Custom Mode

- Mode slug: `contract-guardian` (defined in `.bob/custom_modes.yaml`)
- Invocation: `bob --chat-mode=contract-guardian --auth-method api-key --yolo -p "..."`
- Mode has **baked-in classification rules** — don't repeat them in prompts
- Output **must be pure JSON** — no markdown fences, no prose before/after

## File Locations That Matter

- Verdict schema: `engine/verdict_schema.json` (canonical contract)
- Baseline spec: `mock-api/openapi_baseline.json` (never modified by eval)
- Current spec: `mock-api/openapi.json` (swapped during eval)
- Consumer registry: hardcoded in `mcp-server/server.py` lines 28-46
