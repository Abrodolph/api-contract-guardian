# mobile-bff

Backend-for-frontend that shapes user data for mobile app screens.

## API dependencies

| Endpoint | Method | Fields read |
|----------|--------|-------------|
| `/users/{user_id}` | GET | `id`, `full_name`, `email`, `created_at` |
| `/users` | GET | `id`, `full_name`, `email` (per item in `data[]`), `total`, `page` |

## Usage

```bash
pip install -r requirements.txt
python client.py
```

Calls `get_user_profile("usr_1")` and `list_user_summaries()` against `http://localhost:8000`.

## Key functions

```python
get_user_profile(user_id: str) -> dict
```
Returns a mobile-friendly profile card: `{ id, display_name, email, joined, avatar_initials }`.

```python
list_user_summaries(page: int = 1) -> dict
```
Returns a paginated list of compact user records: `{ items: [{id, full_name, email}], total, page }`.
