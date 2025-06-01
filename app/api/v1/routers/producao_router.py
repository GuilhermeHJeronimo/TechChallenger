from fastapi import APIRouter, Query, HTTPException
from typing import List, Optional
from app.schemas.producao_schemas import ProducaoResponse, ProducaoItemData, ProducaoScrapedItem
from app.services.embrapa_scraper import fetch_producao_data

router = APIRouter()

def _convert_scraped_to_item_data(scraped_items: List[ProducaoScrapedItem], ano: int) -> List[ProducaoItemData]:
    processed_items: List[ProducaoItemData] = []
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
            print(f"ROUTER WARNING: Não foi possível converter quantidade '{scraped_item.quantidade_str}' para float para o produto '{scraped_item.produto}'. Será considerado None.")
            quantidade_litros = None
        
        processed_items.append(
            ProducaoItemData(
                produto=scraped_item.produto,
                sub_produto=scraped_item.sub_produto,
                quantidade_litros=quantidade_litros,
                ano=ano
            )
        )
    return processed_items

@router.get(
    "/",
    response_model=ProducaoResponse,
    summary="Consulta dados de produção vitivinícola por ano",
    description="Retorna uma lista de produtos e suas quantidades produzidas em litros para um determinado ano, buscando diretamente do site da Embrapa.",
    tags=["Produção"]
)
async def get_producao_por_ano(
    ano: int = Query(
        ...,
        ge=1970,
        le=2023,
        description="Ano para consulta dos dados de produção (entre 1970 e 2023)."
    )
):
    try:
        print(f"ROUTER: Recebida requisição para produção do ano: {ano}")
        scraped_items: List[ProducaoScrapedItem] = await fetch_producao_data(year=ano)
        print(f"ROUTER: Scraper retornou {len(scraped_items)} itens raspados.")

        if not scraped_items:
            return ProducaoResponse(
                ano_referencia=ano,
                dados=[],
                total_geral_litros=0.0
            )

        dados_producao_api: List[ProducaoItemData] = _convert_scraped_to_item_data(scraped_items, ano)
        print(f"ROUTER: {len(dados_producao_api)} itens processados para a resposta da API.")
        
        total_litros: float = 0.0
        for item_data in dados_producao_api:
            if item_data.quantidade_litros is not None:
                total_litros += item_data.quantidade_litros
        
        print(f"ROUTER: Total de litros calculado: {total_litros}")

        return ProducaoResponse(
            ano_referencia=ano,
            dados=dados_producao_api,
            total_geral_litros=round(total_litros, 2)
        )

    except Exception as e:
        print(f"ROUTER ERROR: Ocorreu um erro inesperado no endpoint de produção: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Ocorreu um erro interno ao processar os dados de produção. Detalhe: {str(e)}"
        )