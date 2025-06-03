from sqlalchemy.orm import Session
from typing import List, Optional 
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
    print(f"CRUD_EXPORTACAO: Registros antigos para o ano {year} e tipo '{tipo_exportacao}' deletados.")
    
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
    print(f"CRUD_EXPORTACAO: {len(db_exportacao_list)} novos registros para o ano {year} e tipo '{tipo_exportacao}' inseridos.")
    return db_exportacao_list

def get_exportacao_by_year_and_type(
    db: Session, 
    year: int, 
    tipo_exportacao: str
) -> List[ExportacaoModel]:

    print(f"CRUD_EXPORTACAO: Buscando dados para o ano {year} e tipo '{tipo_exportacao}' no DB.")
    return db.query(ExportacaoModel).filter(
        ExportacaoModel.ano == year,
        ExportacaoModel.tipo_exportacao == tipo_exportacao
    ).all()