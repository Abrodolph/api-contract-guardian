from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Literal, Optional
from datetime import datetime, timezone
import uuid
import sys
import os

# Add parent directory to path to import cloud module
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from cloud import cloudant_store
    CLOUDANT_AVAILABLE = cloudant_store.is_cloudant_available()
except Exception as e:
    print(f"Cloudant not available, using in-memory store: {e}")
    CLOUDANT_AVAILABLE = False

try:
    from cloud import granite_alert
    GRANITE_AVAILABLE = True
except Exception as e:
    print(f"Granite alert not available: {e}")
    GRANITE_AVAILABLE = False

app = FastAPI(title="API Contract Guardian")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# --- Models ---

class CallSite(BaseModel):
    file: str
    line: int


class Consumer(BaseModel):
    name: str
    call_sites: list[CallSite]


class BlastRadius(BaseModel):
    consumers: list[Consumer]
    total_call_sites: int


class VerdictIn(BaseModel):
    verdict: Literal["BREAKING", "SAFE", "REVIEW"]
    change_summary: str
    affected_field: Optional[str] = None
    blast_radius: BlastRadius
    reasoning: str


class VerdictDoc(VerdictIn):
    id: str
    timestamp: str
    alert: Optional[str] = None


# --- In-memory store ---

_store: list[VerdictDoc] = []


# --- Seed data ---

def _make_seed() -> list[VerdictDoc]:
    def ts(h: int, m: int = 0) -> str:
        return datetime(2026, 5, 17, h, m, 0, tzinfo=timezone.utc).isoformat()

    return [
        VerdictDoc(
            id=str(uuid.uuid4()),
            timestamp=ts(10),
            verdict="BREAKING",
            change_summary="Removed `user_id` field from GET /orders response",
            affected_field="user_id",
            blast_radius=BlastRadius(
                consumers=[
                    Consumer(name="billing-service", call_sites=[
                        CallSite(file="src/billing/orders.py", line=42),
                        CallSite(file="src/billing/reports.py", line=87),
                    ]),
                    Consumer(name="analytics-service", call_sites=[
                        CallSite(file="src/analytics/pipeline.py", line=15),
                    ]),
                ],
                total_call_sites=3,
            ),
            reasoning="Removing a response field is a hard break for all consumers that read it.",
        ),
        VerdictDoc(
            id=str(uuid.uuid4()),
            timestamp=ts(11, 30),
            verdict="BREAKING",
            change_summary="Changed `amount` type from string to integer in POST /payments",
            affected_field="amount",
            blast_radius=BlastRadius(
                consumers=[
                    Consumer(name="mobile-bff", call_sites=[
                        CallSite(file="src/mobile/payments.ts", line=23),
                        CallSite(file="src/mobile/checkout.ts", line=101),
                        CallSite(file="src/mobile/history.ts", line=67),
                    ]),
                ],
                total_call_sites=3,
            ),
            reasoning="Type change on a required request field causes deserialization failures in all callers.",
        ),
        VerdictDoc(
            id=str(uuid.uuid4()),
            timestamp=ts(12),
            verdict="SAFE",
            change_summary="Added optional `metadata` field to GET /products response",
            affected_field=None,
            blast_radius=BlastRadius(consumers=[], total_call_sites=0),
            reasoning="Adding an optional field to a response is additive and backwards-compatible.",
        ),
        VerdictDoc(
            id=str(uuid.uuid4()),
            timestamp=ts(13),
            verdict="SAFE",
            change_summary="Added optional query param `include_archived` to GET /users",
            affected_field=None,
            blast_radius=BlastRadius(consumers=[], total_call_sites=0),
            reasoning="Optional query parameters with defaults do not affect existing callers.",
        ),
        VerdictDoc(
            id=str(uuid.uuid4()),
            timestamp=ts(14),
            verdict="REVIEW",
            change_summary="Renamed enum value `pending` → `queued` in GET /jobs response",
            affected_field="status",
            blast_radius=BlastRadius(
                consumers=[
                    Consumer(name="worker-service", call_sites=[
                        CallSite(file="src/worker/poll.py", line=55),
                    ]),
                ],
                total_call_sites=1,
            ),
            reasoning="Enum value rename may break consumers comparing against the old string literal. Manual review recommended.",
        ),
    ]


_store.extend(_make_seed())


# --- Endpoints ---

@app.post("/verdict", response_model=VerdictDoc)
def post_verdict(body: VerdictIn):
    # Generate plain-English alert for BREAKING verdicts before storing
    alert: Optional[str] = None
    if body.verdict == "BREAKING" and GRANITE_AVAILABLE:
        try:
            raw = granite_alert.generate_alert(body.model_dump())
            alert = raw if raw else None
        except Exception as e:
            print(f"Granite alert error: {e}")

    verdict_dict = body.model_dump()
    if alert:
        verdict_dict["alert"] = alert

    if CLOUDANT_AVAILABLE:
        try:
            stored_doc = cloudant_store.save_verdict(verdict_dict)
            return VerdictDoc(
                id=stored_doc["_id"],
                timestamp=stored_doc["timestamp"],
                verdict=stored_doc["verdict"],
                change_summary=stored_doc["change_summary"],
                affected_field=stored_doc.get("affected_field"),
                blast_radius=BlastRadius(**stored_doc["blast_radius"]),
                reasoning=stored_doc["reasoning"],
                alert=stored_doc.get("alert"),
            )
        except Exception as e:
            print(f"Cloudant error, falling back to in-memory: {e}")

    # In-memory fallback
    doc = VerdictDoc(
        id=str(uuid.uuid4()),
        timestamp=datetime.now(timezone.utc).isoformat(),
        alert=alert,
        **body.model_dump(),
    )
    _store.append(doc)
    return doc


@app.get("/verdicts", response_model=list[VerdictDoc])
def get_verdicts():
    if CLOUDANT_AVAILABLE:
        try:
            docs = cloudant_store.get_all_verdicts()
            return [
                VerdictDoc(
                    id=doc["_id"],
                    timestamp=doc["timestamp"],
                    verdict=doc["verdict"],
                    change_summary=doc["change_summary"],
                    affected_field=doc.get("affected_field"),
                    blast_radius=BlastRadius(**doc["blast_radius"]),
                    reasoning=doc["reasoning"],
                    alert=doc.get("alert"),
                )
                for doc in docs
            ]
        except Exception as e:
            print(f"Cloudant error, falling back to in-memory: {e}")
            # Fall through to in-memory
    
    # In-memory fallback
    return list(reversed(_store))


@app.get("/verdicts/{id}", response_model=VerdictDoc)
def get_verdict(id: str):
    if CLOUDANT_AVAILABLE:
        try:
            doc = cloudant_store.get_verdict_by_id(id)
            if doc:
                return VerdictDoc(
                    id=doc["_id"],
                    timestamp=doc["timestamp"],
                    verdict=doc["verdict"],
                    change_summary=doc["change_summary"],
                    affected_field=doc.get("affected_field"),
                    blast_radius=BlastRadius(**doc["blast_radius"]),
                    reasoning=doc["reasoning"],
                    alert=doc.get("alert"),
                )
        except Exception as e:
            print(f"Cloudant error, falling back to in-memory: {e}")
            # Fall through to in-memory
    
    # In-memory fallback
    for doc in _store:
        if doc.id == id:
            return doc
    raise HTTPException(status_code=404, detail="Verdict not found")


@app.get("/contract-health", response_model=dict)
def get_contract_health():
    """Get verdict counts grouped by day for the last 30 days (trend chart data)."""
    if CLOUDANT_AVAILABLE:
        try:
            return cloudant_store.get_contract_health()
        except Exception as e:
            print(f"Cloudant error, falling back to in-memory: {e}")
            # Fall through to in-memory
    
    # In-memory fallback - simple aggregation
    from collections import defaultdict
    from datetime import timedelta
    
    day_counts = defaultdict(lambda: {"BREAKING": 0, "SAFE": 0, "REVIEW": 0})
    
    # Count verdicts by day
    for doc in _store:
        day = doc.timestamp[:10]  # Extract YYYY-MM-DD
        day_counts[day][doc.verdict] += 1
    
    # Generate last 30 days
    end_date = datetime.now(timezone.utc)
    days = []
    for i in range(30, -1, -1):  # 30 days ago to today
        day = (end_date - timedelta(days=i)).date().isoformat()
        days.append(day)
    
    return {
        "days": days,
        "breaking": [day_counts[day]["BREAKING"] for day in days],
        "safe": [day_counts[day]["SAFE"] for day in days],
        "review": [day_counts[day]["REVIEW"] for day in days],
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
