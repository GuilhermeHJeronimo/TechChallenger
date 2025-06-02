from sqlalchemy.orm import Session
from typing import List

from app.models.importacao_model import Importacao as ImportacaoModel
from app.schemas.importacao_schemas import ImportacaoItemData

def create_or_replace_importacao_for_year_and_type(
    db: Session, 
    year: int, 
    tipo_importacao: str,
    importacao_data_list: List[ImportacaoItemData]
) -> List[ImportacaoModel]:
    db.query(ImportacaoModel).filter(
        ImportacaoModel.ano == year,
        ImportacaoModel.tipo_importacao == tipo_importacao
    ).delete(synchronize_session=False)
    
    db_importacao_list: List[ImportacaoModel] = []
    for item_data in importacao_data_list:
        if item_data.ano == year and item_data.tipo_importacao == tipo_importacao:
            db_item = ImportacaoModel(
                ano=item_data.ano,
                tipo_importacao=item_data.tipo_importacao,
                pais=item_data.pais,
                quantidade_kg=item_data.quantidade_kg,
                valor_usd=item_data.valor_usd
            )
            db_importacao_list.append(db_item)
            
    if db_importacao_list:
        db.add_all(db_importacao_list)
    db.commit()
    return db_importacao_list