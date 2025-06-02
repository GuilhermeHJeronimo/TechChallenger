from sqlalchemy.orm import Session
from typing import List, Optional
from app.models.producao_model import Producao as ProducaoModel
from app.schemas.producao_schemas import ProducaoItemData 

def create_or_replace_producao_for_year(
    db: Session, 
    year: int, 
    producao_data_list: List[ProducaoItemData]
) -> List[ProducaoModel]:

    db.query(ProducaoModel).filter(ProducaoModel.ano == year).delete(synchronize_session=False)
    print(f"CRUD_PRODUCAO: Registros antigos para o ano {year} deletados (se existiam).")


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
    
    if db_producao_list:
        db.add_all(db_producao_list)
    
    db.commit()

    print(f"CRUD_PRODUCAO: {len(db_producao_list)} novos registros para o ano {year} inseridos.")
    
    return db_producao_list
