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


class UserCreate(BaseModel):
    screen_name: str
    password: str
    email: str


class User(BaseModel):
    id: int
    screen_name: str
    is_active: bool
    rank: int
    performance_point: int
    self_introduction: str

    class Config:
        orm_mode = True


class UserScore(User):
    scores: list[Score] = []

    class Config:
        orm_mode = True


class UserDB(User):
    hashed_password: str
    email: str

    class Config:
        orm_mode = True


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    screen_name: str
