from fastapi import APIRouter, Query, HTTPException, Depends
from typing import List, Optional
from sqlalchemy.orm import Session

from app.schemas.comercializacao_schemas import ComercializacaoResponse, ComercializacaoItemData
from app.services.auth_service import get_current_user
from app.models.user import User as UserModel
from app.models.comercializacao_model import Comercializacao as ComercializacaoModel
from app.db.session import get_db
from app.crud import crud_comercializacao

router = APIRouter()

@router.get(
    "/",
    response_model=ComercializacaoResponse,
    summary="Consulta dados de comercialização por ano do banco de dados (Requer Autenticação).",
    description="Retorna uma lista de produtos e suas quantidades comercializadas em litros para um determinado ano, consultando o banco de dados interno.",
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
    print(f"ROUTER (Comercialização DB): Usuário '{current_user.username}' solicitando dados para o ano: {ano}")
    
    db_items: List[ComercializacaoModel] = crud_comercializacao.get_comercializacao_by_year(db=db, year=ano)
    print(f"ROUTER (Comercialização DB): CRUD retornou {len(db_items)} itens do banco de dados.")

    if not db_items:
        print(f"ROUTER (Comercialização DB): Nenhum dado encontrado no banco para o ano {ano}.")
        return ComercializacaoResponse(
            ano_referencia=ano,
            dados=[],
            total_geral_litros=0.0
        )

    dados_api: List[ComercializacaoItemData] = [ComercializacaoItemData.model_validate(item) for item in db_items]
    
    total_litros: float = sum(item.quantidade_litros for item in dados_api if item.quantidade_litros is not None)
    print(f"ROUTER (Comercialização DB): Total de litros calculado: {total_litros}")

    return ComercializacaoResponse(
        ano_referencia=ano,
        dados=dados_api,
        total_geral_litros=round(total_litros, 2)
    )