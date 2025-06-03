from fastapi import APIRouter, Query, HTTPException, Depends
from typing import List, Optional
from sqlalchemy.orm import Session
from app.schemas.producao_schemas import ProducaoResponse, ProducaoItemData
from app.services.auth_service import get_current_user 
from app.models.user import User as UserModel 
from app.models.producao_model import Producao as ProducaoModel
from app.db.session import get_db
from app.crud import crud_producao

router = APIRouter()

@router.get(
    "/",
    response_model=ProducaoResponse,
    summary="Consulta dados de produção vitivinícola por ano do banco de dados (Requer Autenticação)",
    description="Retorna uma lista de produtos e suas quantidades produzidas em litros para um determinado ano, consultando o banco de dados interno.",
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

    print(f"ROUTER (Produção DB): Usuário '{current_user.username}' solicitando dados para o ano: {ano}")

    db_producao_items: List[ProducaoModel] = crud_producao.get_producao_by_year(db=db, year=ano)
    print(f"ROUTER (Produção DB): CRUD retornou {len(db_producao_items)} itens do banco de dados para o ano {ano}.")

    if not db_producao_items:
        print(f"ROUTER (Produção DB): Nenhum dado encontrado no banco para o ano {ano}.")
        return ProducaoResponse(
            ano_referencia=ano,
            dados=[],
            total_geral_litros=0.0
        )

    dados_api: List[ProducaoItemData] = []
    for db_item in db_producao_items:
        dados_api.append(ProducaoItemData.model_validate(db_item)) 

    total_litros: float = 0.0
    for item_data in dados_api:
        if item_data.quantidade_litros is not None:
            total_litros += item_data.quantidade_litros
    
    print(f"ROUTER (Produção DB): Total de litros calculado: {total_litros}")

    return ProducaoResponse(
        ano_referencia=ano,
        dados=dados_api,
        total_geral_litros=round(total_litros, 2)
    )