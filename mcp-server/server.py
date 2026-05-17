#!/usr/bin/env python3
"""
Contract Guardian MCP Server
Provides access to OpenAPI specifications for contract testing.
"""

import json
import os
import re
from pathlib import Path
from typing import Any

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent


# Initialize the MCP server
app = Server("contract-guardian")

# Get the project root directory (parent of mcp-server)
PROJECT_ROOT = Path(__file__).parent.parent
OPENAPI_CURRENT = PROJECT_ROOT / "mock-api" / "openapi.json"
OPENAPI_BASELINE = PROJECT_ROOT / "mock-api" / "openapi_baseline.json"
MOCK_CONSUMERS_DIR = PROJECT_ROOT / "mock-consumers"

# Hardcoded consumer registry
CONSUMER_REGISTRY = {
    "billing-service": {
        "fields": {
            "User": ["email", "full_name", "id"],
            "Invoice": ["amount", "currency", "user_id", "id", "status"]
        }
    },
    "mobile-bff": {
        "fields": {
            "User": ["email", "full_name", "id", "created_at"]
        }
    },
    "analytics-worker": {
        "fields": {
            "User": ["email", "id", "created_at"],
            "Invoice": ["amount", "currency", "user_id", "id", "created_at"]
        }
    }
}


@app.list_tools()
async def list_tools() -> list[Tool]:
    """List available tools."""
    return [
        Tool(
            name="get_openapi_spec",
            description="Get OpenAPI specification for the Contract Guardian project. "
                        "Use 'current' to get the current API spec or 'baseline' to get the baseline spec for comparison.",
            inputSchema={
                "type": "object",
                "properties": {
                    "version": {
                        "type": "string",
                        "enum": ["current", "baseline"],
                        "description": "Which version of the OpenAPI spec to retrieve: 'current' or 'baseline'"
                    }
                },
                "required": ["version"]
            }
        ),
        Tool(
            name="get_consumer_registry",
            description="Returns a registry of all known consumers and which fields they read from the API. "
                        "Includes information about which schemas (User, Invoice) and fields each consumer depends on.",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
        Tool(
            name="find_call_sites",
            description="Scans mock-consumers directory recursively for Python files and finds where a specific field is accessed. "
                        "Searches for patterns like data['field_name'], item['field_name'], raw['field_name'], response['field_name']. "
                        "Returns a list of call sites with consumer name, file path, and line number.",
            inputSchema={
                "type": "object",
                "properties": {
                    "field_name": {
                        "type": "string",
                        "description": "The field name to search for (e.g., 'email', 'amount', 'user_id')"
                    }
                },
                "required": ["field_name"]
            }
        )
    ]


@app.call_tool()
async def call_tool(name: str, arguments: Any) -> list[TextContent]:
    """Handle tool calls."""
    if name == "get_openapi_spec":
        return await handle_get_openapi_spec(arguments)
    elif name == "get_consumer_registry":
        return await handle_get_consumer_registry(arguments)
    elif name == "find_call_sites":
        return await handle_find_call_sites(arguments)
    else:
        raise ValueError(f"Unknown tool: {name}")


async def handle_get_openapi_spec(arguments: Any) -> list[TextContent]:
    """Handle get_openapi_spec tool call."""
    version = arguments.get("version")
    if not version:
        raise ValueError("Missing required parameter: version")
    
    if version not in ["current", "baseline"]:
        raise ValueError(f"Invalid version: {version}. Must be 'current' or 'baseline'")
    
    # Determine which file to read
    spec_file = OPENAPI_CURRENT if version == "current" else OPENAPI_BASELINE
    
    # Check if file exists
    if not spec_file.exists():
        raise FileNotFoundError(f"OpenAPI spec file not found: {spec_file}")
    
    # Read and return the spec
    try:
        with open(spec_file, 'r', encoding='utf-8') as f:
            spec_content = f.read()
        
        # Validate it's valid JSON
        json.loads(spec_content)
        
        return [
            TextContent(
                type="text",
                text=f"OpenAPI Specification ({version}):\n\n{spec_content}"
            )
        ]
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in {spec_file}: {e}")
    except Exception as e:
        raise RuntimeError(f"Error reading OpenAPI spec: {e}")


async def handle_get_consumer_registry(arguments: Any) -> list[TextContent]:
    """Handle get_consumer_registry tool call."""
    try:
        registry_json = json.dumps(CONSUMER_REGISTRY, indent=2)
        return [
            TextContent(
                type="text",
                text=f"Consumer Registry:\n\n{registry_json}"
            )
        ]
    except Exception as e:
        raise RuntimeError(f"Error generating consumer registry: {e}")


async def handle_find_call_sites(arguments: Any) -> list[TextContent]:
    """Handle find_call_sites tool call."""
    field_name = arguments.get("field_name")
    if not field_name:
        raise ValueError("Missing required parameter: field_name")
    
    # Check if mock-consumers directory exists
    if not MOCK_CONSUMERS_DIR.exists():
        raise FileNotFoundError(f"Mock consumers directory not found: {MOCK_CONSUMERS_DIR}")
    
    call_sites = []
    
    # Pattern to match field access: data["field"], item["field"], raw["field"], response["field"]
    # Also match single quotes: data['field']
    pattern = re.compile(
        rf'(data|item|raw|response|u|inv|payload)\[(["\']){re.escape(field_name)}\2\]'
    )
    
    try:
        # Recursively search all .py files in mock-consumers
        for py_file in MOCK_CONSUMERS_DIR.rglob("*.py"):
            # Skip __pycache__ and other non-source files
            if "__pycache__" in str(py_file):
                continue
            
            # Determine consumer name from directory structure
            relative_path = py_file.relative_to(MOCK_CONSUMERS_DIR)
            consumer_name = relative_path.parts[0] if len(relative_path.parts) > 1 else "unknown"
            
            # Read file and search for pattern
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    for line_num, line in enumerate(f, start=1):
                        if pattern.search(line):
                            call_sites.append({
                                "name": consumer_name,
                                "file": str(py_file.relative_to(PROJECT_ROOT)).replace("\\", "/"),
                                "line": line_num
                            })
            except Exception as e:
                # Skip files that can't be read
                continue
        
        # Format results
        if call_sites:
            result_json = json.dumps(call_sites, indent=2)
            return [
                TextContent(
                    type="text",
                    text=f"Call sites for field '{field_name}':\n\n{result_json}"
                )
            ]
        else:
            return [
                TextContent(
                    type="text",
                    text=f"No call sites found for field '{field_name}'"
                )
            ]
    except Exception as e:
        raise RuntimeError(f"Error searching for call sites: {e}")


async def main():
    """Run the MCP server."""
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())

# Made with Bob
