# Contract Guardian MCP Server

A Model Context Protocol (MCP) server that provides access to OpenAPI specifications for the Contract Guardian project.

## Features

- **get_openapi_spec** tool: Retrieve OpenAPI specifications
  - `version: "current"` - Returns the current API specification from `/mock-api/openapi.json`
  - `version: "baseline"` - Returns the baseline API specification from `/mock-api/openapi_baseline.json`

## Installation

1. Navigate to the mcp-server directory:

```bash
cd mcp-server
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

## Running the Server

Run the server directly:

```bash
python server.py
```

The server communicates via stdio and follows the MCP protocol specification.

## Registering with Bob Shell

Add the following configuration to Bob's settings to register this MCP server:

```json
{
  "mcpServers": {
    "contract-guardian": {
      "command": "python",
      "args": ["c:/Personal/Code/api-contract-guardian/mcp-server/server.py"]
    }
  }
}
```

**Note:** Update the path in `args` to match your actual project location.

## Usage Example

Once registered with Bob Shell, you can use the tool:

```
Get the current OpenAPI spec:
- Tool: get_openapi_spec
- Parameters: {"version": "current"}

Get the baseline OpenAPI spec:
- Tool: get_openapi_spec
- Parameters: {"version": "baseline"}
```

## Project Structure

```
mcp-server/
├── server.py          # Main MCP server implementation
├── requirements.txt   # Python dependencies
└── README.md         # This file
```

## Dependencies

- `mcp>=1.0.0` - Model Context Protocol Python SDK

## License

Part of the Contract Guardian project.
