from pydantic import BaseModel
from datetime import date

class UserCreate(BaseModel):
    first_name: str
    last_name: str
    email: str
    mobile: str
    password: str
    gender_id: int
    age: int
    dob: date
    inv_reg_id: str
    role_id: int
