from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.database.connection import Base


class AuditLog(Base):

    __tablename__ = "audit_logs"


    id = Column(
        Integer,
        primary_key=True,
        index=True
    )


    user_id = Column(
        Integer,
        ForeignKey("users.user_id"),
        nullable=False
    )


    action = Column(
        String,
        nullable=False
    )


    entity = Column(
        String,
        nullable=False
    )


    description = Column(
        Text,
        nullable=True
    )


    timestamp = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )


    user = relationship(
        "User",
        back_populates="audit_logs"
    )