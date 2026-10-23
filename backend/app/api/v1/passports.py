"""Health Passport endpoints."""
import uuid
from datetime import date, datetime, timezone
from fastapi import APIRouter, HTTPException
from app.core.database import get_db
from app.services.passport import generate_passport, verify_passport

router = APIRouter()


@router.post("/businesses/{business_id}/passports")
async def create_passport(business_id: str):
    db = get_db()
    biz = db.businesses.find_one({"business_id": business_id}, {"_id": 0})
    if not biz:
        raise HTTPException(404, f"Business {business_id} not found")

    risk = db.risk_assessments.find_one(
        {"business_id": business_id}, sort=[("created_at", -1)]
    ) or {}
    forecast = db.forecast_runs.find_one(
        {"business_id": business_id}, sort=[("created_at", -1)]
    ) or {}
    findings = list(db.reconciliation_findings.find(
        {"business_id": business_id, "status": {"$in": ["OPEN", "REVIEWING"]}}, {"_id": 0}
    ))

    txns = list(db.bank_transactions.find(
        {"business_id": business_id}, {"_id": 0, "date": 1}
    ).sort("date", 1).limit(1))
    txns_end = list(db.bank_transactions.find(
        {"business_id": business_id}, {"_id": 0, "date": 1}
    ).sort("date", -1).limit(1))

    biz["data_period_start"] = txns[0]["date"][:10] if txns else ""
    biz["data_period_end"] = txns_end[0]["date"][:10] if txns_end else ""

    passport = generate_passport(
        business_data=biz,
        risk_assessment=risk,
        forecast=forecast,
        findings=findings,
    )

    db.health_passports.update_one(
        {"passport_id": passport["passport_id"]},
        {"$set": passport},
        upsert=True,
    )

    return passport


@router.get("/businesses/{business_id}/passports")
async def list_passports(business_id: str):
    db = get_db()
    passports = list(db.health_passports.find(
        {"business_id": business_id}, {"_id": 0, "signed_payload": 0}
    ).sort("created_at", -1).limit(10))
    return {"passports": passports, "total": len(passports)}


@router.post("/businesses/{business_id}/passports/{passport_id}/revoke")
async def revoke_passport(business_id: str, passport_id: str, reason: str = "Owner revoked"):
    db = get_db()
    result = db.health_passports.update_one(
        {"business_id": business_id, "passport_id": passport_id},
        {"$set": {
            "revoked": True,
            "revoked_at": datetime.now(timezone.utc).isoformat(),
            "revocation_reason": reason,
        }}
    )
    if result.matched_count == 0:
        raise HTTPException(404, f"Passport {passport_id} not found")
    return {"status": "revoked"}


@router.get("/passports/{public_id}/verify")
async def verify_passport_public(public_id: str):
    db = get_db()
    passport = db.health_passports.find_one({"public_id": public_id}, {"_id": 0})
    if not passport:
        raise HTTPException(404, "Passport not found or link expired.")

    # Log access
    db.passport_access_logs.insert_one({
        "passport_id": passport.get("passport_id"),
        "public_id": public_id,
        "accessed_at": datetime.now(timezone.utc).isoformat(),
        "is_demo": passport.get("is_demo", False),
    })

    result = verify_passport(passport)

    # Return only safe public fields
    return {
        "verification": result,
        "business_name": passport.get("business_name"),
        "generated_at": passport.get("generated_at"),
        "expires_at": passport.get("expires_at"),
        "readiness_band": passport.get("readiness_band") if result.get("verified") else None,
        "runway_days": passport.get("runway_days") if result.get("verified") else None,
        "is_demo": passport.get("is_demo", False),
        "demo_label": "SYNTHETIC DEMONSTRATION DATA" if passport.get("is_demo") else None,
    }
