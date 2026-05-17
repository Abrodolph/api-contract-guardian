# analytics-worker

Aggregates user and invoice data into revenue reports.

## API dependencies

| Endpoint | Method | Fields read |
|----------|--------|-------------|
| `/users` | GET | `id`, `email`, `created_at` (per item in `data[]`) |
| `/invoices/{invoice_id}` | GET | `id`, `amount`, `currency`, `user_id`, `created_at` |

## Usage

```bash
pip install -r requirements.txt
python client.py
```

Calls `generate_report(["inv_1"])` against `http://localhost:8000`.

## Key function

```python
generate_report(invoice_ids: list[str]) -> dict
```

Fetches all users and the given invoices, then returns:

```json
{
  "user_count": 3,
  "invoice_count": 1,
  "revenue_by_currency": { "usd": 4999 },
  "top_user": "usr_1",
  "top_user_email": "alice@example.com"
}
```
