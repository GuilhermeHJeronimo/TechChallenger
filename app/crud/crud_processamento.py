from sqlalchemy.orm import Session
from typing import List

from app.models.processamento_model import Processamento as ProcessamentoModel
from app.schemas.processamento_schemas import ProcessamentoItemData

def create_or_replace_processamento_for_year_and_type(
    db: Session, 
    year: int, 
    tipo_processamento: str,
    processamento_data_list: List[ProcessamentoItemData]
) -> List[ProcessamentoModel]:
    db.query(ProcessamentoModel).filter(
        ProcessamentoModel.ano == year,
        ProcessamentoModel.tipo_processamento == tipo_processamento
    ).delete(synchronize_session=False)
    
    db_processamento_list: List[ProcessamentoModel] = []
    for item_data in processamento_data_list:
        if item_data.ano == year and item_data.tipo_processamento == tipo_processamento:
            db_item = ProcessamentoModel(
                ano=item_data.ano,
                tipo_processamento=item_data.tipo_processamento,
                cultivar=item_data.cultivar,
                quantidade_kg=item_data.quantidade_kg
            )
            db_processamento_list.append(db_item)
    
    if db_processamento_list:
        db.add_all(db_processamento_list)
    db.commit()
    return db_processamento_list