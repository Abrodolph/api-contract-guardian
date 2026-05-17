"""
billing-service — fetches user and invoice data to process payments.

Field dependencies:
  GET /users/{user_id}   → id, email, full_name
  GET /invoices/{id}     → id, amount, currency, status, user_id
"""

import requests

BASE_URL = "http://localhost:8000"


def get_user(user_id: str) -> dict:
    response = requests.get(f"{BASE_URL}/users/{user_id}")
    response.raise_for_status()
    data = response.json()
    return {
        "id": data["id"],
        "email": data["email"],
        "full_name": data["full_name"],
    }


def get_invoice(invoice_id: str) -> dict:
    response = requests.get(f"{BASE_URL}/invoices/{invoice_id}")
    response.raise_for_status()
    data = response.json()
    return {
        "id": data["id"],
        "amount": data["amount"],
        "currency": data["currency"],
        "status": data["status"],
        "user_id": data["user_id"],
    }


def process_payment(user_id: str, invoice_id: str) -> dict:
    user = get_user(user_id)
    invoice = get_invoice(invoice_id)

    if invoice["status"] not in ("pending", "draft"):
        raise ValueError(
            f"Invoice {invoice['id']} has status '{invoice['status']}' and cannot be paid"
        )

    print(f"Charging {user['full_name']} <{user['email']}>")
    print(f"  Invoice {invoice['id']}: {invoice['amount']} {invoice['currency'].upper()}")

    return {
        "user_id": user["id"],
        "invoice_id": invoice["id"],
        "charged_amount": invoice["amount"],
        "currency": invoice["currency"],
        "result": "ok",
    }


if __name__ == "__main__":
    result = process_payment("usr_1", "inv_1")
    print(result)
