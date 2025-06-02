from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm 
from app.services import auth_service
from app.schemas import token_schemas

router = APIRouter()

@router.post(
    "/token", 
    response_model=token_schemas.Token,
    summary="Autentica o usuário e retorna um token de acesso.",
    description="Use este endpoint para obter um token JWT fornecendo nome de usuário e senha."
)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends()
):
    print(f"AUTH_ROUTER: Tentativa de login para o usuário: {form_data.username}")
    user = await auth_service.authenticate_user(form_data.username, form_data.password)
    
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
