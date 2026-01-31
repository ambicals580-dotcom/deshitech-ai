import os, jwt
from datetime import datetime, timedelta

SECRET = os.getenv("JWT_SECRET", "deshitech_secret")

def create_token(user):
    payload = {
        "user": user,
        "exp": datetime.utcnow() + timedelta(hours=12)
    }
    return jwt.encode(payload, SECRET, algorithm="HS256")

def verify_token(token):
    try:
        data = jwt.decode(token, SECRET, algorithms=["HS256"])
        return data["user"]
    except:
        return None