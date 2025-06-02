from fastapi import APIRouter, Query, HTTPException, Depends
from typing import List, Optional
from sqlalchemy.orm import Session
from app.schemas.producao_schemas import ProducaoResponse, ProducaoItemData
from app.services.embrapa_scraper import fetch_producao_data
from app.services.auth_service import get_current_user
from app.models.user import User as UserModel
from app.db.session import get_db
router = APIRouter()

@router.get(
    "/",
    response_model=ProducaoResponse,
    summary="Consulta dados de produção vitivinícola por ano (Requer Autenticação)",
    description="Retorna uma lista de produtos e suas quantidades produzidas em litros para um determinado ano. Os dados são buscados do site da Embrapa e salvos/atualizados no banco de dados.",
    tags=["Produção"]
)
async def get_producao_por_ano(
    ano: int = Query(
        ...,
        ge=1970,
        le=2023,
        description="Ano para consulta dos dados de produção (entre 1970 e 2023)."
    ),
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):

    print(f"ROUTER (Produção): Usuário '{current_user.username}' acessando dados para o ano: {ano}")
    try:

        dados_producao_api: List[ProducaoItemData] = await fetch_producao_data(db=db, year=ano)
        print(f"ROUTER: Serviço scraper/DB (Produção) retornou {len(dados_producao_api)} itens processados.")

        if not dados_producao_api:
            return ProducaoResponse(
                ano_referencia=ano,
                dados=[],
                total_geral_litros=0.0
            )
        
        total_litros: float = 0.0
        for item_data in dados_producao_api:
            if item_data.quantidade_litros is not None:
                total_litros += item_data.quantidade_litros
        
        print(f"ROUTER: Total de litros (Produção) calculado: {total_litros}")

        return ProducaoResponse(
            ano_referencia=ano,
            dados=dados_producao_api,
            total_geral_litros=round(total_litros, 2)
        )
    except Exception as e:
        import traceback
        print(f"ROUTER ERROR (Produção): Ocorreu um erro inesperado: {str(e)}\n{traceback.format_exc()}")
        raise HTTPException(
            status_code=500,
            detail=f"Erro interno ao processar os dados de produção. Detalhe: {str(e)}"
        )