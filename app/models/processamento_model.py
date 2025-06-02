from sqlalchemy import Column, Integer, String, Float, UniqueConstraint
from app.db.base import Base

class Processamento(Base):
    __tablename__ = "dados_processamento"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    ano = Column(Integer, index=True, nullable=False)
    tipo_processamento = Column(String, index=True, nullable=False)
    cultivar = Column(String, index=True, nullable=False)
    quantidade_kg = Column(Float, nullable=True)

    __table_args__ = (UniqueConstraint('ano', 'tipo_processamento', 'cultivar', name='_ano_tipo_cultivar_uc'),)

    def __repr__(self):
        return f"<Processamento(ano='{self.ano}', tipo='{self.tipo_processamento}', cultivar='{self.cultivar}', qtd_kg='{self.quantidade_kg}')>"