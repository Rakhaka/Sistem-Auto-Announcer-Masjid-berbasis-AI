from fastapi import APIRouter, Depends
from app.models.schemas import StatusResponse
from app.auth import get_current_user
from app.audio_player import is_playing, is_mixer_on, get_volume

router = APIRouter()
tags = ["Status"]

@router.get("/status", response_model=StatusResponse)
async def system_status(_=Depends(get_current_user)):
    try:
        import OPi.GPIO as GPIO
        gpio = True
    except ImportError:
        gpio = False
    return StatusResponse(
        online=True,
        playing=is_playing(),
        mixer_on=is_mixer_on(),
        volume=get_volume() or 0,
        platform="Orange Pi",
        gpio_available=gpio,
    )
