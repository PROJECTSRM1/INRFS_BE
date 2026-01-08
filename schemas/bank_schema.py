from pydantic import BaseModel, Field
from typing import Optional


class BankDetailsCreate(BaseModel):
    bank_id: int = Field(..., example=1)
    bank_account_no: str = Field(..., min_length=9, max_length=20, example=123456789012)
    ifsc_code: str = Field(..., min_length=4, max_length=20, example="HDFC0001234")



class BankDetailsResponse(BaseModel):
    bank_id: Optional[int]
    bank_account_no: Optional[int]
    ifsc_code: Optional[str]
    is_verified: Optional[bool] = None
    # is_verified: bool



