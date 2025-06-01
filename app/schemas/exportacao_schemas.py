from pydantic import BaseModel, Field
from typing import List, Optional

class ExportacaoItemBase(BaseModel):
    pais: str = Field(..., description="País de destino da exportação.")

    class Config:
        from_attributes = True

class ExportacaoItemData(ExportacaoItemBase):
    quantidade_kg: Optional[float] = Field(None, description="Quantidade exportada em quilogramas (KG). Pode ser None se não disponível.")
    valor_usd: Optional[float] = Field(None, description="Valor da exportação em Dólares Americanos (US$). Pode ser None se não disponível.")
    ano: int = Field(..., description="Ano da exportação.")
    tipo_exportacao: str = Field(..., description="Tipo de produto exportado (ex: 'vinhos_mesa', 'espumantes', 'uvas_frescas').")


class ExportacaoScrapedItem(ExportacaoItemBase):
    quantidade_str: str = Field(..., description="Quantidade em KG como string, diretamente do scraping.")
    valor_str: str = Field(..., description="Valor em US$ como string, diretamente do scraping.")
    tipo_exportacao: str = Field(..., description="Tipo de produto exportado (ex: 'vinhos_mesa', 'espumantes').")


class ExportacaoResponse(BaseModel):
    ano_referencia: int = Field(..., description="Ano ao qual os dados de exportação se referem.")
    tipo_exportacao: str = Field(..., description="Tipo de produto exportado para os dados listados.")
    dados: List[ExportacaoItemData] = Field(..., description="Lista dos itens de exportação para o ano e tipo especificados.")
    total_geral_kg: Optional[float] = Field(None, description="Soma total de KG de todos os itens, se disponível e calculado.")
    total_geral_usd: Optional[float] = Field(None, description="Soma total em US$ de todos os itens, se disponível e calculado.")