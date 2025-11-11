# core/database.py (FINAL, CORRECTED VERSION)
from motor.motor_asyncio import AsyncIOMotorClient
from .config import MONGO_URI, DATABASE_NAME
from bson import ObjectId # Import this

client = AsyncIOMotorClient(MONGO_URI)
database = client[DATABASE_NAME]
user_collection = database.get_collection("users")

# This helper is now simpler or you can remove it if you always use the model
def user_helper(user) -> dict:
    user['id'] = str(user['_id'])
    del user['_id']
    return user
