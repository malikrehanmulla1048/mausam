"""MAUSAM API v1 router — aggregates all sub-routers."""
from fastapi import APIRouter
from app.api.v1 import businesses, forecast, customers, invoices, reconciliation, risk, rescue, committee, alerts, passports, demo

router = APIRouter()

router.include_router(businesses.router, prefix="/businesses", tags=["businesses"])
router.include_router(forecast.router, prefix="/businesses", tags=["forecast"])
router.include_router(customers.router, prefix="/businesses", tags=["customers"])
router.include_router(invoices.router, prefix="/businesses", tags=["invoices"])
router.include_router(reconciliation.router, prefix="/businesses", tags=["reconciliation"])
router.include_router(risk.router, prefix="/businesses", tags=["risk"])
router.include_router(rescue.router, prefix="/businesses", tags=["rescue"])
router.include_router(committee.router, prefix="/businesses", tags=["committee"])
router.include_router(alerts.router, prefix="/businesses", tags=["alerts"])
router.include_router(passports.router, tags=["passports"])
router.include_router(demo.router, prefix="/businesses", tags=["demo"])
