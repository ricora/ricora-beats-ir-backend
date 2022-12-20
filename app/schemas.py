from datetime import datetime
from pydantic import BaseModel


class ScoreBase(BaseModel):
    folder: str
    filename: str
    score: float
    combo: int
    judge_0: int
    judge_1: int
    judge_2: int
    judge_3: int
    judge_4: int


class ScoreCreate(ScoreBase):
    pass


class Score(ScoreBase):
    id: int
    player_id: int
    submitted_on: datetime

    class Config:
        orm_mode = True


class UserBase(BaseModel):
    screen_name: str
    email: str


class UserCreate(UserBase):
    password: str


class User(UserBase):
    id: int
    is_active: bool = True
    hashed_password: str
    rank: int
    performance_point: int
    self_introduction: str

    scores: list[Score] = []

    class Config:
        orm_mode = True


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    screen_name: str
