from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, require_owner
from app.api.utils import session_to_out
from app.db.session import get_db
from app.models.enums import UserRole
from app.models.session import Session as SessionModel
from app.schemas.session import CancelRequest, DeleteRequest, SessionCreate, SessionOut, SessionUpdate
from app.services.sessions import (
    cancel_session,
    complete_session,
    create_session,
    delete_session,
    ensure_session_access,
    update_session,
)

router = APIRouter(prefix="/sessions", tags=["sessions"])


@router.post("", response_model=SessionOut, status_code=status.HTTP_201_CREATED)
def create(payload: SessionCreate, db: Session = Depends(get_db), user=Depends(get_current_user)) -> SessionOut:
    session = create_session(db, user, payload)
    return session_to_out(session)


@router.get("/{session_id}", response_model=SessionOut)
def get_one(session_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)) -> SessionOut:
    session = ensure_session_access(db, user, session_id)
    return session_to_out(session)


@router.put("/{session_id}", response_model=SessionOut)
def update(
    session_id: int,
    payload: SessionUpdate,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
) -> SessionOut:
    session = update_session(db, user, session_id, payload)
    return session_to_out(session)


@router.post("/{session_id}/cancel", response_model=SessionOut)
def cancel(
    session_id: int,
    payload: CancelRequest,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
) -> SessionOut:
    session = cancel_session(db, user, session_id, payload.reason)
    return session_to_out(session)


@router.post("/{session_id}/complete", response_model=SessionOut)
def complete(session_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)) -> SessionOut:
    session = complete_session(db, user, session_id)
    return session_to_out(session)


@router.delete("/{session_id}")
def delete(
    session_id: int,
    payload: DeleteRequest,
    db: Session = Depends(get_db),
    user=Depends(require_owner),
) -> dict:
    delete_session(db, user, session_id, payload.reason)
    return {"status": "deleted"}
