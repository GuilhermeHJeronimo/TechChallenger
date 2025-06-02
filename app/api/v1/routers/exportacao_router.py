from fastapi import APIRouter, Query, HTTPException, Depends
from typing import List, Optional

from app.schemas.exportacao_schemas import (
    ExportacaoResponse,
    ExportacaoItemData,
    ExportacaoScrapedItem
)
from app.services.embrapa_scraper import fetch_exportacao_data
from app.services.auth_service import get_current_user
from app.models.user import User as UserModel

router = APIRouter()

TIPO_EXPORTACAO_ENDPOINT_MAP = {
    "vinhos-mesa": "vinhos_mesa",
    "espumantes": "espumantes",
    "uvas-frescas": "uvas_frescas",
    "suco-uva": "suco_uva",
}

def _convert_exportacao_scraped_to_item_data(
    scraped_items: List[ExportacaoScrapedItem],
    ano: int,
    tipo_exportacao_key: str
) -> List[ExportacaoItemData]:
    processed_items: List[ExportacaoItemData] = []
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
            print(f"ROUTER WARNING (Exportação): Não foi possível converter quantidade_kg '{scraped_item.quantidade_str}' para float para o país '{scraped_item.pais}'. Será None.")
            quantidade_kg = None
        
        try:
            if scraped_item.valor_str == "-":
                valor_usd = None
            elif scraped_item.valor_str.strip():
                valor_usd = float(scraped_item.valor_str.replace(',', '.'))
            else:
                valor_usd = None
        except ValueError:
            print(f"ROUTER WARNING (Exportação): Não foi possível converter valor_usd '{scraped_item.valor_str}' para float para o país '{scraped_item.pais}'. Será None.")
            valor_usd = None
        
        processed_items.append(
            ExportacaoItemData(
                pais=scraped_item.pais,
                quantidade_kg=quantidade_kg,
                valor_usd=valor_usd,
                ano=ano,
                tipo_exportacao=scraped_item.tipo_exportacao
            )
        )
    return processed_items

async def _get_exportacao_data_for_endpoint(ano: int, tipo_exportacao_path: str, current_user_username: str):
    tipo_exportacao_key = TIPO_EXPORTACAO_ENDPOINT_MAP.get(tipo_exportacao_path)
    if not tipo_exportacao_key:
        raise HTTPException(status_code=500, detail="Configuração interna inválida para tipo de exportação.")

    print(f"ROUTER (Exportação): Usuário '{current_user_username}' acessando tipo '{tipo_exportacao_key}', ano: {ano}")
    try:
        scraped_items: List[ExportacaoScrapedItem] = await fetch_exportacao_data(
            year=ano,
            tipo_exportacao_key=tipo_exportacao_key
        )
        print(f"ROUTER (Exportação): Scraper retornou {len(scraped_items)} itens para '{tipo_exportacao_key}'.")

        if not scraped_items:
            return ExportacaoResponse(
                ano_referencia=ano,
                tipo_exportacao=tipo_exportacao_key,
                dados=[],
                total_geral_kg=0.0,
                total_geral_usd=0.0
            )

        dados_api: List[ExportacaoItemData] = _convert_exportacao_scraped_to_item_data(
            scraped_items, ano, tipo_exportacao_key
        )
        print(f"ROUTER (Exportação): {len(dados_api)} itens processados para '{tipo_exportacao_key}'.")

        total_kg: float = 0.0
        total_usd: float = 0.0
        for item_data in dados_api:
            if item_data.quantidade_kg is not None:
                total_kg += item_data.quantidade_kg
            if item_data.valor_usd is not None:
                total_usd += item_data.valor_usd
        
        print(f"ROUTER (Exportação): Totais para '{tipo_exportacao_key}': KG={total_kg}, USD={total_usd}")

        return ExportacaoResponse(
            ano_referencia=ano,
            tipo_exportacao=tipo_exportacao_key,
            dados=dados_api,
            total_geral_kg=round(total_kg, 2),
            total_geral_usd=round(total_usd, 2)
        )
    except Exception as e:
        print(f"ROUTER ERROR (Exportação): Erro inesperado para tipo '{tipo_exportacao_key}', ano {ano}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Erro interno ao processar dados de exportação ({tipo_exportacao_key}). Detalhe: {str(e)}"
        )

@router.get(
    "/vinhos-mesa/",
    response_model=ExportacaoResponse,
    summary="Dados de exportação de Vinhos de Mesa por ano (Requer Autenticação).",
    tags=["Exportação"]
)
async def get_exportacao_vinhos_mesa(
    ano: int = Query(..., ge=1970, le=2023, description="Ano para consulta (1970-2023)"),
    current_user: UserModel = Depends(get_current_user)
):
    return await _get_exportacao_data_for_endpoint(ano, "vinhos-mesa", current_user.username)

@router.get(
    "/espumantes/",
    response_model=ExportacaoResponse,
    summary="Dados de exportação de Espumantes por ano (Requer Autenticação).",
    tags=["Exportação"]
)
async def get_exportacao_espumantes(
    ano: int = Query(..., ge=1970, le=2023, description="Ano para consulta (1970-2023)"),
    current_user: UserModel = Depends(get_current_user)
):
    return await _get_exportacao_data_for_endpoint(ano, "espumantes", current_user.username)

@router.get(
    "/uvas-frescas/",
    response_model=ExportacaoResponse,
    summary="Dados de exportação de Uvas Frescas por ano (Requer Autenticação).",
    tags=["Exportação"]
)
async def get_exportacao_uvas_frescas(
    ano: int = Query(..., ge=1970, le=2023, description="Ano para consulta (1970-2023)"),
    current_user: UserModel = Depends(get_current_user)
):
    return await _get_exportacao_data_for_endpoint(ano, "uvas-frescas", current_user.username)

@router.get(
    "/suco-uva/",
    response_model=ExportacaoResponse,
    summary="Dados de exportação de Suco de Uva por ano (Requer Autenticação).",
    tags=["Exportação"]
)
async def get_exportacao_suco_uva(
    ano: int = Query(..., ge=1970, le=2023, description="Ano para consulta (1970-2023)"),
    current_user: UserModel = Depends(get_current_user)
):
    return await _get_exportacao_data_for_endpoint(ano, "suco-uva", current_user.username)