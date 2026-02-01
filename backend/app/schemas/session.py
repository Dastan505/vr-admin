from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import SessionStatus


class SessionBase(BaseModel):
    resource_id: int
    game_id: int
    start_at: datetime
    duration_min: int = Field(gt=0)
    players: int | None = Field(default=None, ge=1)
    status: SessionStatus = SessionStatus.planned
    contact_name: str | None = None
    contact_phone: str | None = None
    comment: str | None = None


class SessionCreate(SessionBase):
    pass


class SessionUpdate(BaseModel):
    resource_id: int | None = None
    game_id: int | None = None
    start_at: datetime | None = None
    duration_min: int | None = Field(default=None, gt=0)
    players: int | None = Field(default=None, ge=1)
    status: SessionStatus | None = None
    contact_name: str | None = None
    contact_phone: str | None = None
    comment: str | None = None


class SessionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    location_id: int
    resource_id: int
    resource_name: str
    game_id: int
    game_name: str
    game_icon: str | None
    start_at: datetime
    end_at: datetime
    duration_min: int
    status: SessionStatus
    players: int | None
    contact_name: str | None
    contact_phone: str | None
    comment: str | None
    canceled_reason: str | None
    created_at: datetime
    updated_at: datetime | None


class CancelRequest(BaseModel):
    reason: str = Field(min_length=2)


class DeleteRequest(BaseModel):
    reason: str = Field(min_length=2)
