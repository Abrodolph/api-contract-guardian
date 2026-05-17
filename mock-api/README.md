# Mock API — User & Billing Service

A minimal FastAPI app that simulates a user-and-billing backend. Used as a stable target for API contract diffing.

## Setup

```bash
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

If you prefer the package-style module path, this also works:

```bash
uvicorn app.main:app --reload --port 8000
```

Interactive docs at <http://localhost:8000/docs>.

---

## Endpoints

### `GET /health`
Returns service liveness. No auth required.

**Response 200**
```json
{ "status": "ok", "version": "1.0.0" }
```

---

### `GET /users`
Paginated list of all users.

**Query params**

| param | type | default | description |
|-------|------|---------|-------------|
| `page` | integer | 1 | Page number (≥ 1) |
| `per_page` | integer | 20 | Results per page (1–100) |

**Response 200** — `UserList`
```json
{
  "data": [{ "id": "usr_1", "email": "alice@example.com", ... }],
  "total": 3,
  "page": 1,
  "per_page": 20
}
```

---

### `GET /users/{user_id}`
Fetch a single user by ID (e.g. `usr_1`).

**Response 200** — `User`
```json
{
  "id": "usr_1",
  "email": "alice@example.com",
  "name": "Alice Chen",
  "plan": "pro",
  "status": "active",
  "created_at": "2024-01-15T10:30:00"
}
```

**Response 404** when the user ID does not exist.

---

### `POST /invoices`
Create a new invoice for a user.

**Request body** — `CreateInvoiceRequest`
```json
{
  "user_id": "usr_1",
  "due_date": "2024-02-28",
  "currency": "usd",
  "line_items": [
    {
      "description": "Pro Plan - February 2024",
      "quantity": 1,
      "unit_price_cents": 4999,
      "amount_cents": 4999
    }
  ]
}
```

**Response 201** — `Invoice` with `status: "pending"` and a generated `id`.

**Response 404** when `user_id` does not exist.

---

### `GET /invoices/{invoice_id}`
Fetch a single invoice by ID (e.g. `inv_1`).

**Response 200** — `Invoice`
```json
{
  "id": "inv_1",
  "user_id": "usr_1",
  "amount_cents": 4999,
  "currency": "usd",
  "status": "paid",
  "line_items": [...],
  "created_at": "2024-01-01T00:00:00",
  "due_date": "2024-01-31"
}
```

**Response 404** when the invoice ID does not exist.

---

## Spec files

| file | purpose |
|------|---------|
| `openapi.json` | Current spec — update this when the API changes |
| `openapi_baseline.json` | Frozen reference snapshot used for contract diffing |

The contract guardian diffs `openapi_baseline.json` → `openapi.json` to detect breaking changes.
