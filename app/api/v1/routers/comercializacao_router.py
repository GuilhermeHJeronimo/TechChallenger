from fastapi import APIRouter, Query, HTTPException
from typing import List, Optional

from app.schemas.comercializacao_schemas import (
    ComercializacaoResponse,
    ComercializacaoItemData,
    ComercializacaoScrapedItem
)
from app.services.embrapa_scraper import fetch_comercializacao_data

router = APIRouter()

def _convert_comercializacao_scraped_to_item_data(
    scraped_items: List[ComercializacaoScrapedItem],
    ano: int
) -> List[ComercializacaoItemData]:
    processed_items: List[ComercializacaoItemData] = []
    for scraped_item in scraped_items:
        quantidade_litros: Optional[float] = None
        try:
            if scraped_item.quantidade_str == "-":
                quantidade_litros = None
            elif scraped_item.quantidade_str.strip():
                quantidade_litros = float(scraped_item.quantidade_str)
            else:
                quantidade_litros = None
        except ValueError:
            print(f"ROUTER WARNING (Comercialização): Não foi possível converter quantidade '{scraped_item.quantidade_str}' para float para o produto '{scraped_item.produto}'. Será None.")
            quantidade_litros = None
        
        processed_items.append(
            ComercializacaoItemData(
                produto=scraped_item.produto,
                sub_produto=scraped_item.sub_produto,
                quantidade_litros=quantidade_litros,
                ano=ano
            )
        )
    return processed_items

@router.get(
    "/",
    response_model=ComercializacaoResponse,
    summary="Consulta dados de comercialização de produtos vitivinícolas por ano.",
    description="Retorna uma lista de produtos e suas quantidades comercializadas em litros para um determinado ano.",
    tags=["Comercialização"]
)
async def get_comercializacao_por_ano(
    ano: int = Query(
        ...,
        ge=1970,
        le=2023,
        description="Ano para consulta dos dados de comercialização (entre 1970 e 2023)."
    )
):
    try:
        print(f"ROUTER: Recebida requisição para Comercialização do ano: {ano}")
        scraped_items: List[ComercializacaoScrapedItem] = await fetch_comercializacao_data(year=ano)
        print(f"ROUTER: Scraper (Comercialização) retornou {len(scraped_items)} itens raspados.")

        if not scraped_items:
            return ComercializacaoResponse(
                ano_referencia=ano,
                dados=[],
                total_geral_litros=0.0
            )

        dados_api: List[ComercializacaoItemData] = _convert_comercializacao_scraped_to_item_data(
            scraped_items, ano
        )
        print(f"ROUTER: {len(dados_api)} itens de Comercialização processados para a API.")
        
        total_litros: float = 0.0
        for item_data in dados_api:
            if item_data.quantidade_litros is not None:
                total_litros += item_data.quantidade_litros
        
        print(f"ROUTER: Total de litros (Comercialização) calculado: {total_litros}")

        return ComercializacaoResponse(
            ano_referencia=ano,
            dados=dados_api,
            total_geral_litros=round(total_litros, 2)
        )
    except Exception as e:
        print(f"ROUTER ERROR (Comercialização): Ocorreu um erro inesperado: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Erro interno ao processar os dados de comercialização. Detalhe: {str(e)}"
        )