from sqlalchemy.orm import Session

from app.models.audit_log import AuditLog


def log_action(
    db: Session,
    user_id: int,
    entity_type: str,
    entity_id: int,
    action: str,
    changes: dict,
) -> None:
    audit = AuditLog(
        user_id=user_id,
        entity_type=entity_type,
        entity_id=entity_id,
        action=action,
        changes=changes or {},
    )
    db.add(audit)
