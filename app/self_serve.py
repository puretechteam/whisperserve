from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException
from fastapi import Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from app.auth.api_key import generate_api_key, get_api_key_owner, get_api_key, get_api_key_tier
from app.billing import get_db
from app.billing.provisioning import provision_api_key
from app.logging.usage import get_usage, get_analytics


router = APIRouter()


class SignupRequest(BaseModel):
    email: str


class SignupResponse(BaseModel):
    api_key: str
    user_id: str


@router.post("/self-serve/signup", response_model=SignupResponse)
async def signup(request: SignupRequest):
    email = request.email
    result = provision_api_key(email)
    return SignupResponse(api_key=result["api_key"], user_id=email)


class TierResponse(BaseModel):
    tier: str


class TierUpgradeRequest(BaseModel):
    tier: str


@router.get("/self-serve/tier", response_model=TierResponse)
async def get_tier(api_key: str = Depends(get_api_key)):
    tier = get_api_key_tier(api_key)
    return TierResponse(tier=tier)


@router.post("/self-serve/tier", response_model=TierResponse)
async def upgrade_tier(
    request: TierUpgradeRequest,
    api_key: str = Depends(get_api_key),
):
    if request.tier not in ("pay-as-you-go", "enterprise"):
        raise HTTPException(status_code=400, detail="Invalid tier")
    db = get_db()
    owner = get_api_key_owner(api_key)
    if owner is None:
        raise HTTPException(status_code=401, detail="Invalid API key")
    rows = list(db["api_keys"].rows_where("owner = ?", (owner,)))
    if not rows:
        raise HTTPException(status_code=404, detail="API key not found")
    db["api_keys"].update(rows[0]["id"], {"tier": request.tier})
    return TierResponse(tier=request.tier)


class TierDetail(BaseModel):
    tier: str
    price_per_call: float | None
    daily_limit: int | None
    description: str


TIERS = [
    TierDetail(
        tier="free",
        price_per_call=0,
        daily_limit=100,
        description="Free tier — 100 calls per day",
    ),
    TierDetail(
        tier="pay-as-you-go",
        price_per_call=0.10,
        daily_limit=10000,
        description="Pro tier — $0.10 per call, 10,000 calls per day",
    ),
    TierDetail(
        tier="enterprise",
        price_per_call=None,
        daily_limit=None,
        description="Enterprise tier — custom pricing, contact us",
    ),
]


@router.get("/self-serve/tiers", response_model=list[TierDetail])
async def list_tiers():
    return TIERS


@router.get("/self-serve/dashboard")
async def dashboard(api_key: str = Depends(get_api_key)):
    return get_usage(api_key)


@router.get("/self-serve/analytics")
async def analytics(api_key: str = Depends(get_api_key)):
    return JSONResponse(content=get_analytics(api_key))


@router.get("/self-serve/api-keys")
async def list_api_keys(api_key: str = Depends(get_api_key)):
    owner = get_api_key_owner(api_key)
    if owner is None:
        raise HTTPException(status_code=401, detail="Invalid API key")
    db = get_db()
    rows = list(db["api_keys"].rows_where("owner = ?", (owner,)))
    return [
        {
            "id": r["id"],
            "api_key": r["api_key"],
            "created_at": r["created_at"],
            "revoked": r["revoked"],
        }
        for r in rows
    ]


@router.delete("/self-serve/api-keys/{key_id}")
async def revoke_api_key(key_id: int, api_key: str = Depends(get_api_key)):
    owner = get_api_key_owner(api_key)
    if owner is None:
        raise HTTPException(status_code=401, detail="Invalid API key")
    db = get_db()
    row = db["api_keys"].get(key_id)
    if row is None or row.get("owner") != owner:
        raise HTTPException(status_code=404, detail="API key not found")
    db["api_keys"].update(row["id"], {"revoked": True})
    return {"detail": "API key revoked"}