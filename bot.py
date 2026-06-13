from motor.motor_asyncio import AsyncIOMotorClient
import os

mongo = AsyncIOMotorClient(
    os.getenv("MONGO_URI")
)

db = mongo["file_store_bot"]

print("MongoDB Connected")
