from sqlalchemy import Enum as SQLEnum
from sqlalchemy import  Column, Integer, String, Date
from app.enums import HabitFrequency, HabitStatus
from app.database import Base


class HabitRecord(Base):
    __tablename__ = "habit"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    description = Column(String)
    created_at = Column(Date)
    weekday = Column(Integer, nullable=True)
    status = Column(SQLEnum(HabitStatus))
    frequency = Column(SQLEnum(HabitFrequency))