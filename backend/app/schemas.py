import re
from datetime import date, datetime
from typing import Annotated
from pydantic import AfterValidator, BaseModel, Field, ConfigDict

EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

def _normalize_email(value: str) -> str:
    """Validate e-mail syntax without rejecting reserved zones such as .local."""
    value = value.strip().lower()
    if not EMAIL_PATTERN.match(value):
        raise ValueError("Некорректный адрес электронной почты")
    return value

Email = Annotated[str, AfterValidator(_normalize_email)]

class UserCreate(BaseModel):
    email: Email
    full_name: str = Field(min_length=2, max_length=160)
    password: str = Field(min_length=8)

class Login(BaseModel):
    email: Email
    password: str

class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    email: str
    full_name: str
    role: str

class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut

class EquipmentCreate(BaseModel):
    name: str = Field(min_length=2, max_length=160)
    category: str
    description: str = ""
    daily_price: float = Field(gt=0)
    quantity: int = Field(ge=1)
    image_url: str = ""

class EquipmentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    category: str
    description: str
    daily_price: float
    quantity: int
    image_url: str
    is_active: bool

class RentalCreate(BaseModel):
    equipment_id: int
    start_date: date
    end_date: date

class RentalOut(BaseModel):
    id: int
    customer_id: int
    customer_name: str
    equipment_id: int
    equipment_name: str
    start_date: date
    end_date: date
    total_price: float
    status: str
    returned_at: datetime | None

class UserRoleUpdate(BaseModel):
    role: str
