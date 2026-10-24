from sqlalchemy import Column, Integer, String, Text, ForeignKey
from app.database.connection import Base


class Assessment(Base):

    __tablename__ = "assessments"

    assessment_id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    organization_id = Column(
        Integer,
        ForeignKey("organizations.organization_id"),
        nullable=False
    )

    control_id = Column(
        Integer,
        ForeignKey("controls.control_id"),
        nullable=False
    )

    status = Column(
        String,
        nullable=False
    )

    score = Column(
        Integer,
        nullable=False
    )

    evidence = Column(
        Text,
        nullable=True
    )