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




# ========================
# TEMP USER DATA STORE
# ========================
# email -> full user data (dict)

_user_temp_store = {}


def store_user_data(email: str, user_data: dict):
    """
    Temporarily store user registration data
    until OTP verification
    """
    _user_temp_store[email] = user_data


def pop_user_data(email: str):
    """
    Get and remove stored user data
    after OTP verification
    """
    return _user_temp_store.pop(email, None)

def is_user_registered(email: str) -> bool:
    """
    Check if the user has a pending registration (OTP not verified yet)
    """
    return email in _user_temp_store







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
