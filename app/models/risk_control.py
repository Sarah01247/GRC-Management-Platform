from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship

from app.database.connection import Base


class RiskControl(Base):

    __tablename__ = "risk_controls"


    id = Column(
        Integer,
        primary_key=True,
        index=True
    )


    risk_id = Column(
        Integer,
        ForeignKey("risks.risk_id")
    )


    control_id = Column(
        Integer,
        ForeignKey("controls.control_id")
    )


    risk = relationship(
        "Risk",
        back_populates="controls"
    )