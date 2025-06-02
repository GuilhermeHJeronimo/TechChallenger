from sqlalchemy import Column, Integer, String, Float, UniqueConstraint
from app.db.base import Base

class Comercializacao(Base):
    __tablename__ = "dados_comercializacao"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    ano = Column(Integer, index=True, nullable=False)
    produto = Column(String, index=True, nullable=False)
    sub_produto = Column(String, index=True, nullable=True)
    quantidade_litros = Column(Float, nullable=True)

    __table_args__ = (UniqueConstraint('ano', 'produto', 'sub_produto', name='_com_ano_prod_subprod_uc'),)

    def __repr__(self):
        return f"<Comercializacao(ano='{self.ano}', produto='{self.produto}', sub_produto='{self.sub_produto}', qtd_l='{self.quantidade_litros}')>"