from jose import jwt, JWTError
from datetime import datetime, timedelta

SECRET_KEY = "DESHITECH_SUPER_SECRET_KEY"
ALGORITHM = "HS256"
EXPIRE_MINUTES = 120

def create_token(data: dict):
    payload = data.copy()
    payload["exp"] = datetime.utcnow() + timedelta(minutes=EXPIRE_MINUTES)
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def decode_token(token: str):
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        return None