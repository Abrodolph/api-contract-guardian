#!/usr/bin/env python3
"""
Contract Guardian MCP Server
Provides access to OpenAPI specifications for contract testing.
"""

import json
import os
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
        )
    ]


@app.call_tool()
async def call_tool(name: str, arguments: Any) -> list[TextContent]:
    """Handle tool calls."""
    if name != "get_openapi_spec":
        raise ValueError(f"Unknown tool: {name}")
    
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
