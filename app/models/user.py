from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.database.connection import Base


class User(Base):

    __tablename__ = "users"


    user_id = Column(
        Integer,
        primary_key=True,
        index=True
    )


    username = Column(
        String,
        unique=True,
        nullable=False
    )


    email = Column(
        String,
        unique=True,
        nullable=False
    )


    password = Column(
        String,
        nullable=False
    )


    role = Column(
        String,
        default="User",
        nullable=False
    )

    audit_logs = relationship(
    "AuditLog",
    back_populates="user"
)