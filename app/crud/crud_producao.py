from sqlalchemy.orm import Session
from typing import List, Optional
from app.models.producao_model import Producao as ProducaoModel
from app.schemas.producao_schemas import ProducaoItemData

def create_or_replace_producao_for_year(
    db: Session,
    year: int,
    producao_data_list: List[ProducaoItemData]
) -> List[ProducaoModel]:

    num_deleted = db.query(ProducaoModel).filter(ProducaoModel.ano == year).delete(synchronize_session=False)
    if num_deleted > 0:
        print(f"CRUD_PRODUCAO: {num_deleted} registros antigos para o ano {year} deletados.")
    else:
        print(f"CRUD_PRODUCAO: Nenhum registro antigo encontrado para o ano {year} para deletar.")

    db_producao_list: List[ProducaoModel] = []
    for item_data in producao_data_list:

        if item_data.ano == year:
            db_item = ProducaoModel(
                ano=item_data.ano,
                produto=item_data.produto,
                sub_produto=item_data.sub_produto,
                quantidade_litros=item_data.quantidade_litros
            )
            db_producao_list.append(db_item)
        else:
            print(f"CRUD_PRODUCAO WARNING: Item com ano {item_data.ano} ignorado ao processar para o ano {year}.")
    
    if db_producao_list:
        db.add_all(db_producao_list)

    db.commit()
    print(f"CRUD_PRODUCAO: {len(db_producao_list)} novos registros para o ano {year} inseridos/atualizados.")

    return db_producao_list

def get_producao_by_year(db: Session, year: int) -> List[ProducaoModel]:

    print(f"CRUD_PRODUCAO: Buscando dados de produção para o ano {year} no banco de dados.")
    results = db.query(ProducaoModel).filter(ProducaoModel.ano == year).all()
    print(f"CRUD_PRODUCAO: Encontrados {len(results)} registros para o ano {year}.")
    return results