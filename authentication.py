from datetime import datetime, timezone, timedelta
import jwt


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
    

    