from datetime import datetime, timedelta

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel, EmailStr
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, create_engine, func
from sqlalchemy.orm import DeclarativeBase, Session, relationship, sessionmaker

DATABASE_URL = "sqlite:///./tetris.db"
SECRET_KEY = "tetris-secret-key-change-in-production-2024"
ALGORITHM = "HS256"
TOKEN_EXPIRE_HOURS = 24

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, nullable=False)
    hashed_password = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    records = relationship("GameRecord", back_populates="user")


class GameRecord(Base):
    __tablename__ = "game_records"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    score = Column(Integer, nullable=False)
    level = Column(Integer, nullable=False)
    lines = Column(Integer, nullable=False)
    played_at = Column(DateTime, default=datetime.utcnow)
    user = relationship("User", back_populates="records")


Base.metadata.create_all(bind=engine)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


class UserRegister(BaseModel):
    email: EmailStr
    username: str
    password: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class TokenOut(BaseModel):
    access_token: str
    token_type: str
    username: str


class GameRecordIn(BaseModel):
    score: int
    level: int
    lines: int


app = FastAPI(title="Tetris API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    err = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="인증이 필요합니다",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if not email:
            raise err
    except JWTError:
        raise err
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise err
    return user


@app.post("/auth/register", status_code=201)
def register(data: UserRegister, db: Session = Depends(get_db)):
    if db.query(User).filter(User.email == data.email).first():
        raise HTTPException(status_code=400, detail="이미 등록된 이메일입니다")
    db.add(User(
        email=data.email,
        username=data.username,
        hashed_password=pwd_context.hash(data.password),
    ))
    db.commit()
    return {"message": "회원가입이 완료되었습니다"}


@app.post("/auth/login", response_model=TokenOut)
def login(data: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == data.email).first()
    if not user or not pwd_context.verify(data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="이메일 또는 비밀번호가 올바르지 않습니다")
    exp = datetime.utcnow() + timedelta(hours=TOKEN_EXPIRE_HOURS)
    token = jwt.encode({"sub": user.email, "exp": exp}, SECRET_KEY, algorithm=ALGORITHM)
    return {"access_token": token, "token_type": "bearer", "username": user.username}


@app.get("/auth/me")
def me(current_user: User = Depends(get_current_user)):
    return {"email": current_user.email, "username": current_user.username}


@app.post("/games/record", status_code=201)
def save_record(
    data: GameRecordIn,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    db.add(GameRecord(user_id=current_user.id, score=data.score, level=data.level, lines=data.lines))
    db.commit()
    return {"message": "기록이 저장되었습니다"}


@app.get("/games/top-score")
def top_score(db: Session = Depends(get_db)):
    result = (
        db.query(User.username, func.max(GameRecord.score).label("score"))
        .join(GameRecord)
        .group_by(User.id)
        .order_by(func.max(GameRecord.score).desc())
        .first()
    )
    if not result:
        return {"username": None, "score": 0}
    return {"username": result.username, "score": result.score}


@app.get("/games/my-records")
def my_records(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    records = (
        db.query(GameRecord)
        .filter(GameRecord.user_id == current_user.id)
        .order_by(GameRecord.played_at.desc())
        .limit(10)
        .all()
    )
    return [
        {"score": r.score, "level": r.level, "lines": r.lines, "played_at": r.played_at.isoformat()}
        for r in records
    ]
