from sqlalchemy import Column, Integer, String, Text, ForeignKey
from app.database.connection import Base
from sqlalchemy.orm import relationship


class Control(Base):

    __tablename__ = "controls"

    control_id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    framework_id = Column(
        Integer,
        ForeignKey("frameworks.framework_id"),
        nullable=False
    )

    control_code = Column(
        String,
        nullable=False
    )

    title = Column(
        String,
        nullable=False
    )

    description = Column(
        Text,
        nullable=True
    )

    category = Column(
        String,
        nullable=True
    )
    framework = relationship(
    "Framework",
    back_populates="controls"
    )

    assessments = relationship(
        "ControlAssessment",
        back_populates="control"
    )


    evidences = relationship(
        "Evidence",
        back_populates="control"
    )