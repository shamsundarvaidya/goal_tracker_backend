from datetime import datetime, timezone, timedelta
import jwt
from fastapi import  HTTPException, status, Depends, Response, Request
from mongoDBModels import db_models

JWT_SECRET = "PASSWORD"
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION = timedelta(hours=1)


def create_access_token(data: dict, expires_delta: timedelta = JWT_EXPIRATION):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + expires_delta
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)


def verify_token(token: str):
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload if payload else None
    except jwt.ExpiredSignatureError:
        return None  # Token expired
    except jwt.InvalidTokenError:
        return None  # Invalid token


async def get_current_user(request: Request):
    print("running token verification")

    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="No token",
            )
    payload = verify_token(token)

    if payload is None:
        print("Cookies received:", request.cookies)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    user = db_models.User.objects(username=payload["sub"]).first()
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invalid token")
    print("token verified")
    return user
