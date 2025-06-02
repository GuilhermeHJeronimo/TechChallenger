from sqlalchemy.orm import Session
from typing import List

from app.models.exportacao_model import Exportacao as ExportacaoModel
from app.schemas.exportacao_schemas import ExportacaoItemData

def create_or_replace_exportacao_for_year_and_type(
    db: Session, 
    year: int, 
    tipo_exportacao: str,
    exportacao_data_list: List[ExportacaoItemData]
) -> List[ExportacaoModel]:
    db.query(ExportacaoModel).filter(
        ExportacaoModel.ano == year,
        ExportacaoModel.tipo_exportacao == tipo_exportacao
    ).delete(synchronize_session=False)
    
    db_exportacao_list: List[ExportacaoModel] = []
    for item_data in exportacao_data_list:
        if item_data.ano == year and item_data.tipo_exportacao == tipo_exportacao:
            db_item = ExportacaoModel(
                ano=item_data.ano,
                tipo_exportacao=item_data.tipo_exportacao,
                pais=item_data.pais,
                quantidade_kg=item_data.quantidade_kg,
                valor_usd=item_data.valor_usd
            )
            db_exportacao_list.append(db_item)
            
    if db_exportacao_list:
        db.add_all(db_exportacao_list)
    db.commit()
    return db_exportacao_list