from fastapi import APIRouter, Query, HTTPException, Depends
from typing import List, Optional
from sqlalchemy.orm import Session
from app.schemas.processamento_schemas import ProcessamentoResponse, ProcessamentoItemData
from app.services.auth_service import get_current_user
from app.models.user import User as UserModel
from app.models.processamento_model import Processamento as ProcessamentoModel
from app.db.session import get_db
from app.crud import crud_processamento

router = APIRouter()

TIPO_PROCESSAMENTO_ENDPOINT_MAP = {
    "viniferas": "viniferas",
    "americanas-hibridas": "americanas_hibridas",
    "uvas-mesa": "uvas_mesa",
    "sem-classificacao": "sem_classificacao",
}

async def _get_processamento_data_for_endpoint(
    db: Session, 
    ano: int, 
    tipo_processamento_path: str, 
    current_user_username: str
):
    tipo_processamento_key = TIPO_PROCESSAMENTO_ENDPOINT_MAP.get(tipo_processamento_path)
    if not tipo_processamento_key:
        raise HTTPException(status_code=500, detail="Configuração interna inválida para tipo de processamento.")

    print(f"ROUTER (Processamento DB): Usuário '{current_user_username}' solicitando tipo '{tipo_processamento_key}', ano: {ano}")
    
    db_items: List[ProcessamentoModel] = crud_processamento.get_processamento_by_year_and_type(
        db=db, year=ano, tipo_processamento=tipo_processamento_key
    )
    print(f"ROUTER (Processamento DB): CRUD retornou {len(db_items)} itens do banco para '{tipo_processamento_key}'.")

    if not db_items:
        print(f"ROUTER (Processamento DB): Nenhum dado encontrado no banco para ano {ano}, tipo '{tipo_processamento_key}'.")
        return ProcessamentoResponse(
            ano_referencia=ano,
            tipo_processamento=tipo_processamento_key,
            dados=[],
            total_geral_kg=0.0
        )

    dados_api: List[ProcessamentoItemData] = [ProcessamentoItemData.model_validate(item) for item in db_items]
    
    total_kg: float = sum(item.quantidade_kg for item in dados_api if item.quantidade_kg is not None)
    print(f"ROUTER (Processamento DB): Total KG para '{tipo_processamento_key}': {total_kg}")

    return ProcessamentoResponse(
        ano_referencia=ano,
        tipo_processamento=tipo_processamento_key,
        dados=dados_api,
        total_geral_kg=round(total_kg, 2)
    )

@router.get("/viniferas/", response_model=ProcessamentoResponse, summary="Processamento de Viníferas (do DB, Requer Autenticação)", tags=["Processamento"])
async def get_processamento_viniferas(
    ano: int = Query(..., ge=1970, le=2023, description="Ano (1970-2023)"),
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    return await _get_processamento_data_for_endpoint(db, ano, "viniferas", current_user.username)

@router.get("/americanas-hibridas/", response_model=ProcessamentoResponse, summary="Processamento de Americanas/Híbridas (do DB, Requer Autenticação)", tags=["Processamento"])
async def get_processamento_americanas_hibridas(
    ano: int = Query(..., ge=1970, le=2023, description="Ano (1970-2023)"),
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    return await _get_processamento_data_for_endpoint(db, ano, "americanas-hibridas", current_user.username)

@router.get("/uvas-mesa/", response_model=ProcessamentoResponse, summary="Processamento de Uvas de Mesa (do DB, Requer Autenticação)", tags=["Processamento"])
async def get_processamento_uvas_mesa(
    ano: int = Query(..., ge=1970, le=2023, description="Ano (1970-2023)"),
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    return await _get_processamento_data_for_endpoint(db, ano, "uvas-mesa", current_user.username)

@router.get("/sem-classificacao/", response_model=ProcessamentoResponse, summary="Processamento de Uvas Sem Classificação (do DB, Requer Autenticação)", tags=["Processamento"])
async def get_processamento_sem_classificacao(
    ano: int = Query(..., ge=1970, le=2023, description="Ano (1970-2023)"),
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    return await _get_processamento_data_for_endpoint(db, ano, "sem-classificacao", current_user.username)