from fastapi import APIRouter, Query, HTTPException, Depends
from typing import List, Optional
from sqlalchemy.orm import Session
from app.schemas.importacao_schemas import ImportacaoResponse, ImportacaoItemData
from app.services.embrapa_scraper import fetch_importacao_data
from app.services.auth_service import get_current_user
from app.models.user import User as UserModel
from app.db.session import get_db
router = APIRouter()

TIPO_IMPORTACAO_ENDPOINT_MAP = {
    "vinhos-mesa": "vinhos_mesa",
    "espumantes": "espumantes",
    "uvas-frescas": "uvas_frescas",
    "uvas-passas": "uvas_passas",
    "suco-uva": "suco_uva",
}


async def _get_importacao_data_for_endpoint(
    db: Session,
    ano: int, 
    tipo_importacao_path: str, 
    current_user_username: str
):
    tipo_importacao_key = TIPO_IMPORTACAO_ENDPOINT_MAP.get(tipo_importacao_path)
    if not tipo_importacao_key:
        raise HTTPException(status_code=500, detail="Configuração interna inválida para tipo de importação.")

    print(f"ROUTER (Importação): Usuário '{current_user_username}' acessando tipo '{tipo_importacao_key}', ano: {ano}")
    try:
        dados_api: List[ImportacaoItemData] = await fetch_importacao_data(
            db=db,
            year=ano,
            tipo_importacao_key=tipo_importacao_key
        )
        print(f"ROUTER (Importação): Serviço scraper/DB retornou {len(dados_api)} itens processados para '{tipo_importacao_key}'.")

        if not dados_api:
            return ImportacaoResponse(
                ano_referencia=ano,
                tipo_importacao=tipo_importacao_key,
                dados=[],
                total_geral_kg=0.0,
                total_geral_usd=0.0
            )

        total_kg: float = 0.0
        total_usd: float = 0.0
        for item_data in dados_api:
            if item_data.quantidade_kg is not None:
                total_kg += item_data.quantidade_kg
            if item_data.valor_usd is not None:
                total_usd += item_data.valor_usd
        
        print(f"ROUTER (Importação): Totais para '{tipo_importacao_key}': KG={total_kg}, USD={total_usd}")

        return ImportacaoResponse(
            ano_referencia=ano,
            tipo_importacao=tipo_importacao_key,
            dados=dados_api,
            total_geral_kg=round(total_kg, 2),
            total_geral_usd=round(total_usd, 2)
        )
    except Exception as e:
        import traceback
        print(f"ROUTER ERROR (Importação): Erro inesperado para tipo '{tipo_importacao_key}', ano {ano}: {str(e)}\n{traceback.format_exc()}")
        raise HTTPException(
            status_code=500,
            detail=f"Erro interno ao processar dados de importação ({tipo_importacao_key}). Detalhe: {str(e)}"
        )

@router.get("/vinhos-mesa/", response_model=ImportacaoResponse, summary="Importação de Vinhos de Mesa (Requer Autenticação)", tags=["Importação"])
async def get_importacao_vinhos_mesa(
    ano: int = Query(..., ge=1970, le=2023, description="Ano (1970-2023)"),
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    return await _get_importacao_data_for_endpoint(db, ano, "vinhos-mesa", current_user.username)

@router.get("/espumantes/", response_model=ImportacaoResponse, summary="Importação de Espumantes (Requer Autenticação)", tags=["Importação"])
async def get_importacao_espumantes(ano: int = Query(..., ge=1970, le=2023), db: Session = Depends(get_db), current_user: UserModel = Depends(get_current_user)):
    return await _get_importacao_data_for_endpoint(db, ano, "espumantes", current_user.username)

@router.get("/uvas-frescas/", response_model=ImportacaoResponse, summary="Importação de Uvas Frescas (Requer Autenticação)", tags=["Importação"])
async def get_importacao_uvas_frescas(ano: int = Query(..., ge=1970, le=2023), db: Session = Depends(get_db), current_user: UserModel = Depends(get_current_user)):
    return await _get_importacao_data_for_endpoint(db, ano, "uvas-frescas", current_user.username)

@router.get("/uvas-passas/", response_model=ImportacaoResponse, summary="Importação de Uvas Passas (Requer Autenticação)", tags=["Importação"])
async def get_importacao_uvas_passas(ano: int = Query(..., ge=1970, le=2023), db: Session = Depends(get_db), current_user: UserModel = Depends(get_current_user)):
    return await _get_importacao_data_for_endpoint(db, ano, "uvas-passas", current_user.username)

@router.get("/suco-uva/", response_model=ImportacaoResponse, summary="Importação de Suco de Uva (Requer Autenticação)", tags=["Importação"])
async def get_importacao_suco_uva(ano: int = Query(..., ge=1970, le=2023), db: Session = Depends(get_db), current_user: UserModel = Depends(get_current_user)):
    return await _get_importacao_data_for_endpoint(db, ano, "suco-uva", current_user.username)