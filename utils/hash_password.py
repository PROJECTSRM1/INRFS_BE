from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    # bcrypt max length = 72 characters → safely truncate
    password = password[:72]
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    plain_password = plain_password[:72]
    return pwd_context.verify(plain_password, hashed_password)
