from datetime import datetime, timezone
from typing import Optional, Dict
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from app.core.config import SECRET_KEY, ALGORITHM
from app.schemas.token_schemas import TokenData
from app.crud import crud_user
from app.models import user as user_model
from app.db.session import get_db
from app.core.security import verify_password

async def authenticate_user(db: Session, username: str, password_provided: str) -> Optional[user_model.User]:

    print(f"AUTH_SERVICE (DB): Tentando autenticar usuário: {username}")
    user = crud_user.get_user_by_username(db, username=username)
    
    if not user:
        print(f"AUTH_SERVICE (DB): Usuário '{username}' NÃO encontrado no banco de dados.")
        return None
    
    print(f"AUTH_SERVICE (DB): Usuário '{username}' encontrado. Verificando senha...")
    
    if not verify_password(password_provided, user.hashed_password_sha256):
        print(f"AUTH_SERVICE (DB): Senha incorreta para o usuário '{username}'.")
        return None
    
    if user.disabled:
        print(f"AUTH_SERVICE (DB): Usuário '{username}' está desabilitado.")
        return None
    
    print(f"AUTH_SERVICE (DB): Usuário '{username}' autenticado com SUCESSO via DB.")
    return user

def create_access_token(data: Dict) -> str:

    to_encode = data.copy()
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    print(f"AUTH_SERVICE (DB): Token de acesso criado para dados: {data}")
    return encoded_jwt

async def decode_access_token(token: str) -> Optional[TokenData]:

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: Optional[str] = payload.get("sub")
        
        if username is None:
            print("AUTH_SERVICE (DB): Erro ao decodificar token - username (sub) não encontrado.")
            return None
        
        token_data = TokenData(username=username)
        print(f"AUTH_SERVICE (DB): Token decodificado com sucesso para usuário: {username}")
        return token_data
    except JWTError as e:
        print(f"AUTH_SERVICE (DB): Erro ao decodificar token JWT - {type(e).__name__}: {str(e)}")
        return None

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/token")

async def get_current_user(
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
) -> user_model.User:
    print(f"AUTH_SERVICE (get_current_user DB): Tentando validar token (início)...")

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Não foi possível validar as credenciais",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    token_data: Optional[TokenData] = await decode_access_token(token)
    
    if token_data is None or token_data.username is None:
        print(f"AUTH_SERVICE (get_current_user DB): Token inválido ou username não encontrado no token.")
        raise credentials_exception
    
    user = crud_user.get_user_by_username(db, username=token_data.username)
    
    if user is None:
        print(f"AUTH_SERVICE (get_current_user DB): Usuário '{token_data.username}' do token não encontrado no DB.")
        raise credentials_exception
    if user.disabled:
        print(f"AUTH_SERVICE (get_current_user DB): Usuário '{token_data.username}' está desabilitado.")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Usuário inativo ou desabilitado."
        )
        
    print(f"AUTH_SERVICE (get_current_user DB): Usuário '{user.username}' validado com sucesso via token e DB.")
    return user