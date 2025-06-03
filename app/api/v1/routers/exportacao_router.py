from fastapi import APIRouter, Query, HTTPException, Depends
from typing import List, Optional
from sqlalchemy.orm import Session
from app.schemas.exportacao_schemas import ExportacaoResponse, ExportacaoItemData
from app.services.auth_service import get_current_user
from app.models.user import User as UserModel
from app.models.exportacao_model import Exportacao as ExportacaoModel
from app.db.session import get_db
from app.crud import crud_exportacao

router = APIRouter()

TIPO_EXPORTACAO_ENDPOINT_MAP = {
    "vinhos-mesa": "vinhos_mesa",
    "espumantes": "espumantes",
    "uvas-frescas": "uvas_frescas",
    "suco-uva": "suco_uva",
}

async def _get_exportacao_data_for_endpoint(
    db: Session, 
    ano: int, 
    tipo_exportacao_path: str, 
    current_user_username: str
):
    tipo_exportacao_key = TIPO_EXPORTACAO_ENDPOINT_MAP.get(tipo_exportacao_path)
    if not tipo_exportacao_key:
        raise HTTPException(status_code=500, detail="Configuração interna inválida para tipo de exportação.")

    print(f"ROUTER (Exportação DB): Usuário '{current_user_username}' solicitando tipo '{tipo_exportacao_key}', ano: {ano}")
    
    db_items: List[ExportacaoModel] = crud_exportacao.get_exportacao_by_year_and_type(
        db=db, year=ano, tipo_exportacao=tipo_exportacao_key
    )
    print(f"ROUTER (Exportação DB): CRUD retornou {len(db_items)} itens do banco para '{tipo_exportacao_key}'.")

    if not db_items:
        print(f"ROUTER (Exportação DB): Nenhum dado encontrado no banco para ano {ano}, tipo '{tipo_exportacao_key}'.")
        return ExportacaoResponse(
            ano_referencia=ano,
            tipo_exportacao=tipo_exportacao_key,
            dados=[],
            total_geral_kg=0.0,
            total_geral_usd=0.0
        )

    dados_api: List[ExportacaoItemData] = [ExportacaoItemData.model_validate(item) for item in db_items]
        
    total_kg: float = sum(item.quantidade_kg for item in dados_api if item.quantidade_kg is not None)
    total_usd: float = sum(item.valor_usd for item in dados_api if item.valor_usd is not None)
    print(f"ROUTER (Exportação DB): Totais para '{tipo_exportacao_key}': KG={total_kg}, USD={total_usd}")

    return ExportacaoResponse(
        ano_referencia=ano,
        tipo_exportacao=tipo_exportacao_key,
        dados=dados_api,
        total_geral_kg=round(total_kg, 2),
        total_geral_usd=round(total_usd, 2)
    )

@router.get("/vinhos-mesa/", response_model=ExportacaoResponse, summary="Exportação de Vinhos de Mesa (do DB, Requer Autenticação)", tags=["Exportação"])
async def get_exportacao_vinhos_mesa(ano: int = Query(..., ge=1970, le=2023), db: Session = Depends(get_db), current_user: UserModel = Depends(get_current_user)):
    return await _get_exportacao_data_for_endpoint(db, ano, "vinhos-mesa", current_user.username)

@router.get("/espumantes/", response_model=ExportacaoResponse, summary="Exportação de Espumantes (do DB, Requer Autenticação)", tags=["Exportação"])
async def get_exportacao_espumantes(ano: int = Query(..., ge=1970, le=2023), db: Session = Depends(get_db), current_user: UserModel = Depends(get_current_user)):
    return await _get_exportacao_data_for_endpoint(db, ano, "espumantes", current_user.username)

@router.get("/uvas-frescas/", response_model=ExportacaoResponse, summary="Exportação de Uvas Frescas (do DB, Requer Autenticação)", tags=["Exportação"])
async def get_exportacao_uvas_frescas(ano: int = Query(..., ge=1970, le=2023), db: Session = Depends(get_db), current_user: UserModel = Depends(get_current_user)):
    return await _get_exportacao_data_for_endpoint(db, ano, "uvas-frescas", current_user.username)

@router.get("/suco-uva/", response_model=ExportacaoResponse, summary="Exportação de Suco de Uva (do DB, Requer Autenticação)", tags=["Exportação"])
async def get_exportacao_suco_uva(ano: int = Query(..., ge=1970, le=2023), db: Session = Depends(get_db), current_user: UserModel = Depends(get_current_user)):
    return await _get_exportacao_data_for_endpoint(db, ano, "suco-uva", current_user.username)