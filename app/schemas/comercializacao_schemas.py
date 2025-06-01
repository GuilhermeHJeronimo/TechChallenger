from pydantic import BaseModel, Field
from typing import List, Optional, Union

class ComercializacaoItemBase(BaseModel):
    produto: str = Field(..., description="Nome do produto ou categoria principal comercializada.")
    sub_produto: Optional[str] = Field(None, description="Nome do subproduto ou especificação. Pode ser nulo.")

    class Config:
        from_attributes = True

class ComercializacaoItemData(ComercializacaoItemBase):
    quantidade_litros: Optional[float] = Field(None, description="Quantidade comercializada em litros. Pode ser None se não disponível/declarado.")
    ano: int = Field(..., description="Ano da comercialização.")

class ComercializacaoScrapedItem(ComercializacaoItemBase):
    quantidade_str: str = Field(..., description="Quantidade como string, diretamente do scraping.")

class ComercializacaoResponse(BaseModel):
    ano_referencia: int = Field(..., description="Ano ao qual os dados de comercialização se referem.")
    dados: List[ComercializacaoItemData] = Field(..., description="Lista dos itens de comercialização para o ano especificado.")
    total_geral_litros: Optional[float] = Field(None, description="Soma total de litros de todos os itens, se disponível e calculado.")