from pydantic import BaseModel, Field
from typing import List, Optional

class ProcessamentoItemBase(BaseModel):
    cultivar: str = Field(..., description="Nome da cultivar ou 'SEM DEFINICAO' para uvas não classificadas.")

    class Config:
        from_attributes = True

class ProcessamentoItemData(ProcessamentoItemBase):
    quantidade_kg: Optional[float] = Field(None, description="Quantidade processada em quilogramas (KG). Pode ser None se não disponível/declarado.")
    ano: int = Field(..., description="Ano do processamento.")
    tipo_processamento: str = Field(..., description="Tipo de uva processada (ex: 'viniferas', 'americanas_hibridas', 'uvas_mesa', 'sem_classificacao').")


class ProcessamentoScrapedItem(ProcessamentoItemBase):
    quantidade_str: str = Field(..., description="Quantidade como string, diretamente do scraping. Ex: '123.456' ou '-'")
    tipo_processamento: str = Field(..., description="Tipo de uva processada (ex: 'viniferas', 'americanas_hibridas', 'uvas_mesa', 'sem_classificacao').")


class ProcessamentoResponse(BaseModel):
    ano_referencia: int = Field(..., description="Ano ao qual os dados de processamento se referem.")
    tipo_processamento: str = Field(..., description="Tipo de uva processada para os dados listados.")
    dados: List[ProcessamentoItemData] = Field(..., description="Lista dos itens de processamento para o ano e tipo especificados.")
    total_geral_kg: Optional[float] = Field(None, description="Soma total de KG de todos os itens, se disponível e calculado.")