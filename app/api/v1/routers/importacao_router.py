from fastapi import APIRouter, Query, HTTPException, Depends
from typing import List, Optional
from sqlalchemy.orm import Session
from app.schemas.importacao_schemas import ImportacaoResponse, ImportacaoItemData
from app.services.auth_service import get_current_user
from app.models.user import User as UserModel
from app.models.importacao_model import Importacao as ImportacaoModel
from app.db.session import get_db
from app.crud import crud_importacao

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

    print(f"ROUTER (Importação DB): Usuário '{current_user_username}' solicitando tipo '{tipo_importacao_key}', ano: {ano}")
    
    db_items: List[ImportacaoModel] = crud_importacao.get_importacao_by_year_and_type(
        db=db, year=ano, tipo_importacao=tipo_importacao_key
    )
    print(f"ROUTER (Importação DB): CRUD retornou {len(db_items)} itens do banco para '{tipo_importacao_key}'.")

    if not db_items:
        print(f"ROUTER (Importação DB): Nenhum dado encontrado no banco para ano {ano}, tipo '{tipo_importacao_key}'.")
        return ImportacaoResponse(
            ano_referencia=ano,
            tipo_importacao=tipo_importacao_key,
            dados=[],
            total_geral_kg=0.0,
            total_geral_usd=0.0
        )

    dados_api: List[ImportacaoItemData] = [ImportacaoItemData.model_validate(item) for item in db_items]
    
    total_kg: float = sum(item.quantidade_kg for item in dados_api if item.quantidade_kg is not None)
    total_usd: float = sum(item.valor_usd for item in dados_api if item.valor_usd is not None)
    print(f"ROUTER (Importação DB): Totais para '{tipo_importacao_key}': KG={total_kg}, USD={total_usd}")

    return ImportacaoResponse(
        ano_referencia=ano,
        tipo_importacao=tipo_importacao_key,
        dados=dados_api,
        total_geral_kg=round(total_kg, 2),
        total_geral_usd=round(total_usd, 2)
    )

@router.get("/vinhos-mesa/", response_model=ImportacaoResponse, summary="Importação de Vinhos de Mesa (do DB, Requer Autenticação)", tags=["Importação"])
async def get_importacao_vinhos_mesa(ano: int = Query(..., ge=1970, le=2023), db: Session = Depends(get_db), current_user: UserModel = Depends(get_current_user)):
    return await _get_importacao_data_for_endpoint(db, ano, "vinhos-mesa", current_user.username)

@router.get("/espumantes/", response_model=ImportacaoResponse, summary="Importação de Espumantes (do DB, Requer Autenticação)", tags=["Importação"])
async def get_importacao_espumantes(ano: int = Query(..., ge=1970, le=2023), db: Session = Depends(get_db), current_user: UserModel = Depends(get_current_user)):
    return await _get_importacao_data_for_endpoint(db, ano, "espumantes", current_user.username)

@router.get("/uvas-frescas/", response_model=ImportacaoResponse, summary="Importação de Uvas Frescas (do DB, Requer Autenticação)", tags=["Importação"])
async def get_importacao_uvas_frescas(ano: int = Query(..., ge=1970, le=2023), db: Session = Depends(get_db), current_user: UserModel = Depends(get_current_user)):
    return await _get_importacao_data_for_endpoint(db, ano, "uvas-frescas", current_user.username)

@router.get("/uvas-passas/", response_model=ImportacaoResponse, summary="Importação de Uvas Passas (do DB, Requer Autenticação)", tags=["Importação"])
async def get_importacao_uvas_passas(ano: int = Query(..., ge=1970, le=2023), db: Session = Depends(get_db), current_user: UserModel = Depends(get_current_user)):
    return await _get_importacao_data_for_endpoint(db, ano, "uvas-passas", current_user.username)

@router.get("/suco-uva/", response_model=ImportacaoResponse, summary="Importação de Suco de Uva (do DB, Requer Autenticação)", tags=["Importação"])
async def get_importacao_suco_uva(ano: int = Query(..., ge=1970, le=2023), db: Session = Depends(get_db), current_user: UserModel = Depends(get_current_user)):
    return await _get_importacao_data_for_endpoint(db, ano, "suco-uva", current_user.username)