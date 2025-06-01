from pydantic import BaseModel, Field
from typing import List, Optional

class ImportacaoItemBase(BaseModel):
    pais: str = Field(..., description="País de origem da importação.")

    class Config:
        from_attributes = True

class ImportacaoItemData(ImportacaoItemBase):
    quantidade_kg: Optional[float] = Field(None, description="Quantidade importada em quilogramas (KG). Pode ser None se não disponível.")
    valor_usd: Optional[float] = Field(None, description="Valor da importação em Dólares Americanos (US$). Pode ser None se não disponível.")
    ano: int = Field(..., description="Ano da importação.")
    tipo_importacao: str = Field(..., description="Tipo de produto importado (ex: 'vinhos_mesa', 'espumantes', 'uvas_frescas').")


class ImportacaoScrapedItem(ImportacaoItemBase):
    quantidade_str: str = Field(..., description="Quantidade em KG como string, diretamente do scraping.")
    valor_str: str = Field(..., description="Valor em US$ como string, diretamente do scraping.")
    tipo_importacao: str = Field(..., description="Tipo de produto importado (ex: 'vinhos_mesa', 'espumantes').")


class ImportacaoResponse(BaseModel):
    ano_referencia: int = Field(..., description="Ano ao qual os dados de importação se referem.")
    tipo_importacao: str = Field(..., description="Tipo de produto importado para os dados listados.")
    dados: List[ImportacaoItemData] = Field(..., description="Lista dos itens de importação para o ano e tipo especificados.")
    total_geral_kg: Optional[float] = Field(None, description="Soma total de KG de todos os itens, se disponível e calculado.")
    total_geral_usd: Optional[float] = Field(None, description="Soma total em US$ de todos os itens, se disponível e calculado.")