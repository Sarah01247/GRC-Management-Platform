from app.models.audit_log import AuditLog


def create_audit_log(
    db,
    user_id,
    action,
    entity,
    description=None
):

    log = AuditLog(
        user_id=user_id,
        action=action,
        entity=entity,
        description=description
    )

    db.add(log)
    db.commit()
    db.refresh(log)

    return log