from sqlalchemy.orm import relationship, declarative_base
from sqlalchemy import Integer, VARCHAR, Column, DateTime, ForeignKey, Boolean, Float
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, autoincrement=True)
    is_admin = Column(Boolean, default=False, nullable=False)
    tg_id = Column(VARCHAR(10), unique=True, nullable=False)
    fname = Column(VARCHAR(100))
    lname = Column(VARCHAR(100))
    username = Column(VARCHAR(100))
    last_login = Column(DateTime(), default=datetime.now)
    created_on = Column(DateTime(), default=datetime.now)
    updated_on = Column(DateTime(), default=datetime.now, onupdate=datetime.now)

    def __str__(self):
        return f"{self.fname} {self.lname}"

class Question(Base):
    __tablename__ = 'questions'

    id = Column(Integer, primary_key=True, autoincrement=True)
    question = Column(VARCHAR(2000), nullable=False)
    answer = Column(VARCHAR(250), nullable=False)
    section_id = Column(Integer, ForeignKey('sections.id'), nullable=False)
    created_on = Column(DateTime(), default=datetime.now)

    def __str__(self):
        return f"{self.id}: {self.question} - {self.answer}"

class Section(Base):
    __tablename__ = 'sections'

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(VARCHAR(150), unique=True, nullable=False)
    results = relationship("Result", backref='section', cascade='all,delete')
    questions = relationship("Question", backref='section', cascade='all,delete')
    created_on = Column(DateTime(), default=datetime.now)

    def __str__(self):
        return self.title

class Result(Base):
    __tablename__ = 'results'

    id = Column(Integer, primary_key=True, autoincrement=True)
    result = Column(Float(2), nullable=False)  # result of survey in percent
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    section_id = Column(Integer, ForeignKey('sections.id'), nullable=False)
    user = relationship("User", backref='results')
    created_on = Column(DateTime(), default=datetime.now)

    def __str__(self):
        return self.result