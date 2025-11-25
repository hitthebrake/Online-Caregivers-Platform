from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from sqlalchemy.orm import Session, joinedload
from . import models
from .database import get_db
import os
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()

class TokenData(BaseModel):
    email: Optional[str] = None
    user_type: Optional[str] = None

def truncate_password(password: str) -> str:
    if not isinstance(password, str):
        password = str(password)
    password_bytes = password.encode('utf-8')
    if len(password_bytes) > 72:
        password_bytes = password_bytes[:72]
    return password_bytes.decode('utf-8', 'ignore')

def verify_password(plain_password, hashed_password):
    plain_password = truncate_password(plain_password).strip()
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    password = truncate_password(password)
    return pwd_context.hash(password).strip()

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security),
                           db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        user_type: str = payload.get("user_type")
        if email is None or user_type is None:
            raise credentials_exception
        token_data = TokenData(email=email, user_type=user_type)
    except JWTError:
        raise credentials_exception

    user = db.query(models.User).filter(models.User.email == token_data.email).first()
    if user is None:
        raise credentials_exception
    return user

async def get_current_caregiver(current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    caregiver = db.query(models.Caregiver) \
        .filter(models.Caregiver.caregiver_user_id == current_user.user_id) \
        .options(joinedload(models.Caregiver.user)).first()
    if not caregiver:
        raise HTTPException(status_code=403, detail="Not a caregiver")
    return caregiver

async def get_current_member(current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    member = db.query(models.Member) \
        .filter(models.Member.member_user_id == current_user.user_id) \
        .options(joinedload(models.Member.user)).first()
    if not member:
        raise HTTPException(status_code=403, detail="Not a member")
    return member