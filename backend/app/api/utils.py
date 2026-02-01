from app.models.session import Session as SessionModel
from app.schemas.session import SessionOut


def session_to_out(session: SessionModel) -> SessionOut:
    return SessionOut(
        id=session.id,
        location_id=session.location_id,
        resource_id=session.resource_id,
        resource_name=session.resource.name if session.resource else "",
        game_id=session.game_id,
        game_name=session.game.name if session.game else "",
        game_icon=session.game.mode_icon if session.game else None,
        start_at=session.start_at,
        end_at=session.end_at,
        duration_min=session.duration_min,
        status=session.status,
        players=session.players,
        contact_name=session.contact_name,
        contact_phone=session.contact_phone,
        comment=session.comment,
        canceled_reason=session.canceled_reason,
        created_at=session.created_at,
        updated_at=session.updated_at,
    )
