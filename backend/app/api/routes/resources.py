from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.enums import UserRole
from app.models.resource import Resource
from app.schemas.resource import ResourceOut

router = APIRouter(prefix="/resources", tags=["resources"])


@router.get("", response_model=list[ResourceOut])
def list_resources(db: Session = Depends(get_db), user=Depends(get_current_user)) -> list[ResourceOut]:
    query = db.query(Resource)
    if user.role != UserRole.owner:
        query = query.filter(Resource.location_id == user.location_id)
    return query.order_by(Resource.id.asc()).all()
