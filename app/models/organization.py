from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from app.database.connection import Base


class Organization(Base):

    __tablename__ = "organizations"


    organization_id = Column(
        Integer,
        primary_key=True,
        index=True
    )


    name = Column(
        String,
        nullable=False
    )


    industry = Column(
        String,
        nullable=False
    )


    size = Column(
        String,
        nullable=False
    )


    frameworks = relationship(
        "Framework",
        back_populates="organization"
    )


    risks = relationship(
        "Risk",
        back_populates="organization"
    )