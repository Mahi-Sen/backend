# api/admin.py (FINAL, FULLY CORRECTED VERSION)

from fastapi import APIRouter, Depends, HTTPException, status, Body
from typing import List, Optional
from pydantic import BaseModel
from bson import ObjectId  # <-- IMPORTANT: Import ObjectId

from models.user import User, UserUpdate
from core.database import user_collection, user_helper
from core.security import generate_access_key, get_admin_user
from core.config_manager import get_system_config, update_system_config, SystemConfig

# This is a Pydantic model for the request body when updating system config
class SystemConfigUpdate(BaseModel):
    api_enabled: Optional[bool] = None
    daily_lockdown_start_utc: Optional[str] = None
    daily_lockdown_end_utc: Optional[str] = None
    maintenance_message: Optional[str] = None

# This is a Pydantic model for the request body for notifications
class NotificationRequest(BaseModel):
    message: str

router = APIRouter()

@router.get("/admin/users", response_model=List[dict], dependencies=[Depends(get_admin_user)])
async def get_all_users():
    """Get a list of all users for the admin panel."""
    users = []
    async for user in user_collection.find():
        users.append(user_helper(user))
    return users

@router.post("/admin/users", response_model=dict, status_code=status.HTTP_201_CREATED, dependencies=[Depends(get_admin_user)])
async def create_user(user_data: User = Body(...)):
    """Create a new user."""
    # Check if a user with this username already exists
    if await user_collection.find_one({"username": user_data.username}):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"User with username '{user_data.username}' already exists."
        )
        
    user_data.access_key = generate_access_key()
    
    # We dump the model to a dict, but we exclude 'id' because MongoDB generates it.
    user_dict = user_data.model_dump(by_alias=True, exclude=["id"])

    new_user = await user_collection.insert_one(user_dict)
    created_user = await user_collection.find_one({"_id": new_user.inserted_id})
    
    return user_helper(created_user)

@router.put("/admin/users/{user_id}", response_model=dict, dependencies=[Depends(get_admin_user)])
async def update_user(user_id: str, update_data: UserUpdate = Body(...)):
    """Update a user's details."""
    if not ObjectId.is_valid(user_id):
        raise HTTPException(status_code=400, detail="Invalid user ID format.")

    update_dict = {k: v for k, v in update_data.model_dump(by_alias=True).items() if v is not None}
    
    if not update_dict:
        raise HTTPException(status_code=400, detail="No update data provided.")

    await user_collection.update_one({"_id": ObjectId(user_id)}, {"$set": update_dict})
    
    updated_user = await user_collection.find_one({"_id": ObjectId(user_id)})
    if updated_user:
        return user_helper(updated_user)
        
    raise HTTPException(status_code=404, detail=f"User with id {user_id} not found.")

@router.delete("/admin/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(get_admin_user)])
async def delete_user(user_id: str):
    """Delete a user."""
    if not ObjectId.is_valid(user_id):
        raise HTTPException(status_code=400, detail="Invalid user ID format.")
        
    delete_result = await user_collection.delete_one({"_id": ObjectId(user_id)})
    
    if delete_result.deleted_count == 0:
        raise HTTPException(status_code=404, detail=f"User with id {user_id} not found.")
    return

@router.post("/admin/users/{user_id}/notify", status_code=status.HTTP_202_ACCEPTED, dependencies=[Depends(get_admin_user)])
async def send_notification_to_user(user_id: str, request: NotificationRequest = Body(...)):
    """Sets a pending notification message for a specific user."""
    if not ObjectId.is_valid(user_id):
        raise HTTPException(status_code=400, detail="Invalid user ID format.")
        
    update_result = await user_collection.update_one(
        {"_id": ObjectId(user_id)}, 
        {"$set": {"pending_notification": request.message}}
    )
    
    if update_result.matched_count == 0:
        raise HTTPException(status_code=404, detail=f"User with id {user_id} not found.")
        
    return {"detail": "Notification queued for user."}

@router.post("/admin/users/{user_id}/uninstall", status_code=status.HTTP_202_ACCEPTED, dependencies=[Depends(get_admin_user)])
async def trigger_remote_uninstall(user_id: str):
    """Flags a user's application for remote uninstallation on next launch."""
    if not ObjectId.is_valid(user_id):
        raise HTTPException(status_code=400, detail="Invalid user ID format.")
        
    update_result = await user_collection.update_one(
        {"_id": ObjectId(user_id)}, 
        {"$set": {"uninstall_pending": True}}
    )
    
    if update_result.matched_count == 0:
        raise HTTPException(status_code=404, detail=f"User with id {user_id} not found.")
        
    return {"detail": "Application has been flagged for uninstallation."}

@router.get("/admin/system-config", response_model=SystemConfig, dependencies=[Depends(get_admin_user)])
async def get_current_system_config():
    """Retrieves the current global system configuration."""
    return await get_system_config()

@router.put("/admin/system-config", status_code=status.HTTP_202_ACCEPTED, dependencies=[Depends(get_admin_user)])
async def update_current_system_config(config_update: SystemConfigUpdate = Body(...)):
    """Updates the global system configuration."""
    update_data = config_update.model_dump(exclude_unset=True)
    
    if not update_data:
        raise HTTPException(status_code=400, detail="No configuration data provided.")
        
    await update_system_config(update_data)
    
    return {"detail": "System configuration updated successfully."}
