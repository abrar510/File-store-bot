from motor.motor_asyncio import AsyncIOMotorClient
import os

client = AsyncIOMotorClient(
    os.getenv("MONGO_URI")
)

db = client["file_store_bot"]

files_col = db["files"]
batches_col = db["batches"]


# ==========================
# SINGLE FILE
# ==========================

async def save_file(file_id, message_id):

    await files_col.update_one(
        {"file_id": file_id},
        {
            "$set": {
                "message_id": message_id
            }
        },
        upsert=True
    )


async def get_file(file_id):

    return await files_col.find_one(
        {"file_id": file_id}
    )


# ==========================
# BATCH
# ==========================

async def save_batch(batch_id, message_ids):

    await batches_col.update_one(
        {"batch_id": batch_id},
        {
            "$set": {
                "message_ids": message_ids
            }
        },
        upsert=True
    )


async def get_batch(batch_id):

    return await batches_col.find_one(
        {"batch_id": batch_id}
    )
