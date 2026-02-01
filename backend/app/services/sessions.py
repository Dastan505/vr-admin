from __future__ import annotations

from datetime import datetime, timedelta

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.enums import SessionStatus, UserRole
from app.models.game import Game
from app.models.resource import Resource
from app.models.session import Session as SessionModel
from app.services.audit import log_action


def compute_end_at(start_at: datetime, duration_min: int) -> datetime:
    return start_at + timedelta(minutes=duration_min)


def ensure_resource_access(db: Session, user, resource_id: int) -> Resource:
    resource = db.query(Resource).filter(Resource.id == resource_id).first()
    if not resource:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resource not found")
    if user.role != UserRole.owner and resource.location_id != user.location_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Location access denied")
    return resource


def ensure_session_access(db: Session, user, session_id: int) -> SessionModel:
    query = db.query(SessionModel).filter(SessionModel.id == session_id)
    if user.role != UserRole.owner:
        query = query.filter(SessionModel.location_id == user.location_id)
    session = query.first()
    if not session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")
    return session


def check_overlap(
    db: Session,
    resource_id: int,
    start_at: datetime,
    end_at: datetime,
    ignore_session_id: int | None = None,
) -> None:
    query = db.query(SessionModel).filter(
        SessionModel.resource_id == resource_id,
        SessionModel.status != SessionStatus.canceled,
        SessionModel.start_at < end_at,
        SessionModel.end_at > start_at,
    )
    if ignore_session_id:
        query = query.filter(SessionModel.id != ignore_session_id)
    exists = db.query(query.exists()).scalar()
    if exists:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Time overlap for resource")


def create_session(db: Session, user, payload) -> SessionModel:
    resource = ensure_resource_access(db, user, payload.resource_id)
    game = db.query(Game).filter(Game.id == payload.game_id, Game.is_active.is_(True)).first()
    if not game:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Game not found")
    end_at = compute_end_at(payload.start_at, payload.duration_min)
    check_overlap(db, resource.id, payload.start_at, end_at)

    session = SessionModel(
        location_id=resource.location_id,
        resource_id=resource.id,
        game_id=payload.game_id,
        start_at=payload.start_at,
        end_at=end_at,
        duration_min=payload.duration_min,
        status=payload.status,
        players=payload.players,
        contact_name=payload.contact_name,
        contact_phone=payload.contact_phone,
        comment=payload.comment,
        created_by_id=user.id,
        updated_by_id=user.id,
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    return session


def update_session(db: Session, user, session_id: int, payload) -> SessionModel:
    session = ensure_session_access(db, user, session_id)

    new_resource_id = payload.resource_id or session.resource_id
    resource = ensure_resource_access(db, user, new_resource_id)
    if payload.game_id:
        game = db.query(Game).filter(Game.id == payload.game_id, Game.is_active.is_(True)).first()
        if not game:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Game not found")

    new_start = payload.start_at or session.start_at
    new_duration = payload.duration_min or session.duration_min
    new_end = compute_end_at(new_start, new_duration)

    if payload.resource_id or payload.start_at or payload.duration_min:
        check_overlap(db, new_resource_id, new_start, new_end, ignore_session_id=session.id)

    changes: dict = {}
    if payload.resource_id and payload.resource_id != session.resource_id:
        changes["resource_id"] = {"from": session.resource_id, "to": payload.resource_id}
        session.resource_id = payload.resource_id
        session.location_id = resource.location_id
    if payload.game_id and payload.game_id != session.game_id:
        changes["game_id"] = {"from": session.game_id, "to": payload.game_id}
        session.game_id = payload.game_id
    if payload.start_at and payload.start_at != session.start_at:
        changes["start_at"] = {"from": session.start_at.isoformat(), "to": payload.start_at.isoformat()}
        session.start_at = payload.start_at
    if payload.duration_min and payload.duration_min != session.duration_min:
        changes["duration_min"] = {"from": session.duration_min, "to": payload.duration_min}
        session.duration_min = payload.duration_min
    if payload.status and payload.status != session.status:
        changes["status"] = {"from": session.status, "to": payload.status}
        session.status = payload.status
    if payload.players is not None and payload.players != session.players:
        changes["players"] = {"from": session.players, "to": payload.players}
        session.players = payload.players
    if payload.contact_name is not None and payload.contact_name != session.contact_name:
        changes["contact_name"] = {"from": session.contact_name, "to": payload.contact_name}
        session.contact_name = payload.contact_name
    if payload.contact_phone is not None and payload.contact_phone != session.contact_phone:
        changes["contact_phone"] = {"from": session.contact_phone, "to": payload.contact_phone}
        session.contact_phone = payload.contact_phone
    if payload.comment is not None and payload.comment != session.comment:
        changes["comment"] = {"from": session.comment, "to": payload.comment}
        session.comment = payload.comment

    session.end_at = new_end
    session.updated_by_id = user.id

    if changes:
        log_action(db, user.id, "session", session.id, "update", changes)

    db.commit()
    db.refresh(session)
    return session


def cancel_session(db: Session, user, session_id: int, reason: str) -> SessionModel:
    session = ensure_session_access(db, user, session_id)

    session.status = SessionStatus.canceled
    session.canceled_reason = reason
    session.canceled_at = datetime.now()
    session.updated_by_id = user.id

    log_action(db, user.id, "session", session.id, "cancel", {"reason": reason})

    db.commit()
    db.refresh(session)
    return session


def complete_session(db: Session, user, session_id: int) -> SessionModel:
    session = ensure_session_access(db, user, session_id)

    session.status = SessionStatus.completed
    session.completed_at = datetime.now()
    session.updated_by_id = user.id

    log_action(db, user.id, "session", session.id, "complete", {})

    db.commit()
    db.refresh(session)
    return session


def delete_session(db: Session, user, session_id: int, reason: str) -> None:
    session = ensure_session_access(db, user, session_id)

    log_action(db, user.id, "session", session.id, "delete", {"reason": reason})

    db.delete(session)
    db.commit()
