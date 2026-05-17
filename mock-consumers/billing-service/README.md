# billing-service

Processes payments by combining user and invoice data from the mock API.

## API dependencies

| Endpoint | Method | Fields read |
|----------|--------|-------------|
| `/users/{user_id}` | GET | `id`, `email`, `full_name` |
| `/invoices/{invoice_id}` | GET | `id`, `amount`, `currency`, `status`, `user_id` |

## Usage

```bash
pip install -r requirements.txt
python client.py
```

The entry point calls `process_payment("usr_1", "inv_1")` against `http://localhost:8000`.
Override the base URL by setting `BASE_URL` in `client.py`.

## Key function

```python
process_payment(user_id: str, invoice_id: str) -> dict
```

Fetches the user and invoice, guards against non-payable statuses, prints a charge
summary, and returns `{ user_id, invoice_id, charged_amount, currency, result }`.
