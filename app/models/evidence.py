from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from datetime import datetime

from sqlalchemy.orm import relationship

from app.database.connection import Base


class Evidence(Base):

    __tablename__ = "evidences"

    evidence_id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    control_id = Column(
        Integer,
        ForeignKey("controls.control_id"),
        nullable=False
    )

    file_name = Column(
        String,
        nullable=False
    )

    file_path = Column(
        String,
        nullable=False
    )

    uploaded_by = Column(
        String,
        nullable=False
    )

    uploaded_at = Column(
        DateTime,
        default=datetime.utcnow
    )


    control = relationship(
        "Control",
        back_populates="evidences"
    )