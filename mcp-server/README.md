# Contract Guardian MCP Server

A Model Context Protocol (MCP) server that provides access to OpenAPI specifications for the Contract Guardian project.

## Features

### Tools

1. **get_openapi_spec** - Retrieve OpenAPI specifications
   - `version: "current"` - Returns the current API specification from `/mock-api/openapi.json`
   - `version: "baseline"` - Returns the baseline API specification from `/mock-api/openapi_baseline.json`

2. **get_consumer_registry** - Get the registry of all known API consumers
   - No parameters required
   - Returns a JSON object mapping consumer names to the fields they read from each schema
   - Example output:
     ```json
     {
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
     ```

3. **find_call_sites** - Find where a specific field is accessed in consumer code
   - `field_name: string` - The field name to search for (e.g., "email", "amount", "user_id")
   - Recursively scans `/mock-consumers` directory for Python files
   - Searches for patterns like `data["field_name"]`, `item["field_name"]`, `raw["field_name"]`, etc.
   - Returns a list of call sites with consumer name, file path, and line number
   - Example output for `find_call_sites("email")`:
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

## Usage Examples

Once registered with Bob Shell, you can use the tools:

### Get OpenAPI Specification

```
Tool: get_openapi_spec
Parameters: {"version": "current"}
```

### Get Consumer Registry

```
Tool: get_consumer_registry
Parameters: {}
```

### Find Field Call Sites

```
Tool: find_call_sites
Parameters: {"field_name": "email"}
```

This will return all locations where the "email" field is accessed across all consumer services.

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
