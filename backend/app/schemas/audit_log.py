from datetime import datetime

from pydantic import BaseModel


class AuditLogOut(BaseModel):
    id: int
    user_id: int
    entity_type: str
    entity_id: int
    action: str
    changes: dict
    created_at: datetime
