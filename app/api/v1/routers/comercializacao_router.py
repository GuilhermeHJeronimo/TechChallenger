from fastapi import APIRouter, Query, HTTPException, Depends
from typing import List, Optional
from sqlalchemy.orm import Session
from app.schemas.comercializacao_schemas import ComercializacaoResponse, ComercializacaoItemData
from app.services.embrapa_scraper import fetch_comercializacao_data
from app.services.auth_service import get_current_user
from app.models.user import User as UserModel
from app.db.session import get_db

router = APIRouter()

@router.get(
    "/",
    response_model=ComercializacaoResponse,
    summary="Consulta dados de comercialização por ano (Requer Autenticação).",
    description="Retorna uma lista de produtos e suas quantidades comercializadas em litros para um determinado ano. Os dados são buscados e salvos/atualizados no banco.",
    tags=["Comercialização"]
)
async def get_comercializacao_por_ano(
    ano: int = Query(
        ...,
        ge=1970,
        le=2023,
        description="Ano para consulta dos dados de comercialização (entre 1970 e 2023)."
    ),
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    print(f"ROUTER (Comercialização): Usuário '{current_user.username}' acessando dados para o ano: {ano}")
    try:
        dados_api: List[ComercializacaoItemData] = await fetch_comercializacao_data(db=db, year=ano)
        print(f"ROUTER: Serviço scraper/DB (Comercialização) retornou {len(dados_api)} itens processados.")

        if not dados_api:
            return ComercializacaoResponse(
                ano_referencia=ano,
                dados=[],
                total_geral_litros=0.0
            )
        
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
        import traceback
        print(f"ROUTER ERROR (Comercialização): Ocorreu um erro inesperado: {str(e)}\n{traceback.format_exc()}")
        raise HTTPException(
            status_code=500,
            detail=f"Erro interno ao processar os dados de comercialização. Detalhe: {str(e)}"
        )