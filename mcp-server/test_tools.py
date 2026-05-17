#!/usr/bin/env python3
"""
Test script for the new MCP server tools.
"""

import json
import re
from pathlib import Path

# Simulate the server's logic
PROJECT_ROOT = Path(__file__).parent.parent
MOCK_CONSUMERS_DIR = PROJECT_ROOT / "mock-consumers"

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

def test_consumer_registry():
    """Test get_consumer_registry functionality."""
    print("=== Testing Consumer Registry ===")
    print(json.dumps(CONSUMER_REGISTRY, indent=2))
    print()

def test_find_call_sites(field_name):
    """Test find_call_sites functionality."""
    print(f"=== Testing find_call_sites for '{field_name}' ===")
    
    call_sites = []
    pattern = re.compile(
        rf'(data|item|raw|response|u|inv|payload)\[(["\']){re.escape(field_name)}\2\]'
    )
    
    for py_file in MOCK_CONSUMERS_DIR.rglob("*.py"):
        if "__pycache__" in str(py_file):
            continue
        
        relative_path = py_file.relative_to(MOCK_CONSUMERS_DIR)
        consumer_name = relative_path.parts[0] if len(relative_path.parts) > 1 else "unknown"
        
        try:
            with open(py_file, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f, start=1):
                    if pattern.search(line):
                        call_sites.append({
                            "name": consumer_name,
                            "file": str(py_file.relative_to(PROJECT_ROOT)).replace("\\", "/"),
                            "line": line_num
                        })
        except Exception:
            continue
    
    print(json.dumps(call_sites, indent=2))
    print()

if __name__ == "__main__":
    test_consumer_registry()
    test_find_call_sites("email")
    test_find_call_sites("amount")
    test_find_call_sites("user_id")

# Made with Bob
