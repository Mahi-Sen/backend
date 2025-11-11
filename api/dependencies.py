from fastapi import HTTPException, status
from core.config_manager import get_system_config
from datetime import datetime, time
import pytz

async def check_api_status():
    """
    A FastAPI dependency that checks if the API is globally enabled,
    both manually and via a recurring daily schedule.
    """
    config = await get_system_config()
    
    if not config.api_enabled:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=config.maintenance_message or "The service is temporarily disabled by an administrator."
        )
        
    if config.daily_lockdown_start_utc and config.daily_lockdown_end_utc:
        try:
            now_utc_time = datetime.now(pytz.utc).time()

            start_time = time.fromisoformat(config.daily_lockdown_start_utc)
            end_time = time.fromisoformat(config.daily_lockdown_end_utc)

            is_locked = False
            if start_time <= end_time:
                if start_time <= now_utc_time <= end_time:
                    is_locked = True
            else: 
                if now_utc_time >= start_time or now_utc_time <= end_time:
                    is_locked = True
            
            if is_locked:
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail=config.maintenance_message or "The service is currently in a scheduled maintenance window."
                )
        except (ValueError, TypeError):
            print("Warning: Invalid daily lockdown time format in database. Skipping schedule check.")
    
    return True