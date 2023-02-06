from datetime import datetime, timezone, timedelta
import sqlalchemy
from sqlalchemy.orm import Session

import models, schemas

import performance


def get_user(db: Session, user_id: int):
    return db.execute(sqlalchemy.select(models.User).filter(models.User.id == user_id)).scalars().first()


def get_user_by_email(db: Session, email: str):
    return db.execute(sqlalchemy.select(models.User).filter(models.User.email == email)).scalars().first()


def get_user_by_screen_name(db: Session, screen_name: str):
    return db.execute(sqlalchemy.select(models.User).filter(models.User.screen_name == screen_name)).scalars().first()


def get_users(db: Session, skip: int = 0, limit: int = 100000):
    return db.execute(sqlalchemy.select(models.User).offset(skip).limit(limit)).scalars().all()


def create_user(db: Session, user: schemas.UserCreate, hashed_password: str):
    db_user = models.User(screen_name=user.screen_name, email=user.email, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_score(db: Session, folder: str, filename: str, player_id: int):
    return (
        db.execute(
            sqlalchemy.select(models.Score)
            .filter(models.Score.folder == folder)
            .filter(models.Score.filename == filename)
            .filter(models.Score.player_id == player_id)
        )
        .scalars()
        .first()
    )


def get_scores(db: Session, skip: int = 0, limit: int = 100):
    return db.execute(sqlalchemy.select(models.Score).offset(skip).limit(limit)).scalars().all()


def get_scores_by_beatmap(db: Session, folder: str, filename: str):
    return (
        db.execute(
            sqlalchemy.select(models.Score)
            .filter(models.Score.folder == folder)
            .filter(models.Score.filename == filename)
        )
        .scalars()
        .all()
    )


def create_score(db: Session, score: schemas.ScoreCreate, player_id: int):
    db_score = models.Score(
        **score.dict(),
        player_id=player_id,
        submitted_on=datetime.now(timezone(timedelta(hours=0))) + timedelta(hours=9),
        performance_point=performance.calculate(score=score.score, level=score.level)
    )
    db.add(db_score)
    db.commit()
    db.refresh(db_score)
    return db_score


def update_score(db: Session, score: schemas.ScoreCreate, player_id: int):
    db_score: schemas.Score = get_score(db, folder=score.folder, filename=score.filename, player_id=player_id)
    db_score.submitted_on = datetime.now(timezone(timedelta(hours=0))) + timedelta(hours=9)
    db_score.performance_point = performance.calculate(score=score.score, level=score.level)

    for key, value in score.dict().items():
        setattr(db_score, key, value)
    db.add(db_score)
    db.commit()
    db.refresh(db_score)
    return db_score


def update_ranking(db: Session):
    db_users: list[schemas.UserScore] = get_users(db)
    for user in db_users:
        performance_point = 0
        for i, score in enumerate(sorted(user.scores, key=lambda score: score.performance_point, reverse=True)[:30]):
            performance_point += score.performance_point * (100 ** (-i / 30))
        user.performance_point = performance_point

        db.add(user)

    for i, user in enumerate(sorted(db_users, key=lambda user: user.performance_point, reverse=True)):
        user.rank = i + 1

        db.add(user)
    db.commit()
