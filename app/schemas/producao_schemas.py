from pydantic import BaseModel, Field
from typing import List, Optional, Union

class ProducaoItemBase(BaseModel):
    produto: str = Field(..., description="Nome do produto ou categoria principal. Ex: 'VINHO DE MESA'")
    sub_produto: Optional[str] = Field(None, description="Nome do subproduto ou especificação. Ex: 'Tinto', 'Branco'. Pode ser nulo se não houver subproduto.")

    class Config:
        from_attributes = True

class ProducaoItemData(ProducaoItemBase):
    quantidade_litros: Optional[Union[float, str]] = Field(..., description="Quantidade produzida em litros. Pode ser 'nd' ou '-' se não disponível/declarado, que será tratado como None ou 0 na lógica de negócios. No retorno da API, idealmente float ou None.")
    ano: int = Field(..., description="Ano da produção.")

class ProducaoScrapedItem(ProducaoItemBase):
    quantidade_str: str = Field(..., description="Quantidade como string, diretamente do scraping. Ex: '169.762.429' ou '-'")

class ProducaoResponse(BaseModel):
    ano_referencia: int = Field(..., description="Ano ao qual os dados de produção se referem.")
    dados: List[ProducaoItemData] = Field(..., description="Lista dos itens de produção para o ano especificado.")
    total_geral_litros: Optional[float] = Field(None, description="Soma total de litros de todos os itens, se disponível e calculado.")
