from jose import jwt
from datetime import datetime, timedelta, timezone
from auth.config import JWT_SECRET_KEY

def create_jwt_token(user_email: str) -> str:
    expiration = datetime.now(timezone.utc) + timedelta(hours=1)
    payload = {"sub": user_email, "exp": expiration}
    return jwt.encode(payload, JWT_SECRET_KEY, algorithm="HS256")

def verify_jwt_token(token: str):
    return jwt.decode(token, JWT_SECRET_KEY, algorithms=["HS256"])
