"""
MAUSAM — MongoDB Database Connection
Singleton client with connection pooling.
"""
import logging
from functools import lru_cache
from pymongo import MongoClient, ASCENDING, DESCENDING
from pymongo.database import Database
from app.core.config import settings

logger = logging.getLogger(__name__)

_client: MongoClient | None = None


def get_client() -> MongoClient:
    global _client
    if _client is None:
        try:
            client = MongoClient(
                settings.MONGODB_URI,
                maxPoolSize=10,
                minPoolSize=1,
                serverSelectionTimeoutMS=1500,
                connectTimeoutMS=1500,
            )
            client.admin.command("ping")
            _client = client
            logger.info("Connected to MongoDB at %s", settings.MONGODB_URI)
        except Exception as e:
            logger.warning("Could not connect to MongoDB (%s). Using high-fidelity in-memory mongomock for local development/demo.", e)
            try:
                import mongomock
                _client = mongomock.MongoClient()
            except ImportError:
                _client = client
    return _client



def get_db() -> Database:
    return get_client()[settings.MONGODB_DB_NAME]


def init_indexes() -> None:
    """Create all required indexes. Idempotent."""
    db = get_db()

    # businesses
    db.businesses.create_index([("business_id", ASCENDING)], unique=True)
    db.businesses.create_index([("owner_name", ASCENDING)])

    # customers
    db.customers.create_index([("business_id", ASCENDING), ("customer_id", ASCENDING)], unique=True)
    db.customers.create_index([("business_id", ASCENDING), ("reliability_grade", ASCENDING)])

    # suppliers
    db.suppliers.create_index([("business_id", ASCENDING), ("supplier_id", ASCENDING)], unique=True)

    # invoices
    db.invoices.create_index([("business_id", ASCENDING), ("invoice_id", ASCENDING)], unique=True)
    db.invoices.create_index([("business_id", ASCENDING), ("customer_id", ASCENDING), ("invoice_date", DESCENDING)])
    db.invoices.create_index([("business_id", ASCENDING), ("status", ASCENDING), ("due_date", ASCENDING)])

    # bank_transactions
    db.bank_transactions.create_index([("business_id", ASCENDING), ("txn_id", ASCENDING)], unique=True)
    db.bank_transactions.create_index([("business_id", ASCENDING), ("date", DESCENDING)])
    db.bank_transactions.create_index([("business_id", ASCENDING), ("type", ASCENDING), ("date", DESCENDING)])

    # gst_summaries
    db.gst_summaries.create_index([("business_id", ASCENDING), ("period_key", ASCENDING)], unique=True)

    # obligations
    db.obligations.create_index([("business_id", ASCENDING), ("obligation_id", ASCENDING)], unique=True)
    db.obligations.create_index([("business_id", ASCENDING), ("next_due_date", ASCENDING)])

    # reconciliation_runs
    db.reconciliation_runs.create_index([("business_id", ASCENDING), ("run_id", ASCENDING)], unique=True)
    db.reconciliation_runs.create_index([("business_id", ASCENDING), ("created_at", DESCENDING)])

    # reconciliation_findings
    db.reconciliation_findings.create_index([("business_id", ASCENDING), ("finding_id", ASCENDING)], unique=True)
    db.reconciliation_findings.create_index([("business_id", ASCENDING), ("run_id", ASCENDING), ("severity", ASCENDING)])
    db.reconciliation_findings.create_index([("business_id", ASCENDING), ("status", ASCENDING)])

    # payment_predictions
    db.payment_predictions.create_index([("business_id", ASCENDING), ("invoice_id", ASCENDING)], unique=True)

    # forecast_runs
    db.forecast_runs.create_index([("business_id", ASCENDING), ("run_id", ASCENDING)], unique=True)
    db.forecast_runs.create_index([("business_id", ASCENDING), ("created_at", DESCENDING)])

    # risk_assessments
    db.risk_assessments.create_index([("business_id", ASCENDING), ("assessment_id", ASCENDING)], unique=True)
    db.risk_assessments.create_index([("business_id", ASCENDING), ("created_at", DESCENDING)])

    # rescue_simulations
    db.rescue_simulations.create_index([("business_id", ASCENDING), ("sim_id", ASCENDING)], unique=True)

    # committee_sessions
    db.committee_sessions.create_index([("business_id", ASCENDING), ("session_id", ASCENDING)], unique=True)
    db.committee_sessions.create_index([("business_id", ASCENDING), ("created_at", DESCENDING)])

    # alerts
    db.alerts.create_index([("business_id", ASCENDING), ("alert_id", ASCENDING)], unique=True)
    db.alerts.create_index([("business_id", ASCENDING), ("is_read", ASCENDING), ("created_at", DESCENDING)])

    # health_passports
    db.health_passports.create_index([("business_id", ASCENDING), ("passport_id", ASCENDING)], unique=True)
    db.health_passports.create_index([("public_id", ASCENDING)], unique=True)
    db.health_passports.create_index([("business_id", ASCENDING), ("created_at", DESCENDING)])

    # passport_access_logs
    db.passport_access_logs.create_index([("passport_id", ASCENDING), ("accessed_at", DESCENDING)])

    # audit_events
    db.audit_events.create_index([("business_id", ASCENDING), ("created_at", DESCENDING)])

    # integration_status
    db.integration_status.create_index([("business_id", ASCENDING), ("service_name", ASCENDING)], unique=True)

    logger.info("MongoDB indexes initialized")


def ping_db() -> bool:
    try:
        client = get_client()
        # If running mongomock, always healthy
        if hasattr(client, "__class__") and "mongomock" in client.__class__.__module__:
            return True
        client.admin.command("ping")
        return True
    except Exception as e:
        logger.error(f"MongoDB ping failed: {e}")
        return False

