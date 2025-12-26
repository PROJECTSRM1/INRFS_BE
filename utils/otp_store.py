import random
import time

# ========================
# OTP storage
# ========================

# email -> {otp, expiry}
_otp_store = {}

OTP_EXPIRY_SECONDS = 300  # 5 minutes


def generate_otp(email: str) -> str:
    otp = str(random.randint(100000, 999999))
    _otp_store[email] = {
        "otp": otp,
        "expiry": time.time() + OTP_EXPIRY_SECONDS,
    }
    return otp


def verify_otp(email: str, otp: str) -> bool:
    record = _otp_store.get(email)

    if not record:
        return False

    if time.time() > record["expiry"]:
        del _otp_store[email]
        return False

    if record["otp"] != otp:
        return False

    del _otp_store[email]
    return True


# ========================
# VERIFIED USERS (OTP passed)
# ========================

_verified_users = set()  # email or inv_reg_id


def mark_verified(identifier: str):
    _verified_users.add(identifier)


def is_verified(identifier: str) -> bool:
    return identifier in _verified_users








# import random
# import time

# # email -> {otp, expiry}
# _otp_store = {}

# OTP_EXPIRY_SECONDS = 300  # 5 minutes


# def generate_otp(email: str) -> str:
#     otp = str(random.randint(100000, 999999))
#     _otp_store[email] = {
#         "otp": otp,
#         "expiry": time.time() + OTP_EXPIRY_SECONDS,
#     }
#     return otp


# def verify_otp(email: str, otp: str) -> bool:
#     record = _otp_store.get(email)

#     if not record:
#         return False

#     if time.time() > record["expiry"]:
#         del _otp_store[email]
#         return False

#     if record["otp"] != otp:
#         return False

#     del _otp_store[email]
#     return True
