from datetime import datetime, timezone
from typing import Optional, Dict, List 
from jose import JWTError, jwt
from pydantic import BaseModel
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from app.core.config import SECRET_KEY, ALGORITHM
from app.schemas.token_schemas import TokenData 


fake_users_db = {
    "testuser": {
        "username": "testuser",
        "full_name": "Test User",
        "email": "testuser@example.com",
        "password": "testpassword123", 
        "disabled": False,
    }
}

class UserInDB(BaseModel):
    username: str
    email: Optional[str] = None
    full_name: Optional[str] = None
    disabled: Optional[bool] = None
    password: str 


def verify_password(plain_password_provided: str, plain_password_stored: str) -> bool:
    print(f"AUTH_SERVICE DEBUG (plain_text_verify): Provided='{plain_password_provided}', Stored='{plain_password_stored}'")
    return plain_password_provided == plain_password_stored

# --- Funções de Autenticação e Token ---

def get_user(username: str) -> Optional[UserInDB]:

    if username in fake_users_db:
        user_dict = fake_users_db[username]
        return UserInDB(**user_dict)
    return None

async def authenticate_user(username: str, password_provided: str) -> Optional[UserInDB]:

    user = get_user(username)
    print(f"AUTH_SERVICE (plain_text): Tentando autenticar usuário: {username}")
    if not user:
        print(f"AUTH_SERVICE (plain_text): Usuário '{username}' NÃO encontrado.")
        return None
    
    print(f"AUTH_SERVICE (plain_text): Usuário '{username}' encontrado. Senha armazenada (texto plano): '{user.password}'")
    
    password_matches = verify_password(password_provided, user.password)
    print(f"AUTH_SERVICE (plain_text): Senha fornecida ('{password_provided}') corresponde à armazenada? {password_matches}")
    
    if not password_matches:
        print(f"AUTH_SERVICE (plain_text): Senha incorreta para o usuário '{username}'.")
        return None
    
    if user.disabled:
        print(f"AUTH_SERVICE (plain_text): Usuário '{username}' está desabilitado.")
        return None
    
    print(f"AUTH_SERVICE (plain_text): Usuário '{username}' autenticado com SUCESSO.")
    return user

def create_access_token(data: Dict) -> str:

    to_encode = data.copy()

    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    print(f"AUTH_SERVICE (plain_text): Token de acesso criado para dados: {data}")
    return encoded_jwt

async def decode_access_token(token: str) -> Optional[TokenData]:

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: Optional[str] = payload.get("sub")
        
        if username is None:
            print("AUTH_SERVICE (plain_text): Erro ao decodificar token - username (sub) não encontrado.")
            return None

        token_data = TokenData(username=username)
        print(f"AUTH_SERVICE (plain_text): Token decodificado com sucesso para usuário: {username}")
        return token_data
    except JWTError as e:
        print(f"AUTH_SERVICE (plain_text): Erro ao decodificar token JWT - {type(e).__name__}: {str(e)}")
        return None
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/token")

async def get_current_user(token: str = Depends(oauth2_scheme)) -> UserInDB:
    print(f"AUTH_SERVICE (get_current_user): Tentando validar token (início): {token[:20]}...")

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Não foi possível validar as credenciais",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    token_data: Optional[TokenData] = await decode_access_token(token)
    
    if token_data is None or token_data.username is None:
        print(f"AUTH_SERVICE (get_current_user): Token inválido ou username não encontrado no token.")
        raise credentials_exception
    
    user = get_user(token_data.username) 
    if user is None:
        print(f"AUTH_SERVICE (get_current_user): Usuário '{token_data.username}' do token não encontrado no DB.")
        raise credentials_exception
    if user.disabled:
        print(f"AUTH_SERVICE (get_current_user): Usuário '{token_data.username}' está desabilitado.")

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Usuário inativo ou desabilitado."
        )
        
    print(f"AUTH_SERVICE (get_current_user): Usuário '{user.username}' validado com sucesso via token.")
    return user