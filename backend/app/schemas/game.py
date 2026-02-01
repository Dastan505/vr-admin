from pydantic import BaseModel, ConfigDict


class GameOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    mode_icon: str | None
    is_active: bool


class GameCreate(BaseModel):
    name: str
    mode_icon: str | None = None


class GameUpdate(BaseModel):
    name: str | None = None
    mode_icon: str | None = None
    is_active: bool | None = None
