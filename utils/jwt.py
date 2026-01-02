from datetime import datetime, timedelta
from jose import jwt
import os

from dotenv import load_dotenv

load_dotenv()  # ✅ REQUIRED

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_EXPIRE_MIN = 15
REFRESH_EXPIRE_DAYS = 7


if not SECRET_KEY:
    raise RuntimeError("SECRET_KEY is not set in environment variables")


def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_EXPIRE_MIN)
    to_encode.update({"exp": expire, "type": "access"})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def create_refresh_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=REFRESH_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)



# # utils/auth.py
# from fastapi import Depends, HTTPException
# from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
# from jose import jwt, JWTError
# from sqlalchemy.orm import Session

# from core.database import get_db
# from models.generated_models import UserRegistration
# from utils.jwt import SECRET_KEY, ALGORITHM

# security = HTTPBearer()

# def get_current_user(
#     credentials: HTTPAuthorizationCredentials = Depends(security),
#     db: Session = Depends(get_db)
# ):
#     token = credentials.credentials

#     try:
#         payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
#         user_id = payload.get("user_id")
#         token_type = payload.get("type")

#         if token_type != "access":
#             raise HTTPException(status_code=401, detail="Invalid token type")

#         if not user_id:
#             raise HTTPException(status_code=401, detail="Invalid token")

#     except JWTError:
#         raise HTTPException(status_code=401, detail="Invalid or expired token")

#     user = db.query(UserRegistration).filter(
#         UserRegistration.id == user_id
#     ).first()

#     if not user:
#         raise HTTPException(status_code=401, detail="User not found")

#     return user


















# from datetime import datetime, timedelta
# from jose import jwt, JWTError
# import os

# from dotenv import load_dotenv

# from fastapi import Depends, HTTPException, status
# from fastapi.security import OAuth2PasswordBearer
# from sqlalchemy.orm import Session

# from core.database import get_db
# from models.generated_models import UserRegistration


# # ---------------------------
# # LOAD ENV
# # ---------------------------
# load_dotenv()

# SECRET_KEY = os.getenv("SECRET_KEY")
# ALGORITHM = "HS256"
# ACCESS_EXPIRE_MIN = 15
# REFRESH_EXPIRE_DAYS = 7

# if not SECRET_KEY:
#     raise RuntimeError("SECRET_KEY is not set in environment variables")


# # ---------------------------
# # TOKEN GENERATION
# # ---------------------------
# def create_access_token(data: dict) -> str:
#     to_encode = data.copy()
#     expire = datetime.utcnow() + timedelta(minutes=ACCESS_EXPIRE_MIN)
#     to_encode.update({
#         "exp": expire,
#         "type": "access"
#     })
#     return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


# def create_refresh_token(data: dict) -> str:
#     to_encode = data.copy()
#     expire = datetime.utcnow() + timedelta(days=REFRESH_EXPIRE_DAYS)
#     to_encode.update({
#         "exp": expire,
#         "type": "refresh"
#     })
#     return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


# # ---------------------------
# # JWT VALIDATION (READ TOKEN)
# # ---------------------------
# oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/users/login")


# def get_current_user(
#     token: str = Depends(oauth2_scheme),
#     db: Session = Depends(get_db),
# ) -> UserRegistration:
#     try:
#         payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

#         # 🔐 Ensure access token
#         if payload.get("type") != "access":
#             raise HTTPException(
#                 status_code=status.HTTP_401_UNAUTHORIZED,
#                 detail="Invalid access token",
#             )

#         inv_reg_id = payload.get("sub")
#         if not inv_reg_id:
#             raise HTTPException(
#                 status_code=status.HTTP_401_UNAUTHORIZED,
#                 detail="Invalid token payload",
#             )

#         user = (
#             db.query(UserRegistration)
#             .filter(UserRegistration.inv_reg_id == inv_reg_id)
#             .first()
#         )

#         if not user:
#             raise HTTPException(
#                 status_code=status.HTTP_401_UNAUTHORIZED,
#                 detail="User not found",
#             )

#         return user

#     except JWTError:
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Could not validate credentials",
#         )
