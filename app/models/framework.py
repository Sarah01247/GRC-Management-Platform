from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship

from app.database.connection import Base


class Framework(Base):

    __tablename__ = "frameworks"


    framework_id = Column(
        Integer,
        primary_key=True,
        index=True
    )


    organization_id = Column(
        Integer,
        ForeignKey("organizations.organization_id"),
        nullable=False
    )


    name = Column(
        String,
        nullable=False
    )


    version = Column(
        String,
        nullable=True
    )


    description = Column(
        Text,
        nullable=True
    )


    organization = relationship(
        "Organization",
        back_populates="frameworks"
    )


    controls = relationship(
        "Control",
        back_populates="framework"
    )