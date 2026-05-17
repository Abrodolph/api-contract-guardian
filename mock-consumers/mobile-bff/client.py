"""
mobile-bff — shapes user data for mobile app screens.

Field dependencies:
  GET /users/{user_id}   → id, full_name, email, created_at
  GET /users             → id, full_name, email   (per item in data[])
"""

import requests

BASE_URL = "http://localhost:8000"


def get_user_profile(user_id: str) -> dict:
    response = requests.get(f"{BASE_URL}/users/{user_id}")
    response.raise_for_status()
    data = response.json()
    return {
        "id": data["id"],
        "display_name": data["full_name"],
        "email": data["email"],
        "member_since": data["created_at"],
    }


def list_user_summaries(page: int = 1) -> dict:
    response = requests.get(f"{BASE_URL}/users", params={"page": page, "per_page": 50})
    response.raise_for_status()
    payload = response.json()
    summaries = [
        {
            "id": item["id"],
            "full_name": item["full_name"],
            "email": item["email"],
        }
        for item in payload["data"]
    ]
    return {
        "items": summaries,
        "total": payload["total"],
        "page": payload["page"],
    }


def get_user_profile(user_id: str) -> dict:
    """Return a mobile-friendly profile card for the given user."""
    response = requests.get(f"{BASE_URL}/users/{user_id}")
    response.raise_for_status()
    raw = response.json()

    return {
        "id": raw["id"],
        "display_name": raw["full_name"],
        "email": raw["email"],
        "joined": raw["created_at"],
        "avatar_initials": _initials(raw["full_name"]),
    }


def _initials(full_name: str) -> str:
    parts = full_name.split()
    return "".join(p[0].upper() for p in parts[:2])


if __name__ == "__main__":
    profile = get_user_profile("usr_1")
    print("Profile:", profile)

    summaries = list_user_summaries()
    print("Users:", summaries)
