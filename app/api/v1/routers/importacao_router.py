from fastapi import APIRouter, Query, HTTPException, Depends
from typing import List, Optional

from app.schemas.importacao_schemas import (
    ImportacaoResponse,
    ImportacaoItemData,
    ImportacaoScrapedItem
)
from app.services.embrapa_scraper import fetch_importacao_data
from app.services.auth_service import get_current_user, UserInDB

router = APIRouter()

TIPO_IMPORTACAO_ENDPOINT_MAP = {
    "vinhos-mesa": "vinhos_mesa",
    "espumantes": "espumantes",
    "uvas-frescas": "uvas_frescas",
    "uvas-passas": "uvas_passas",
    "suco-uva": "suco_uva",
}

def _convert_importacao_scraped_to_item_data(
    scraped_items: List[ImportacaoScrapedItem],
    ano: int,
    tipo_importacao_key: str
) -> List[ImportacaoItemData]:
    processed_items: List[ImportacaoItemData] = []
    for scraped_item in scraped_items:
        quantidade_kg: Optional[float] = None
        valor_usd: Optional[float] = None
        try:
            if scraped_item.quantidade_str == "-":
                quantidade_kg = None
            elif scraped_item.quantidade_str.strip():
                quantidade_kg = float(scraped_item.quantidade_str.replace(',', '.'))
            else:
                quantidade_kg = None
        except ValueError:
            print(f"ROUTER WARNING (Importação): Não foi possível converter quantidade_kg '{scraped_item.quantidade_str}' para float para o país '{scraped_item.pais}'. Será None.")
            quantidade_kg = None
        
        try:
            if scraped_item.valor_str == "-":
                valor_usd = None
            elif scraped_item.valor_str.strip():
                valor_usd = float(scraped_item.valor_str.replace(',', '.'))
            else:
                valor_usd = None
        except ValueError:
            print(f"ROUTER WARNING (Importação): Não foi possível converter valor_usd '{scraped_item.valor_str}' para float para o país '{scraped_item.pais}'. Será None.")
            valor_usd = None
        
        processed_items.append(
            ImportacaoItemData(
                pais=scraped_item.pais,
                quantidade_kg=quantidade_kg,
                valor_usd=valor_usd,
                ano=ano,
                tipo_importacao=scraped_item.tipo_importacao
            )
        )
    return processed_items

async def _get_importacao_data_for_endpoint(ano: int, tipo_importacao_path: str, current_user_username: str):
    tipo_importacao_key = TIPO_IMPORTACAO_ENDPOINT_MAP.get(tipo_importacao_path)
    if not tipo_importacao_key:
        raise HTTPException(status_code=500, detail="Configuração interna inválida para tipo de importação.")

    print(f"ROUTER (Importação): Usuário '{current_user_username}' acessando tipo '{tipo_importacao_key}', ano: {ano}")
    try:
        scraped_items: List[ImportacaoScrapedItem] = await fetch_importacao_data(
            year=ano,
            tipo_importacao_key=tipo_importacao_key
        )
        print(f"ROUTER (Importação): Scraper retornou {len(scraped_items)} itens para '{tipo_importacao_key}'.")

        if not scraped_items:
            return ImportacaoResponse(
                ano_referencia=ano,
                tipo_importacao=tipo_importacao_key,
                dados=[],
                total_geral_kg=0.0,
                total_geral_usd=0.0
            )

        dados_api: List[ImportacaoItemData] = _convert_importacao_scraped_to_item_data(
            scraped_items, ano, tipo_importacao_key
        )
        print(f"ROUTER (Importação): {len(dados_api)} itens processados para '{tipo_importacao_key}'.")

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
        print(f"ROUTER ERROR (Importação): Erro inesperado para tipo '{tipo_importacao_key}', ano {ano}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Erro interno ao processar dados de importação ({tipo_importacao_key}). Detalhe: {str(e)}"
        )

@router.get(
    "/vinhos-mesa/",
    response_model=ImportacaoResponse,
    summary="Dados de importação de Vinhos de Mesa por ano (Requer Autenticação).",
    tags=["Importação"]
)
async def get_importacao_vinhos_mesa(
    ano: int = Query(..., ge=1970, le=2023, description="Ano para consulta (1970-2023)"),
    current_user: UserInDB = Depends(get_current_user)
):
    return await _get_importacao_data_for_endpoint(ano, "vinhos-mesa", current_user.username)

@router.get(
    "/espumantes/",
    response_model=ImportacaoResponse,
    summary="Dados de importação de Espumantes por ano (Requer Autenticação).",
    tags=["Importação"]
)
async def get_importacao_espumantes(
    ano: int = Query(..., ge=1970, le=2023, description="Ano para consulta (1970-2023)"),
    current_user: UserInDB = Depends(get_current_user)
):
    return await _get_importacao_data_for_endpoint(ano, "espumantes", current_user.username)

@router.get(
    "/uvas-frescas/",
    response_model=ImportacaoResponse,
    summary="Dados de importação de Uvas Frescas por ano (Requer Autenticação).",
    tags=["Importação"]
)
async def get_importacao_uvas_frescas(
    ano: int = Query(..., ge=1970, le=2023, description="Ano para consulta (1970-2023)"),
    current_user: UserInDB = Depends(get_current_user)
):
    return await _get_importacao_data_for_endpoint(ano, "uvas-frescas", current_user.username)

@router.get(
    "/uvas-passas/",
    response_model=ImportacaoResponse,
    summary="Dados de importação de Uvas Passas por ano (Requer Autenticação).",
    tags=["Importação"]
)
async def get_importacao_uvas_passas(
    ano: int = Query(..., ge=1970, le=2023, description="Ano para consulta (1970-2023)"),
    current_user: UserInDB = Depends(get_current_user)
):
    return await _get_importacao_data_for_endpoint(ano, "uvas-passas", current_user.username)

@router.get(
    "/suco-uva/",
    response_model=ImportacaoResponse,
    summary="Dados de importação de Suco de Uva por ano (Requer Autenticação).",
    tags=["Importação"]
)
async def get_importacao_suco_uva(
    ano: int = Query(..., ge=1970, le=2023, description="Ano para consulta (1970-2023)"),
    current_user: UserInDB = Depends(get_current_user)
):
    return await _get_importacao_data_for_endpoint(ano, "suco-uva", current_user.username)