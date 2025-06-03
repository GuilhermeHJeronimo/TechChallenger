from sqlalchemy.orm import Session
from typing import List, Optional
from app.models.comercializacao_model import Comercializacao as ComercializacaoModel
from app.schemas.comercializacao_schemas import ComercializacaoItemData

def create_or_replace_comercializacao_for_year(
    db: Session, 
    year: int, 
    comercializacao_data_list: List[ComercializacaoItemData]
) -> List[ComercializacaoModel]:
    db.query(ComercializacaoModel).filter(ComercializacaoModel.ano == year).delete(synchronize_session=False)
    print(f"CRUD_COMERCIALIZACAO: Registros antigos para o ano {year} deletados.")
    
    db_comercializacao_list: List[ComercializacaoModel] = []
    for item_data in comercializacao_data_list:
        if item_data.ano == year:
            db_item = ComercializacaoModel(
                ano=item_data.ano,
                produto=item_data.produto,
                sub_produto=item_data.sub_produto,
                quantidade_litros=item_data.quantidade_litros
            )
            db_comercializacao_list.append(db_item)
            
    if db_comercializacao_list:
        db.add_all(db_comercializacao_list)
    db.commit()
    print(f"CRUD_COMERCIALIZACAO: {len(db_comercializacao_list)} novos registros para o ano {year} inseridos.")
    return db_comercializacao_list


def get_comercializacao_by_year(db: Session, year: int) -> List[ComercializacaoModel]:

    print(f"CRUD_COMERCIALIZACAO: Buscando dados para o ano {year} no DB.")
    return db.query(ComercializacaoModel).filter(ComercializacaoModel.ano == year).all()