from datetime import datetime

from sqlalchemy.orm import Session

import models, schemas


def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()


def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()


def get_user_by_screen_name(db: Session, screen_name: str):
    return db.query(models.User).filter(models.User.screen_name == screen_name).first()


def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()


def create_user(db: Session, user: schemas.UserCreate, hashed_password: str):
    db_user = models.User(screen_name=user.screen_name, email=user.email, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_score(db: Session, folder: str, filename: str, player_id: int):
    return (
        db.query(models.Score)
        .filter(models.Score.folder == folder)
        .filter(models.Score.filename == filename)
        .filter(models.Score.player_id == player_id)
        .first()
    )


def get_scores(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Score).offset(skip).limit(limit).all()


def get_scores_by_beatmap(db: Session, folder: str, filename: str):
    return db.query(models.Score).filter(models.Score.folder == folder).filter(models.Score.filename == filename).all()


def create_score(db: Session, score: schemas.ScoreCreate, player_id: int):
    db_score = models.Score(**score.dict(), player_id=player_id, submitted_on=datetime.now())
    db.add(db_score)
    db.commit()
    db.refresh(db_score)
    return db_score


def update_score(db: Session, score: schemas.ScoreCreate, player_id: int):
    db_score = (
        db.query(models.Score)
        .filter(models.Score.folder == score.folder)
        .filter(models.Score.filename == score.filename)
        .filter(models.Score.player_id == player_id)
        .first()
    )
    assert db_score is not None
    db_score.submitted_on = datetime.now()

    for key, value in score.dict().items():
        setattr(db_score, key, value)
    db.add(db_score)
    db.commit()
    db.refresh(db_score)
    return db_score
