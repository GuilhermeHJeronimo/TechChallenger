from pydantic import BaseModel, Field
from typing import Optional

class UserBase(BaseModel):

    username: str = Field(..., min_length=3, max_length=50, description="Nome de usuário único para login.")
    full_name: Optional[str] = Field(None, max_length=100, description="Nome completo do usuário.")


class UserCreate(UserBase):

    password: str = Field(..., min_length=6, description="Senha do usuário (será hasheada).")


class UserUpdate(BaseModel):

    full_name: Optional[str] = Field(None, max_length=100, description="Novo nome completo do usuário.")
    password: Optional[str] = Field(None, min_length=6, description="Nova senha (será hasheada se fornecida).")
    disabled: Optional[bool] = None


class UserInDBBase(UserBase):

    id: int
    hashed_password_sha256: str
    disabled: bool = False

    class Config:
        from_attributes = True


class User(UserBase):

    id: int
    disabled: bool = False

    class Config:
        from_attributes = True