from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import Integer, VARCHAR, DateTime, ForeignKey, Boolean, Float
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.ext.asyncio import AsyncAttrs
from datetime import datetime

class Base(AsyncAttrs, DeclarativeBase):
    pass

class User(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    tg_id: Mapped[str] = mapped_column(VARCHAR(10), unique=True, nullable=False)
    fname: Mapped[str | None] = mapped_column(VARCHAR(100))
    lname: Mapped[str | None] = mapped_column(VARCHAR(100))
    username: Mapped[str | None] = mapped_column(VARCHAR(100))
    last_login: Mapped[datetime] = mapped_column(DateTime(), default=datetime.now)
    created_on: Mapped[datetime] = mapped_column(DateTime(), default=datetime.now)
    updated_on: Mapped[datetime] = mapped_column(DateTime(), default=datetime.now, onupdate=datetime.now)
    results: Mapped[list["Result"]] = relationship("Result", back_populates='user', cascade='all,delete')

    def __str__(self):
        return f"{self.fname} {self.lname}"

class Question(Base):
    __tablename__ = 'questions'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    question: Mapped[str] = mapped_column(VARCHAR(2000), nullable=False)
    answer: Mapped[str] = mapped_column(VARCHAR(250), nullable=False)
    section_id: Mapped[int] = mapped_column(Integer, ForeignKey('sections.id'), nullable=False)
    section: Mapped["Section"] = relationship("Section", back_populates='questions')
    created_on: Mapped[datetime] = mapped_column(DateTime(), default=datetime.now)

    def __str__(self):
        return f"{self.id}: {self.question} - {self.answer}"

class Section(Base):
    __tablename__ = 'sections'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(VARCHAR(150), unique=True, nullable=False)
    results: Mapped[list["Result"]] = relationship("Result", back_populates='section', cascade='all,delete')
    questions: Mapped[list["Question"]] = relationship("Question", back_populates='section', cascade='all,delete')
    created_on: Mapped[datetime] = mapped_column(DateTime(), default=datetime.now)

    def __str__(self):
        return self.title

class Result(Base):
    __tablename__ = 'results'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    result: Mapped[float] = mapped_column(Float(2), nullable=False)  # result of survey, 0 - 100
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id'), nullable=False)
    section_id: Mapped[int] = mapped_column(Integer, ForeignKey('sections.id'), nullable=False)
    section: Mapped["Section"] = relationship("Section", back_populates='results')
    user: Mapped["User"] = relationship("User", back_populates='results')
    created_on: Mapped[datetime] = mapped_column(DateTime(), default=datetime.now)

    def __str__(self):
        return self.result