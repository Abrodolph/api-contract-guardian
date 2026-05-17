"""
Generates the 15 remaining labeled eval cases (cases 004-018).
Run from repo root: python engine/eval/generate_cases.py
Already-existing cases (001-003) are left untouched.
"""
import copy
import json
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent.parent
BASELINE = REPO_ROOT / "mock-api" / "openapi_baseline.json"
CASES_DIR = Path(__file__).parent / "cases"


def load_baseline() -> dict:
    return json.loads(BASELINE.read_text(encoding="utf-8"))


def write_case(name: str, verdict: str, spec: dict) -> None:
    d = CASES_DIR / name
    d.mkdir(parents=True, exist_ok=True)
    (d / "current_spec.json").write_text(json.dumps(spec, indent=2), encoding="utf-8")
    (d / "expected.json").write_text(json.dumps({"verdict": verdict}), encoding="utf-8")
    print(f"  {name}  ->  {verdict}")


# ── BREAKING cases (6 more, total 7 with case_001) ────────────────────────────

def b004_rename_name_to_full_name(spec: dict) -> None:
    user = spec["components"]["schemas"]["User"]
    props = user["properties"]
    props["full_name"] = props.pop("name")
    req = user["required"]
    req[req.index("name")] = "full_name"


def b005_plan_type_change(spec: dict) -> None:
    user = spec["components"]["schemas"]["User"]
    user["properties"]["plan"] = {"type": "integer", "example": 1}


def b006_add_required_request_field(spec: dict) -> None:
    req_schema = spec["components"]["schemas"]["CreateInvoiceRequest"]
    req_schema["required"].append("currency_code")
    req_schema["properties"]["currency_code"] = {
        "type": "string",
        "description": "ISO 4217 currency code",
        "example": "USD",
    }


def b007_path_change(spec: dict) -> None:
    paths = spec["paths"]
    paths["/users/{id}"] = paths.pop("/users/{user_id}")


def b008_method_change(spec: dict) -> None:
    invoices = spec["paths"]["/invoices"]
    invoices["put"] = invoices.pop("post")


def b009_remove_currency_field(spec: dict) -> None:
    invoice = spec["components"]["schemas"]["Invoice"]
    invoice["properties"].pop("currency")
    invoice["required"].remove("currency")


# ── SAFE cases (6 more, total 7 with case_002) ────────────────────────────────

def s010_add_optional_phone(spec: dict) -> None:
    user = spec["components"]["schemas"]["User"]
    user["properties"]["phone"] = {"type": "string", "example": "+1-555-0100"}


def s011_add_new_endpoint(spec: dict) -> None:
    spec["paths"]["/users/{user_id}/invoices"] = {
        "get": {
            "tags": ["invoices"],
            "summary": "List User Invoices",
            "operationId": "list_user_invoices_get",
            "parameters": [
                {
                    "name": "user_id",
                    "in": "path",
                    "required": True,
                    "schema": {"type": "string"},
                }
            ],
            "responses": {
                "200": {
                    "description": "Invoices belonging to the user",
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "array",
                                "items": {"$ref": "#/components/schemas/Invoice"},
                            }
                        }
                    },
                }
            },
        }
    }


def s012_add_optional_request_field(spec: dict) -> None:
    req_schema = spec["components"]["schemas"]["CreateInvoiceRequest"]
    req_schema["properties"]["notes"] = {
        "type": "string",
        "description": "Optional internal notes for this invoice",
        "example": "Rush order",
    }


def s013_description_only(spec: dict) -> None:
    user = spec["components"]["schemas"]["User"]
    user["properties"]["email"]["description"] = (
        "Primary email address of the user (must be unique across accounts)"
    )


def s014_add_sort_query_param(spec: dict) -> None:
    spec["paths"]["/users"]["get"]["parameters"].append(
        {
            "name": "sort",
            "in": "query",
            "required": False,
            "schema": {
                "type": "string",
                "enum": ["created_at", "email", "name"],
                "default": "created_at",
            },
        }
    )


def s015_add_new_response_field(spec: dict) -> None:
    user = spec["components"]["schemas"]["User"]
    user["properties"]["updated_at"] = {"type": "string", "format": "date-time"}


# ── REVIEW cases (3 more, total 4 with case_003) ──────────────────────────────

def r016_remove_plan_enum_value(spec: dict) -> None:
    user = spec["components"]["schemas"]["User"]
    user["properties"]["plan"]["enum"] = ["free", "pro"]


def r017_widen_amount_type(spec: dict) -> None:
    invoice = spec["components"]["schemas"]["Invoice"]
    invoice["properties"]["amount_cents"]["type"] = "number"


def r018_add_nullable(spec: dict) -> None:
    user = spec["components"]["schemas"]["User"]
    user["properties"]["email"]["nullable"] = True


# ── Main ──────────────────────────────────────────────────────────────────────

CASES = [
    ("case_004_breaking_field_renamed",         "BREAKING", b004_rename_name_to_full_name),
    ("case_005_breaking_type_change",           "BREAKING", b005_plan_type_change),
    ("case_006_breaking_required_field_added",  "BREAKING", b006_add_required_request_field),
    ("case_007_breaking_path_change",           "BREAKING", b007_path_change),
    ("case_008_breaking_method_change",         "BREAKING", b008_method_change),
    ("case_009_breaking_field_removed_currency","BREAKING", b009_remove_currency_field),
    ("case_010_safe_new_optional_field",        "SAFE",     s010_add_optional_phone),
    ("case_011_safe_new_endpoint",              "SAFE",     s011_add_new_endpoint),
    ("case_012_safe_new_optional_request_field","SAFE",     s012_add_optional_request_field),
    ("case_013_safe_description_change",        "SAFE",     s013_description_only),
    ("case_014_safe_new_query_param",           "SAFE",     s014_add_sort_query_param),
    ("case_015_safe_new_response_field",        "SAFE",     s015_add_new_response_field),
    ("case_016_review_enum_value_removed",      "REVIEW",   r016_remove_plan_enum_value),
    ("case_017_review_type_widening",           "REVIEW",   r017_widen_amount_type),
    ("case_018_review_nullability_change",      "REVIEW",   r018_add_nullable),
]

if __name__ == "__main__":
    print(f"Generating {len(CASES)} cases into {CASES_DIR.relative_to(REPO_ROOT)}\n")
    for name, verdict, mutate in CASES:
        spec = load_baseline()
        mutate(spec)
        write_case(name, verdict, spec)
    print(f"\nDone. Total cases now: 3 existing + {len(CASES)} new = {3 + len(CASES)}")
