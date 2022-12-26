from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Float, DateTime
from sqlalchemy.orm import relationship

from database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    screen_name = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)

    self_introduction = Column(String, default="")

    rank = Column(Integer, default=0)
    performance_point = Column(Integer, default=0)

    scores = relationship("Score", back_populates="player")


class Score(Base):
    __tablename__ = "scores"

    id = Column(Integer, primary_key=True, index=True)
    folder = Column(String, index=True)
    filename = Column(String, index=True)
    level = Column(Integer, default=0)
    score = Column(Float)
    combo = Column(Integer)
    judge_0 = Column(Integer)
    judge_1 = Column(Integer)
    judge_2 = Column(Integer)
    judge_3 = Column(Integer)
    judge_4 = Column(Integer)

    submitted_on = Column(DateTime)
    performance_point = Column(Integer, default=0)

    player_id = Column(Integer, ForeignKey("users.id"))

    player = relationship("User", back_populates="scores")
