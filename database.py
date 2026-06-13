from motor.motor_asyncio import AsyncIOMotorClient
import os

client = AsyncIOMotorClient(os.getenv("MONGO_URI"))

db = client["file_store_bot"]

files = db["files"]
batches = db["batches"]
