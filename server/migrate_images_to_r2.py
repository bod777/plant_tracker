"""
One-time migration: upload image_data from MongoDB documents to R2,
replace image_data with image_urls, remove image_data field.

Run from the server/ directory:
    python migrate_images_to_r2.py

Requires .env with R2_* and MONGODB_* variables set.
"""

import asyncio
import os
import sys
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

from pymongo import MongoClient
from pymongo.server_api import ServerApi
from app.storage import upload_base64_image

MONGODB_URI = os.getenv("MONGODB_URI")
DB_NAME = os.getenv("MONGODB_DB_NAME", "plant_tracker")


def migrate():
    client = MongoClient(MONGODB_URI, server_api=ServerApi("1"))
    db = client[DB_NAME]
    plants = db["plants"]

    query = {"image_data": {"$exists": True, "$not": {"$size": 0}}, "image_urls": {"$exists": False}}
    total = plants.count_documents(query)
    print(f"Found {total} documents to migrate.")

    if total == 0:
        print("Nothing to do.")
        return

    migrated = 0
    failed = 0

    for doc in plants.find(query, {"_id": 1, "image_data": 1}):
        doc_id = doc["_id"]
        image_data = doc.get("image_data") or []
        try:
            urls = [upload_base64_image(img) for img in image_data]
            plants.update_one(
                {"_id": doc_id},
                {
                    "$set": {"image_urls": urls},
                    "$unset": {"image_data": ""},
                }
            )
            migrated += 1
            print(f"  [{migrated}/{total}] Migrated {doc_id} → {len(urls)} image(s)")
        except Exception as e:
            failed += 1
            print(f"  FAILED {doc_id}: {e}", file=sys.stderr)

    print(f"\nDone. {migrated} migrated, {failed} failed.")
    client.close()


if __name__ == "__main__":
    migrate()
