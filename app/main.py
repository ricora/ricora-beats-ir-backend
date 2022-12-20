from datetime import datetime, timedelta
import os

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

import crud, models, schemas
from database import SessionLocal, engine

SECRET_KEY = os.environ["SECRET_KEY"]
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def authenticate_user(db: Session, screen_name: str, password: str) -> schemas.User | bool:
    user = crud.get_user_by_screen_name(db, screen_name)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def get_current_user(token: str = Depends(oauth2_scheme)) -> schemas.User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        screen_name: str | None = payload.get("sub")
        if screen_name is None:
            raise credentials_exception
        token_data = schemas.TokenData(screen_name=screen_name)
    except JWTError:
        raise credentials_exception
    with SessionLocal() as db:
        user = crud.get_user_by_screen_name(db, screen_name=token_data.screen_name)
    if user is None:
        raise credentials_exception
    return user


def get_current_active_user(current_user: schemas.User = Depends(get_current_user)) -> schemas.User:
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


@app.post("/token", response_model=schemas.Token)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect screen name or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    assert not isinstance(user, bool)
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub": user.screen_name}, expires_delta=access_token_expires)
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/users/me")
def read_users_me(current_user: schemas.User = Depends(get_current_active_user)):
    return current_user


@app.post("/users/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    db_user = crud.get_user_by_screen_name(db, screen_name=user.screen_name)
    if db_user:
        raise HTTPException(status_code=400, detail="Screen name already registered")
    return crud.create_user(db=db, user=user, hashed_password=get_password_hash(user.password))


@app.get("/users/", response_model=list[schemas.User])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    users = crud.get_users(db, skip=skip, limit=limit)
    return users


@app.get("/users/{user_id}", response_model=schemas.User)
def read_user(user_id: int, db: Session = Depends(get_db)):
    db_user = crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user


@app.post("/scores/", response_model=schemas.Score)
def create_score(
    score: schemas.ScoreCreate,
    current_user: schemas.User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    old_score: schemas.Score | None = crud.get_score(
        db, folder=score.folder, filename=score.filename, player_id=current_user.id
    )
    if old_score:
        if old_score.score <= score.score:
            return crud.update_score(db=db, score=score, player_id=current_user.id)
        else:
            return old_score
    else:
        return crud.create_score(db=db, score=score, player_id=current_user.id)


@app.get("/scores/", response_model=list[schemas.Score])
def read_scores(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    scores = crud.get_scores(db, skip=skip, limit=limit)
    return scores


@app.get("/scores/{folder}/{filename}/", response_model=list[schemas.Score])
def read_score(folder: str, filename: str, db: Session = Depends(get_db)):
    scores = crud.get_scores_by_beatmap(db, folder=folder, filename=filename)
    return scores
