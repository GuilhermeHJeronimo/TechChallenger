from pydantic import BaseModel, Field
from typing import Optional, List

class Token(BaseModel):
    access_token: str = Field(..., description="O token de acesso JWT.")
    token_type: str = Field(default="bearer", description="O tipo do token (geralmente 'bearer').")

class TokenData(BaseModel):
    username: Optional[str] = Field(None, description="O nome de usuário (ou identificador) associado ao token.")
