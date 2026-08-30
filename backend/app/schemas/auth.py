from pydantic import BaseModel, EmailStr, ConfigDict, Field


class UserRegister(BaseModel):
    name: str
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    name: str
    email: EmailStr
    is_premium_trial_used: bool


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut
