from fastapi import APIRouter, Query, HTTPException, Depends
from typing import List, Optional

from app.schemas.processamento_schemas import (
    ProcessamentoResponse,
    ProcessamentoItemData,
    ProcessamentoScrapedItem
)
from app.services.embrapa_scraper import fetch_processamento_data
from app.services.auth_service import get_current_user
from app.models.user import User as UserModel 

router = APIRouter()

TIPO_PROCESSAMENTO_ENDPOINT_MAP = {
    "viniferas": "viniferas",
    "americanas-hibridas": "americanas_hibridas",
    "uvas-mesa": "uvas_mesa",
    "sem-classificacao": "sem_classificacao",
}

def _convert_processamento_scraped_to_item_data(
    scraped_items: List[ProcessamentoScrapedItem],
    ano: int,
    tipo_processamento_key: str
) -> List[ProcessamentoItemData]:
    processed_items: List[ProcessamentoItemData] = []
    for scraped_item in scraped_items:
        quantidade_kg: Optional[float] = None
        try:
            if scraped_item.quantidade_str == "-":
                quantidade_kg = None
            elif scraped_item.quantidade_str.strip():
                quantidade_kg = float(scraped_item.quantidade_str.replace(',', '.'))
            else:
                quantidade_kg = None
        except ValueError:
            print(f"ROUTER WARNING (Processamento): Não foi possível converter quantidade '{scraped_item.quantidade_str}' para float para cultivar '{scraped_item.cultivar}'. Será None.")
            quantidade_kg = None
        
        processed_items.append(
            ProcessamentoItemData(
                cultivar=scraped_item.cultivar,
                quantidade_kg=quantidade_kg,
                ano=ano,
                tipo_processamento=scraped_item.tipo_processamento
            )
        )
    return processed_items

async def _get_processamento_data_for_endpoint(ano: int, tipo_processamento_path: str, current_user_username: str):
    tipo_processamento_key = TIPO_PROCESSAMENTO_ENDPOINT_MAP.get(tipo_processamento_path)
    if not tipo_processamento_key:
        raise HTTPException(status_code=500, detail="Configuração interna inválida para tipo de processamento.")

    print(f"ROUTER (Processamento): Usuário '{current_user_username}' acessando tipo '{tipo_processamento_key}', ano: {ano}")
    try:
        scraped_items: List[ProcessamentoScrapedItem] = await fetch_processamento_data(
            year=ano,
            tipo_processamento_key=tipo_processamento_key
        )
        print(f"ROUTER (Processamento): Scraper retornou {len(scraped_items)} itens para '{tipo_processamento_key}'.")

        if not scraped_items:
            return ProcessamentoResponse(
                ano_referencia=ano,
                tipo_processamento=tipo_processamento_key,
                dados=[],
                total_geral_kg=0.0
            )

        dados_api: List[ProcessamentoItemData] = _convert_processamento_scraped_to_item_data(
            scraped_items, ano, tipo_processamento_key
        )
        print(f"ROUTER (Processamento): {len(dados_api)} itens processados para '{tipo_processamento_key}'.")

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
        print(f"ROUTER ERROR (Processamento): Erro inesperado para tipo '{tipo_processamento_key}', ano {ano}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Erro interno ao processar dados de processamento ({tipo_processamento_key}). Detalhe: {str(e)}"
        )


@router.get(
    "/viniferas/",
    response_model=ProcessamentoResponse,
    summary="Dados de processamento de uvas Viníferas por ano (Requer Autenticação).",
    tags=["Processamento"]
)
async def get_processamento_viniferas(
    ano: int = Query(..., ge=1970, le=2023, description="Ano para consulta (1970-2023)"),
    current_user: UserModel = Depends(get_current_user)
):
    return await _get_processamento_data_for_endpoint(ano, "viniferas", current_user.username)

@router.get(
    "/americanas-hibridas/",
    response_model=ProcessamentoResponse,
    summary="Dados de processamento de uvas Americanas e Híbridas por ano (Requer Autenticação).",
    tags=["Processamento"]
)
async def get_processamento_americanas_hibridas(
    ano: int = Query(..., ge=1970, le=2023, description="Ano para consulta (1970-2023)"),
    current_user: UserModel = Depends(get_current_user)
):
    return await _get_processamento_data_for_endpoint(ano, "americanas-hibridas", current_user.username)

@router.get(
    "/uvas-mesa/",
    response_model=ProcessamentoResponse,
    summary="Dados de processamento de Uvas de Mesa por ano (Requer Autenticação).",
    tags=["Processamento"]
)
async def get_processamento_uvas_mesa(
    ano: int = Query(..., ge=1970, le=2023, description="Ano para consulta (1970-2023)"),
    current_user: UserModel = Depends(get_current_user)
):
    return await _get_processamento_data_for_endpoint(ano, "uvas-mesa", current_user.username)

@router.get(
    "/sem-classificacao/",
    response_model=ProcessamentoResponse,
    summary="Dados de processamento de uvas Sem Classificação por ano (Requer Autenticação).",
    tags=["Processamento"]
)
async def get_processamento_sem_classificacao(
    ano: int = Query(..., ge=1970, le=2023, description="Ano para consulta (1970-2023)"),
    current_user: UserModel = Depends(get_current_user)
):
    return await _get_processamento_data_for_endpoint(ano, "sem-classificacao", current_user.username)