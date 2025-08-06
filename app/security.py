import datetime
import logging
import os
from fastapi import HTTPException, status, Depends
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from passlib.context import CryptContext
from jose import jwt, ExpiredSignatureError, JWTError
from dotenv import load_dotenv

from app.config import config
from app.utils.user_utils import fetch_user_by_email

load_dotenv()
logger = logging.getLogger(__name__)

security = HTTPBearer()
pwd_context = CryptContext(schemes=["bcrypt"])

credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)

def access_token_expire_minutes() -> int:
    return 7 * 24 * 60  # 7 days = 10080 minutes

def create_access_token(email: str, role_id: int) -> str:
    expire = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(minutes=access_token_expire_minutes())
    jwt_data = {
        "sub": email,
        "role_id": role_id,
        "exp": expire
    }
    encoded_jwt = jwt.encode(
        jwt_data,
        key=os.getenv("DEV_SECRET_KEY"),
        algorithm=os.getenv("DEV_ALGORITHM")
    )
    return encoded_jwt

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    try:
        payload = jwt.decode(token, key=os.getenv("DEV_SECRET_KEY"), algorithms=[os.getenv("DEV_ALGORITHM")])
        email = payload.get("sub")
        role_id = payload.get("role_id")
        if email is None or role_id is None:
            raise credentials_exception
    except ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"}
        )
    except JWTError:
        raise credentials_exception

    user = await fetch_user_by_email(email=email)
    if user is None:
        raise credentials_exception
    return user

async def get_current_admin_user(current_user=Depends(get_current_user)):
    if current_user["roleId"] != 1:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "status_code": 403,
                "message": "Admin privileges required"
            }
        )
    return current_user

async def get_current_regular_user(current_user=Depends(get_current_user)):
    if current_user["roleId"] != 2:
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content={
                "status_code": status.HTTP_403_FORBIDDEN,
                "message": "User privileges required"
            }
        )
    return current_user

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def hash_password(password):
    return pwd_context.hash(password)