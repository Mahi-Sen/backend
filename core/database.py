from motor.motor_asyncio import AsyncIOMotorClient
from .config import MONGO_URI, DATABASE_NAME

client = AsyncIOMotorClient(MONGO_URI)
database = client[DATABASE_NAME]
user_collection = database.get_collection("users")

def user_helper(user) -> dict:
    return {
        "id": str(user["_id"]),
        "username": user["username"],
        "access_key": user["access_key"],
        "is_active": user["is_active"],
        "api_calls_total": user["api_calls_total"],
        "api_call_limit": user.get("api_call_limit"),
        "created_at": user["created_at"],
        "expires_on": user.get("expires_on"),
        "txl_config": user.get("txl_config"),
        "ixl_config": user.get("ixl_config"),
    }