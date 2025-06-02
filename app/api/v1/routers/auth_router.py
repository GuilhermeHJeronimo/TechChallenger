from fastapi import APIRouter, Depends, HTTPException, status, Form
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import Optional

from app.services import auth_service
from app.schemas import token_schemas
from app.schemas import user_schemas
from app.crud import crud_user
from app.db.session import get_db

router = APIRouter()

@router.post(
    "/token", 
    response_model=token_schemas.Token,
    summary="Autentica o usuário e retorna um token de acesso.",
    description="Use este endpoint para obter um token JWT fornecendo nome de usuário e senha como form data."
)
async def login_for_access_token(
    db: Session = Depends(get_db),
    form_data: OAuth2PasswordRequestForm = Depends()
):
    print(f"AUTH_ROUTER: Tentativa de login para o usuário: {form_data.username}")
    user = await auth_service.authenticate_user(db=db, username=form_data.username, password_provided=form_data.password)
    if not user:
        print(f"AUTH_ROUTER: Falha na autenticação para o usuário: {form_data.username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Nome de usuário ou senha incorretos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_payload = {"sub": user.username}
    access_token = auth_service.create_access_token(data=access_token_payload)
    print(f"AUTH_ROUTER: Token gerado com sucesso para o usuário: {form_data.username}")
    return {"access_token": access_token, "token_type": "bearer"}


@router.post(
    "/register",
    response_model=user_schemas.User,
    status_code=status.HTTP_201_CREATED,
    summary="Registra um novo usuário.",
    description="Cria uma nova conta de usuário com nome de usuário, nome completo e senha, enviados como form data."
)
async def register_new_user(
    db: Session = Depends(get_db),
    username: str = Form(..., min_length=3, max_length=50, description="Nome de usuário único para login."),
    password: str = Form(..., min_length=6, description="Senha do usuário."),
    full_name: Optional[str] = Form(None, max_length=100, description="Nome completo do usuário (opcional).")
):
    print(f"AUTH_ROUTER: Tentativa de registro para o usuário: {username}")
    
    db_user_by_username = crud_user.get_user_by_username(db, username=username)
    if db_user_by_username:
        print(f"AUTH_ROUTER: Username '{username}' já registrado.")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username já registrado. Por favor, escolha outro."
        )
        
    user_in_schema = user_schemas.UserCreate(
        username=username,
        password=password,
        full_name=full_name
    )
    
    created_user = crud_user.create_user(db=db, user_create_schema=user_in_schema)
    print(f"AUTH_ROUTER: Usuário '{created_user.username}' registrado com sucesso com ID: {created_user.id}")
    
    return created_user