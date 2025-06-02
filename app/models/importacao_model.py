from sqlalchemy import Column, Integer, String, Float, UniqueConstraint
from app.db.base import Base

class Importacao(Base):
    __tablename__ = "dados_importacao"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    ano = Column(Integer, index=True, nullable=False)
    tipo_importacao = Column(String, index=True, nullable=False)
    pais = Column(String, index=True, nullable=False)
    quantidade_kg = Column(Float, nullable=True)
    valor_usd = Column(Float, nullable=True)

    __table_args__ = (UniqueConstraint('ano', 'tipo_importacao', 'pais', name='_imp_ano_tipo_pais_uc'),)

    def __repr__(self):
        return f"<Importacao(ano='{self.ano}', tipo='{self.tipo_importacao}', pais='{self.pais}', qtd_kg='{self.quantidade_kg}', val_usd='{self.valor_usd}')>"