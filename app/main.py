from datetime import date
from app.enums import HabitFrequency, HabitStatus
from app.db_models import HabitRecord
from app.database import engine
from sqlalchemy.orm import Session
from sqlalchemy import select


if __name__ == "__main__":
    record = HabitRecord(name="Habit", description="habit", created_at=(date.today()), weekday=None, status=HabitStatus.ACTIVE, frequency=HabitFrequency.EVERYDAY)
    # with Session(engine) as session:
    #     session.add(record)
    #     session.commit()

    with Session(engine) as session:
        stmt = select(HabitRecord).where(HabitRecord.name == "Habit")
        records = session.scalars(stmt).all()
        for record in records:
            print(record.id, record.name, record.status)