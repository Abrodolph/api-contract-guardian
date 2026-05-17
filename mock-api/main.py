from datetime import date, datetime
from typing import List
import uuid

from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel

app = FastAPI(
    title="User & Billing Service",
    description="Mock service for managing users and invoices",
    version="1.0.0",
)


# ── Models ────────────────────────────────────────────────────────────────────

class User(BaseModel):
    id: str
    email: str
    name: str
    plan: str           # free | pro | enterprise
    status: str         # active | suspended | cancelled
    created_at: datetime


class UserList(BaseModel):
    data: List[User]
    total: int
    page: int
    per_page: int


class LineItem(BaseModel):
    description: str
    quantity: int
    unit_price_cents: int
    amount_cents: int


class Invoice(BaseModel):
    id: str
    user_id: str
    amount_cents: int
    currency: str
    status: str         # draft | pending | paid | void
    line_items: List[LineItem]
    created_at: datetime
    due_date: date


class CreateInvoiceRequest(BaseModel):
    user_id: str
    line_items: List[LineItem]
    due_date: date
    currency: str = "usd"


class HealthResponse(BaseModel):
    status: str
    version: str


# ── Seed data ─────────────────────────────────────────────────────────────────

USERS: dict[str, User] = {
    "usr_1": User(
        id="usr_1",
        email="alice@example.com",
        name="Alice Chen",
        plan="pro",
        status="active",
        created_at=datetime(2024, 1, 15, 10, 30, 0),
    ),
    "usr_2": User(
        id="usr_2",
        email="bob@example.com",
        name="Bob Smith",
        plan="free",
        status="active",
        created_at=datetime(2024, 2, 20, 14, 0, 0),
    ),
    "usr_3": User(
        id="usr_3",
        email="carol@example.com",
        name="Carol Davis",
        plan="enterprise",
        status="active",
        created_at=datetime(2023, 11, 5, 9, 0, 0),
    ),
}

INVOICES: dict[str, Invoice] = {
    "inv_1": Invoice(
        id="inv_1",
        user_id="usr_1",
        amount_cents=4999,
        currency="usd",
        status="paid",
        line_items=[
            LineItem(
                description="Pro Plan - January 2024",
                quantity=1,
                unit_price_cents=4999,
                amount_cents=4999,
            )
        ],
        created_at=datetime(2024, 1, 1, 0, 0, 0),
        due_date=date(2024, 1, 31),
    ),
}


# ── Routes ────────────────────────────────────────────────────────────────────

@app.get("/health", response_model=HealthResponse, tags=["system"])
def health():
    return HealthResponse(status="ok", version="1.0.0")


@app.get("/users", response_model=UserList, tags=["users"])
def list_users(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
):
    all_users = list(USERS.values())
    start = (page - 1) * per_page
    return UserList(
        data=all_users[start : start + per_page],
        total=len(all_users),
        page=page,
        per_page=per_page,
    )


@app.get("/users/{user_id}", response_model=User, tags=["users"])
def get_user(user_id: str):
    user = USERS.get(user_id)
    if not user:
        raise HTTPException(status_code=404, detail=f"User '{user_id}' not found")
    return user


@app.post("/invoices", response_model=Invoice, status_code=201, tags=["invoices"])
def create_invoice(body: CreateInvoiceRequest):
    if body.user_id not in USERS:
        raise HTTPException(status_code=404, detail=f"User '{body.user_id}' not found")
    total_cents = sum(item.amount_cents for item in body.line_items)
    invoice_id = f"inv_{uuid.uuid4().hex[:8]}"
    inv = Invoice(
        id=invoice_id,
        user_id=body.user_id,
        amount_cents=total_cents,
        currency=body.currency,
        status="pending",
        line_items=body.line_items,
        created_at=datetime.utcnow(),
        due_date=body.due_date,
    )
    INVOICES[invoice_id] = inv
    return inv


@app.get("/invoices/{invoice_id}", response_model=Invoice, tags=["invoices"])
def get_invoice(invoice_id: str):
    invoice = INVOICES.get(invoice_id)
    if not invoice:
        raise HTTPException(status_code=404, detail=f"Invoice '{invoice_id}' not found")
    return invoice
