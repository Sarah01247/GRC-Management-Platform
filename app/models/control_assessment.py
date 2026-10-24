from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from app.database.connection import Base


class ControlAssessment(Base):

    __tablename__ = "control_assessments"


    assessment_id = Column(
        Integer,
        primary_key=True,
        index=True
    )


    control_id = Column(
        Integer,
        ForeignKey("controls.control_id")
    )


    status = Column(
        String
    )


    effectiveness = Column(
        String
    )


    evidence = Column(
        String,
        nullable=True
    )


    notes = Column(
        String,
        nullable=True
    )


    control = relationship(
        "Control",
        back_populates="assessments"
    )