"""
MAUSAM — Seed Data to MongoDB (Local or MongoDB Atlas)
Usage:
  # Uses MONGODB_URI from backend/.env:
  python scripts/seed_to_mongo.py

  # Or pass custom MongoDB Atlas URI:
  python scripts/seed_to_mongo.py --uri "mongodb+srv://<user>:<password>@cluster0.xyz.mongodb.net" --db mausam_dev
"""
import sys
import os
import json
import argparse
from pathlib import Path
from pymongo import MongoClient

# Ensure app is importable
backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

from app.core.config import settings
from app.core.database import init_indexes


def seed_database(mongo_uri: str, db_name: str, json_file: Path):
    print(f"Connecting to MongoDB at: {mongo_uri.split('@')[-1] if '@' in mongo_uri else mongo_uri} ...")
    try:
        client = MongoClient(mongo_uri, serverSelectionTimeoutMS=5000)
        client.admin.command("ping")
        print("Connected successfully to MongoDB!")
    except Exception as e:
        print(f"\n❌ Error connecting to MongoDB: {e}")
        print("\nTip for MongoDB Atlas:")
        print("  1. Ensure your IP address is whitelisted in Atlas (Network Access -> Add IP Address -> Allow Access from Anywhere: 0.0.0.0/0)")
        print("  2. Ensure your username and password in the connection string are correct.")
        sys.exit(1)

    db = client[db_name]
    print(f"Target Database: '{db_name}'")

    if not json_file.exists():
        print(f"File {json_file} not found. Generating fresh synthetic dataset...")
        from scripts.generate_demo_data import generate_dataset
        data = generate_dataset()
        with open(json_file, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2, default=str)
    else:
        print(f"Loading data from {json_file.name} ...")
        with open(json_file, "r", encoding="utf-8") as f:
            data = json.load(f)

    business_id = data.get("business", {}).get("business_id", "demo_ramesh_textiles")

    # 1. Business
    if "business" in data:
        db.businesses.update_one({"business_id": business_id}, {"$set": data["business"]}, upsert=True)
        print("  - Saved business profile")

    # 2. Customers
    custs = data.get("customers", [])
    if custs:
        for c in custs:
            db.customers.update_one({"business_id": business_id, "customer_id": c["customer_id"]}, {"$set": {**c, "business_id": business_id}}, upsert=True)
        print(f"  - Saved {len(custs)} customers")

    # 3. Suppliers
    supps = data.get("suppliers", [])
    if supps:
        for s in supps:
            db.suppliers.update_one({"business_id": business_id, "supplier_id": s["supplier_id"]}, {"$set": {**s, "business_id": business_id}}, upsert=True)
        print(f"  - Saved {len(supps)} suppliers")

    # 4. Obligations
    obls = data.get("obligations", [])
    if obls:
        for o in obls:
            db.obligations.update_one({"business_id": business_id, "obligation_id": o["obligation_id"]}, {"$set": {**o, "business_id": business_id}}, upsert=True)
        print(f"  - Saved {len(obls)} obligations")

    # 5. Invoices
    invs = data.get("invoices", [])
    if invs:
        for inv in invs:
            db.invoices.update_one({"business_id": business_id, "invoice_id": inv["invoice_id"]}, {"$set": inv}, upsert=True)
        print(f"  - Saved {len(invs)} invoices")

    # 6. Bank transactions
    txns = data.get("bank_transactions", [])
    if txns:
        for txn in txns:
            db.bank_transactions.update_one({"business_id": business_id, "txn_id": txn["txn_id"]}, {"$set": txn}, upsert=True)
        print(f"  - Saved {len(txns)} bank transactions")

    # 7. GST Summaries
    gsts = data.get("gst_summaries", [])
    if gsts:
        for gst in gsts:
            db.gst_summaries.update_one({"business_id": business_id, "period_key": gst["period_key"]}, {"$set": gst}, upsert=True)
        print(f"  - Saved {len(gsts)} GST monthly summaries")

    # 8. Payment Histories
    phs = data.get("payment_histories", [])
    if phs:
        for ph in phs:
            db.payment_histories.update_one({"business_id": business_id, "invoice_id": ph["invoice_id"]}, {"$set": ph}, upsert=True)
        print(f"  - Saved {len(phs)} payment history records")

    # 9. Payment Predictions
    preds = data.get("payment_predictions", [])
    if preds:
        for pred in preds:
            db.payment_predictions.update_one({"business_id": business_id, "invoice_id": pred["invoice_id"]}, {"$set": pred}, upsert=True)
        print(f"  - Saved {len(preds)} payment prediction records")

    print("\nInitializing database indexes...")
    init_indexes()
    print("All collections and indexes uploaded successfully to MongoDB!")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Upload MAUSAM data to MongoDB / MongoDB Atlas")
    parser.add_argument("--uri", default=settings.MONGODB_URI, help="MongoDB connection URI")
    parser.add_argument("--db", default=settings.MONGODB_DB_NAME, help="Database name")
    parser.add_argument("--file", default=Path(__file__).parent / "demo_data.json", help="Path to demo_data.json")

    args = parser.parse_args()
    seed_database(args.uri, args.db, Path(args.file))
