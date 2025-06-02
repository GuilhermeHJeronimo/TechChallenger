from sqlalchemy import Column, Integer, String, Float, UniqueConstraint
from app.db.base import Base

class Producao(Base):
    __tablename__ = "dados_producao"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    ano = Column(Integer, index=True, nullable=False)
    produto = Column(String, index=True, nullable=False)
    sub_produto = Column(String, index=True, nullable=True)
    quantidade_litros = Column(Float, nullable=True)

    __table_args__ = (UniqueConstraint('ano', 'produto', 'sub_produto', name='_ano_produto_subproduto_uc'),)

    def __repr__(self):
        return f"<Producao(ano='{self.ano}', produto='{self.produto}', sub_produto='{self.sub_produto}', qtd='{self.quantidade_litros}')>"