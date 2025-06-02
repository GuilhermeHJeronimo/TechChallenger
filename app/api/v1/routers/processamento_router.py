from fastapi import APIRouter, Query, HTTPException, Depends
from typing import List, Optional
from sqlalchemy.orm import Session
from app.schemas.processamento_schemas import ProcessamentoResponse, ProcessamentoItemData
from app.services.embrapa_scraper import fetch_processamento_data
from app.services.auth_service import get_current_user
from app.models.user import User as UserModel
from app.db.session import get_db

router = APIRouter()

TIPO_PROCESSAMENTO_ENDPOINT_MAP = {
    "viniferas": "viniferas",
    "americanas-hibridas": "americanas_hibridas",
    "uvas-mesa": "uvas_mesa",
    "sem-classificacao": "sem_classificacao",
}

async def _get_processamento_data_for_endpoint(
    db: Session, # Adicionado db
    ano: int, 
    tipo_processamento_path: str, 
    current_user_username: str
):
    tipo_processamento_key = TIPO_PROCESSAMENTO_ENDPOINT_MAP.get(tipo_processamento_path)
    if not tipo_processamento_key:
        raise HTTPException(status_code=500, detail="Configuração interna inválida para tipo de processamento.")

    print(f"ROUTER (Processamento): Usuário '{current_user_username}' acessando tipo '{tipo_processamento_key}', ano: {ano}")
    try:
        dados_api: List[ProcessamentoItemData] = await fetch_processamento_data(
            db=db, # Passando db
            year=ano,
            tipo_processamento_key=tipo_processamento_key
        )
        print(f"ROUTER (Processamento): Serviço scraper/DB retornou {len(dados_api)} itens processados para '{tipo_processamento_key}'.")

        if not dados_api:
            return ProcessamentoResponse(
                ano_referencia=ano,
                tipo_processamento=tipo_processamento_key,
                dados=[],
                total_geral_kg=0.0
            )

        total_kg: float = 0.0
        for item_data in dados_api:
            if item_data.quantidade_kg is not None:
                total_kg += item_data.quantidade_kg
        
        print(f"ROUTER (Processamento): Total KG para '{tipo_processamento_key}': {total_kg}")

        return ProcessamentoResponse(
            ano_referencia=ano,
            tipo_processamento=tipo_processamento_key,
            dados=dados_api,
            total_geral_kg=round(total_kg, 2)
        )
    except Exception as e:
        import traceback
        print(f"ROUTER ERROR (Processamento): Erro inesperado para tipo '{tipo_processamento_key}', ano {ano}: {str(e)}\n{traceback.format_exc()}")
        raise HTTPException(
            status_code=500,
            detail=f"Erro interno ao processar dados de processamento ({tipo_processamento_key}). Detalhe: {str(e)}"
        )

@router.get("/viniferas/", response_model=ProcessamentoResponse, summary="Processamento de Viníferas (Requer Autenticação)", tags=["Processamento"])
async def get_processamento_viniferas(
    ano: int = Query(..., ge=1970, le=2023, description="Ano (1970-2023)"),
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    return await _get_processamento_data_for_endpoint(db, ano, "viniferas", current_user.username)

@router.get("/americanas-hibridas/", response_model=ProcessamentoResponse, summary="Processamento de Americanas e Híbridas (Requer Autenticação)", tags=["Processamento"])
async def get_processamento_americanas_hibridas(
    ano: int = Query(..., ge=1970, le=2023, description="Ano (1970-2023)"),
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    return await _get_processamento_data_for_endpoint(db, ano, "americanas-hibridas", current_user.username)

@router.get("/uvas-mesa/", response_model=ProcessamentoResponse, summary="Processamento de Uvas de Mesa (Requer Autenticação)", tags=["Processamento"])
async def get_processamento_uvas_mesa(
    ano: int = Query(..., ge=1970, le=2023, description="Ano (1970-2023)"),
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    return await _get_processamento_data_for_endpoint(db, ano, "uvas-mesa", current_user.username)

@router.get("/sem-classificacao/", response_model=ProcessamentoResponse, summary="Processamento de Uvas Sem Classificação (Requer Autenticação)", tags=["Processamento"])
async def get_processamento_sem_classificacao(
    ano: int = Query(..., ge=1970, le=2023, description="Ano (1970-2023)"),
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    return await _get_processamento_data_for_endpoint(db, ano, "sem-classificacao", current_user.username)