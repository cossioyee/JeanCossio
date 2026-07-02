from datetime import datetime, time

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Time,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class Person(Base):
    __tablename__ = "persons"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    phone_number: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    sleep_start: Mapped[time | None] = mapped_column(Time, nullable=True)
    sleep_end: Mapped[time | None] = mapped_column(Time, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    tasks_assigned: Mapped[list["Task"]] = relationship(
        "Task", foreign_keys="Task.current_assignee_id", back_populates="current_assignee"
    )
    tasks_created: Mapped[list["Task"]] = relationship(
        "Task", foreign_keys="Task.created_by_id", back_populates="created_by"
    )
    completions: Mapped[list["TaskCompletion"]] = relationship(
        "TaskCompletion", back_populates="person"
    )


class Task(Base):
    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    frequency_days: Mapped[int] = mapped_column(Integer, nullable=False)
    current_assignee_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("persons.id"), nullable=True
    )
    created_by_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("persons.id"), nullable=True
    )
    next_due_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    current_assignee: Mapped["Person | None"] = relationship(
        "Person", foreign_keys=[current_assignee_id], back_populates="tasks_assigned"
    )
    created_by: Mapped["Person | None"] = relationship(
        "Person", foreign_keys=[created_by_id], back_populates="tasks_created"
    )
    completions: Mapped[list["TaskCompletion"]] = relationship(
        "TaskCompletion", back_populates="task"
    )


class TaskCompletion(Base):
    __tablename__ = "task_completions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    task_id: Mapped[int] = mapped_column(Integer, ForeignKey("tasks.id"), nullable=False)
    person_id: Mapped[int] = mapped_column(Integer, ForeignKey("persons.id"), nullable=False)
    completed_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)

    task: Mapped["Task"] = relationship("Task", back_populates="completions")
    person: Mapped["Person"] = relationship("Person", back_populates="completions")


class Setting(Base):
    __tablename__ = "settings"

    key: Mapped[str] = mapped_column(String(100), primary_key=True)
    value: Mapped[str] = mapped_column(String(255), nullable=False)
