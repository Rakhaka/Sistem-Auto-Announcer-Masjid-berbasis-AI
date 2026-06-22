from pydantic import BaseModel, Field
from typing import Optional

class LoginRequest(BaseModel):
    username: str
    password: str

class TokenResponse(BaseModel):
    token: str
    token_type: str = "bearer"

class AnnounceRequest(BaseModel):
    message: Optional[str] = None
    audio_id: Optional[int] = None
    zone: str = "masjid-1"
    priority: str = "normal"

class AnnounceResponse(BaseModel):
    success: bool
    message: str
    jobId: Optional[str] = None

class StopResponse(BaseModel):
    success: bool
    message: str

class HealthResponse(BaseModel):
    status: str
    version: str = "2.0.0"

class StatusResponse(BaseModel):
    online: bool
    playing: bool
    mixer_on: bool
    volume: int
    platform: str
    gpio_available: bool

class PlayMurottalRequest(BaseModel):
    url_audio: str

class SetVolumeRequest(BaseModel):
    volume: int = Field(ge=0, le=100)

class ScheduleCreate(BaseModel):
    nama_jadwal: str
    waktu_putar: str
    audio_id: int

class ScheduleUpdate(BaseModel):
    nama_jadwal: Optional[str] = None
    waktu_putar: Optional[str] = None

class ProsesSuaraRequest(BaseModel):
    nama_audio: str = "Pengumuman"
    teks: str

class UploadResponse(BaseModel):
    success: bool
    filename: Optional[str] = None
    message: str
