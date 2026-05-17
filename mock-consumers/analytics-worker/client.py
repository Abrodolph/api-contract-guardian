"""
analytics-worker — aggregates user and invoice data for reporting.

Field dependencies:
  GET /users             → id, email, created_at   (per item in data[])
  GET /invoices/{id}     → id, amount, currency, user_id, created_at
"""

import requests
from collections import defaultdict

BASE_URL = "http://localhost:8000"


def fetch_all_users() -> list[dict]:
    response = requests.get(f"{BASE_URL}/users", params={"per_page": 100})
    response.raise_for_status()
    return [
        {
            "id": u["id"],
            "email": u["email"],
            "created_at": u["created_at"],
        }
        for u in response.json()["data"]
    ]


def fetch_invoice(invoice_id: str) -> dict:
    response = requests.get(f"{BASE_URL}/invoices/{invoice_id}")
    response.raise_for_status()
    data = response.json()
    return {
        "id": data["id"],
        "amount": data["amount"],
        "currency": data["currency"],
        "user_id": data["user_id"],
        "created_at": data["created_at"],
    }


def generate_report(invoice_ids: list[str]) -> dict:
    """Aggregate users and invoices into a summary report."""
    users = fetch_all_users()
    invoices = [fetch_invoice(iid) for iid in invoice_ids]

    revenue_by_currency: dict[str, int] = defaultdict(int)
    revenue_by_user: dict[str, int] = defaultdict(int)

    for inv in invoices:
        revenue_by_currency[inv["currency"]] += inv["amount"]
        revenue_by_user[inv["user_id"]] += inv["amount"]

    user_index = {u["id"]: u["email"] for u in users}

    return {
        "user_count": len(users),
        "invoice_count": len(invoices),
        "revenue_by_currency": dict(revenue_by_currency),
        "top_user": max(
            revenue_by_user,
            key=lambda uid: revenue_by_user[uid],
            default=None,
        ),
        "top_user_email": user_index.get(
            max(revenue_by_user, key=lambda uid: revenue_by_user[uid], default="")
        ),
    }


if __name__ == "__main__":
    report = generate_report(["inv_1"])
    print("Report:", report)
