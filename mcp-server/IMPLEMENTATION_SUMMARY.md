# MCP Server Extension - Implementation Summary

## Overview

Extended the Contract Guardian MCP server with two new tools for consumer field dependency tracking.

## New Tools Added

### 1. get_consumer_registry()

**Purpose:** Returns a hardcoded registry of all known consumers and their field dependencies.

**Implementation:**

- Defined `CONSUMER_REGISTRY` constant with consumer-to-field mappings
- Covers three consumers: billing-service, mobile-bff, analytics-worker
- Maps each consumer to schemas (User, Invoice) and their accessed fields
- Returns JSON-formatted registry

**Example Output:**

```json
{
  "billing-service": {
    "fields": {
      "User": ["email", "full_name", "id"],
      "Invoice": ["amount", "currency", "user_id", "id", "status"]
    }
  },
  ...
}
```

### 2. find_call_sites(field_name)

**Purpose:** Scans consumer code to find where specific fields are accessed.

**Implementation:**

- Recursively scans `/mock-consumers` directory for `.py` files
- Uses regex pattern to match field access: `(data|item|raw|response|u|inv|payload)["field_name"]`
- Supports both single and double quotes
- Returns list of call sites with consumer name, file path, and line number
- Handles errors gracefully (skips unreadable files)

**Example Output for find_call_sites("email"):**

```json
[
  {
    "name": "billing-service",
    "file": "mock-consumers/billing-service/client.py",
    "line": 20
  },
  {
    "name": "mobile-bff",
    "file": "mock-consumers/mobile-bff/client.py",
    "line": 21
  },
  {
    "name": "analytics-worker",
    "file": "mock-consumers/analytics-worker/client.py",
    "line": 21
  }
]
```

## Code Changes

### server.py

1. Added `import re` for regex pattern matching
2. Added `MOCK_CONSUMERS_DIR` constant pointing to mock-consumers directory
3. Added `CONSUMER_REGISTRY` constant with hardcoded consumer field mappings
4. Extended `list_tools()` to include two new tool definitions
5. Refactored `call_tool()` to dispatch to handler functions
6. Added `handle_get_consumer_registry()` function
7. Added `handle_find_call_sites()` function with regex-based file scanning

### README.md

- Updated Features section with detailed documentation for all three tools
- Added usage examples for each tool
- Included sample outputs for better understanding

### requirements.txt

- No changes needed (only uses standard library + existing mcp dependency)

## Testing

Created `test_tools.py` to verify functionality:

- ✅ Consumer registry returns correct structure
- ✅ find_call_sites("email") finds 6 call sites across 3 consumers
- ✅ find_call_sites("amount") finds 4 call sites
- ✅ find_call_sites("user_id") finds 3 call sites

## Files Modified

- `mcp-server/server.py` - Core implementation
- `mcp-server/README.md` - Documentation
- `mcp-server/test_tools.py` - Test script (new file)
- `mcp-server/IMPLEMENTATION_SUMMARY.md` - This file (new)

## Integration

The MCP server maintains backward compatibility with the existing `get_openapi_spec` tool while adding the new consumer tracking capabilities. All tools follow the same async pattern and error handling conventions.
