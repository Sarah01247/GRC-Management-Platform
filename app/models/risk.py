from sqlalchemy import Column, Integer, String, Text, ForeignKey
from app.database.connection import Base
from sqlalchemy.orm import relationship
from sqlalchemy.orm import relationship
class Risk(Base):

    __tablename__ = "risks"

    risk_id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    organization_id = Column(
        Integer,
        ForeignKey("organizations.organization_id"),
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

    likelihood = Column(
        Integer,
        nullable=False
    )

    impact = Column(
        Integer,
        nullable=False
    )

    status = Column(
        String,
        nullable=False
    )

    mitigation = Column(
        Text,
        nullable=True
    )


    organization = relationship(
        "Organization",
        back_populates="risks"
    )


    controls = relationship(
        "RiskControl",
        back_populates="risk"
    )