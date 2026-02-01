from datetime import date as date_type, datetime, time, timedelta

from fastapi import APIRouter, Depends
from sqlalchemy import case
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.api.utils import session_to_out
from app.db.session import get_db
from app.models.enums import SessionStatus, UserRole
from app.models.session import Session as SessionModel
from app.schemas.session import SessionOut

router = APIRouter(tags=["calendar"])


@router.get("/calendar/day", response_model=list[SessionOut])
def calendar_day(
    date: date_type,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
) -> list[SessionOut]:
    start = datetime.combine(date, time.min)
    end = start + timedelta(days=1)

    status_order = case(
        (SessionModel.status == SessionStatus.arrived, 1),
        (SessionModel.status == SessionStatus.planned, 2),
        (SessionModel.status == SessionStatus.completed, 3),
        (SessionModel.status == SessionStatus.canceled, 4),
        else_=5,
    )

    query = db.query(SessionModel).filter(SessionModel.start_at >= start, SessionModel.start_at < end)
    if user.role != UserRole.owner:
        query = query.filter(SessionModel.location_id == user.location_id)

    sessions = query.order_by(SessionModel.start_at.asc(), status_order.asc(), SessionModel.id.asc()).all()
    return [session_to_out(item) for item in sessions]
