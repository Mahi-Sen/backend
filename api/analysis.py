from fastapi import APIRouter, Body, HTTPException, status, Request, Depends
from pydantic import BaseModel
from datetime import datetime
import secrets
import json

from .dependencies import check_api_status
from core.database import user_collection
from services.llm_service import get_image_description_from_ixl, get_final_answer_from_txl
from models.user import LLMConfig

router = APIRouter()

class AnalysisRequest(BaseModel):
    access_key: str
    device_key: str
    image_data: str

class SecureRequest(BaseModel):
    access_key: str
    device_key: str

class ActivationRequest(BaseModel):
    access_key: str

@router.post("/auth/activate")
async def activate_device(payload: ActivationRequest):
    access_key = payload.access_key
    user = await user_collection.find_one({"access_key": access_key})
    if not user or not user.get("is_active"):
        raise HTTPException(status_code=403, detail="Invalid or inactive access key.")
    new_device_key = f"bkm_dev_{secrets.token_urlsafe(32)}"
    await user_collection.update_one({"_id": user["_id"]}, {"$set": {"device_key": new_device_key}})
    print(f"Generated and saved new device key for user {user.get('username', 'unknown')}.")
    return {"device_key": new_device_key}

@router.post("/analyze", dependencies=[Depends(check_api_status)])
async def analyze_screen(request: AnalysisRequest):
    user = await user_collection.find_one({"access_key": request.access_key})
    if not user or not user.get("is_active") or user.get("device_key") != request.device_key:
        raise HTTPException(status_code=403, detail="Invalid credentials or device key mismatch.")
    
    if user.get("expires_on") and user["expires_on"] < datetime.utcnow():
        raise HTTPException(status_code=403, detail="Your Access Key has expired.")
        
    if user.get("api_call_limit") is not None and user.get("api_calls_total", 0) >= user["api_call_limit"]:
        raise HTTPException(status_code=429, detail="API call limit reached for this key.")

    try:
        try:
            ixl_config = LLMConfig(**user.get("ixl_config", {}))
            txl_config = LLMConfig(**user.get("txl_config", {}))
            image_description = await get_image_description_from_ixl(request.image_data, ixl_config)
            final_answer = await get_final_answer_from_txl(image_description, txl_config)
        except Exception as llm_error:
            print(f"External LLM API Error: {llm_error}")
            raise HTTPException(status_code=503, detail="I'm stuck in a glitch... The external AI service may be down. Please try again in a moment.")

        await user_collection.update_one({"_id": user["_id"]}, {"$inc": {"api_calls_total": 1}})
        return {"result": final_answer}
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        print(f"Unexpected internal server error during analysis: {e}")
        raise HTTPException(status_code=500, detail="An unexpected internal server error occurred.")

@router.post("/auth/validate")
async def validate_key(request: Request):
    try:
        body = await request.json()
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON body.")
    access_key = body.get("access_key")
    if not access_key:
        return {"is_valid": False}
    user = await user_collection.find_one({"access_key": access_key})
    if not user or not user.get("is_active"):
        return {"is_valid": False}
    return {"is_valid": True}

@router.post("/client/check-notifications", dependencies=[Depends(check_api_status)])
async def check_notifications(request: SecureRequest):
    user = await user_collection.find_one(
        {"access_key": request.access_key, "device_key": request.device_key},
        {"pending_notification": 1}
    )
    if not user or not user.get("pending_notification"):
        return {"message": None}
    message = user["pending_notification"]
    await user_collection.update_one({"_id": user["_id"]}, {"$set": {"pending_notification": None}})
    return {"message": message}

@router.post("/client/check-status", dependencies=[Depends(check_api_status)])
async def check_client_status(request: SecureRequest):
    user = await user_collection.find_one(
        {"access_key": request.access_key, "device_key": request.device_key},
        {"is_active": 1, "uninstall_pending": 1}
    )
    if not user:
        return {"action": "ok"}
    if user.get("uninstall_pending"):
        return {"action": "uninstall"}
    if not user.get("is_active"):
        return {"action": "block"}
    return {"action": "ok"}