import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from app.schemas.producao_schemas import ProducaoScrapedItem, ProducaoItemData
from app.schemas.processamento_schemas import ProcessamentoScrapedItem, ProcessamentoItemData
from app.schemas.comercializacao_schemas import ComercializacaoScrapedItem, ComercializacaoItemData
from app.schemas.importacao_schemas import ImportacaoScrapedItem, ImportacaoItemData
from app.schemas.exportacao_schemas import ExportacaoScrapedItem, ExportacaoItemData
from app.core.config import EMBRAPA_INDEX_PHP_URL, EMBRAPA_REQUEST_TIMEOUT
from app.crud import crud_producao
from app.crud import crud_processamento
from app.crud import crud_comercializacao
from app.crud import crud_importacao
from app.crud import crud_exportacao

DEFAULT_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

# --- Helpers de Conversão ---
def _convert_producao_scraped_to_item_data(items: List[ProducaoScrapedItem], ano: int) -> List[ProducaoItemData]:
    processed = []
    for item in items:
        qtd: Optional[float] = None
        try:
            if item.quantidade_str and item.quantidade_str != "-": qtd = float(item.quantidade_str.replace(',', '.'))
        except ValueError: print(f"SCRAPER_SERVICE (Produção Conversão): Erro ao converter '{item.quantidade_str}'.")
        processed.append(ProducaoItemData(produto=item.produto, sub_produto=item.sub_produto, quantidade_litros=qtd, ano=ano))
    return processed

def _convert_processamento_scraped_to_item_data(items: List[ProcessamentoScrapedItem], ano: int, tipo_key: str) -> List[ProcessamentoItemData]:
    processed = []
    for item in items:
        qtd: Optional[float] = None
        try:
            if item.quantidade_str and item.quantidade_str != "-": qtd = float(item.quantidade_str.replace(',', '.'))
        except ValueError: print(f"SCRAPER_SERVICE (Processamento Conversão): Erro ao converter '{item.quantidade_str}'.")
        processed.append(ProcessamentoItemData(cultivar=item.cultivar, quantidade_kg=qtd, ano=ano, tipo_processamento=tipo_key))
    return processed

def _convert_comercializacao_scraped_to_item_data(items: List[ComercializacaoScrapedItem], ano: int) -> List[ComercializacaoItemData]:
    processed = []
    for item in items:
        qtd: Optional[float] = None
        try:
            if item.quantidade_str and item.quantidade_str != "-": qtd = float(item.quantidade_str.replace(',', '.'))
        except ValueError: print(f"SCRAPER_SERVICE (Comercialização Conversão): Erro ao converter '{item.quantidade_str}'.")
        processed.append(ComercializacaoItemData(produto=item.produto, sub_produto=item.sub_produto, quantidade_litros=qtd, ano=ano))
    return processed

def _convert_importacao_scraped_to_item_data(items: List[ImportacaoScrapedItem], ano: int, tipo_key: str) -> List[ImportacaoItemData]:
    processed = []
    for item in items:
        qtd_kg: Optional[float] = None; val_usd: Optional[float] = None
        try:
            if item.quantidade_str and item.quantidade_str != "-": qtd_kg = float(item.quantidade_str.replace(',', '.'))
        except ValueError: print(f"SCRAPER_SERVICE (Importação Conversão Qtd): Erro ao converter '{item.quantidade_str}'.")
        try:
            if item.valor_str and item.valor_str != "-": val_usd = float(item.valor_str.replace(',', '.'))
        except ValueError: print(f"SCRAPER_SERVICE (Importação Conversão Valor): Erro ao converter '{item.valor_str}'.")
        processed.append(ImportacaoItemData(pais=item.pais, quantidade_kg=qtd_kg, valor_usd=val_usd, ano=ano, tipo_importacao=tipo_key))
    return processed

def _convert_exportacao_scraped_to_item_data(items: List[ExportacaoScrapedItem], ano: int, tipo_key: str) -> List[ExportacaoItemData]:
    processed = []
    for item in items:
        qtd_kg: Optional[float] = None; val_usd: Optional[float] = None
        try:
            if item.quantidade_str and item.quantidade_str != "-": qtd_kg = float(item.quantidade_str.replace(',', '.'))
        except ValueError: print(f"SCRAPER_SERVICE (Exportação Conversão Qtd): Erro ao converter '{item.quantidade_str}'.")
        try:
            if item.valor_str and item.valor_str != "-": val_usd = float(item.valor_str.replace(',', '.'))
        except ValueError: print(f"SCRAPER_SERVICE (Exportação Conversão Valor): Erro ao converter '{item.valor_str}'.")
        processed.append(ExportacaoItemData(pais=item.pais, quantidade_kg=qtd_kg, valor_usd=val_usd, ano=ano, tipo_exportacao=tipo_key))
    return processed


# --- Funções de Scraping ---

async def fetch_producao_data(db: Session, year: int) -> List[ProducaoItemData]:
    params = {'opcao': 'opt_02', 'ano': year}
    raw_scraped_items: List[ProducaoScrapedItem] = []
    current_main_product: Optional[str] = None
    print(f"SERVICE: Iniciando scraping de Produção para o ano: {year}...")
    try:
        response = requests.get(EMBRAPA_INDEX_PHP_URL, params=params, headers=DEFAULT_HEADERS, timeout=EMBRAPA_REQUEST_TIMEOUT)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        data_table = soup.find('table', class_='tb_dados')
        if not data_table: return []
        table_body = data_table.find('tbody')
        if not table_body: return []
        rows = table_body.find_all('tr')
        for row in rows:
            cols = row.find_all('td')
            if len(cols) == 2:
                product_cell_text = cols[0].get_text(separator=" ", strip=True)
                quantidade_cell_text = cols[1].get_text(separator=" ", strip=True).replace('.', '')
                product_cell_class = cols[0].get('class', [])
                produto_nome: Optional[str] = None; sub_produto_nome: Optional[str] = None
                if 'tb_item' in product_cell_class: current_main_product = product_cell_text; produto_nome = current_main_product
                elif 'tb_subitem' in product_cell_class and current_main_product: produto_nome = current_main_product; sub_produto_nome = product_cell_text
                elif 'tb_subitem' not in product_cell_class and not current_main_product: current_main_product = product_cell_text; produto_nome = current_main_product
                elif 'tb_subitem' not in product_cell_class and current_main_product: current_main_product = product_cell_text; produto_nome = current_main_product
                else: continue
                raw_scraped_items.append(ProducaoScrapedItem(produto=produto_nome, sub_produto=sub_produto_nome, quantidade_str=quantidade_cell_text if quantidade_cell_text else "0"))
    except requests.exceptions.RequestException as e: print(f"SERVICE ERROR (Produção) ano {year}: {e}"); return []
    processed_data_list = _convert_producao_scraped_to_item_data(raw_scraped_items, year)
    if processed_data_list:
        try: crud_producao.create_or_replace_producao_for_year(db=db, year=year, producao_data_list=processed_data_list)
        except Exception as e: print(f"SERVICE ERROR (Produção DB Save) ano {year}: {e}")
    return processed_data_list

PROCESSAMENTO_TIPO_MAP = {"viniferas": "subopt_01", "americanas_hibridas": "subopt_02", "uvas_mesa": "subopt_03", "sem_classificacao": "subopt_04"}
async def fetch_processamento_data(db: Session, year: int, tipo_processamento_key: str) -> List[ProcessamentoItemData]:
    if tipo_processamento_key not in PROCESSAMENTO_TIPO_MAP: return []
    subopcao = PROCESSAMENTO_TIPO_MAP[tipo_processamento_key]
    params = {'opcao': 'opt_03', 'subopcao': subopcao, 'ano': year}
    raw_scraped_items: List[ProcessamentoScrapedItem] = []
    print(f"SERVICE: Iniciando scraping de Processamento ({tipo_processamento_key}) para o ano: {year}...")
    try:
        response = requests.get(EMBRAPA_INDEX_PHP_URL, params=params, headers=DEFAULT_HEADERS, timeout=EMBRAPA_REQUEST_TIMEOUT)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        data_table = soup.find('table', class_='tb_dados')
        if not data_table: return []
        table_body = data_table.find('tbody')
        if not table_body: return []
        rows = table_body.find_all('tr')
        for row in rows:
            cols = row.find_all('td')
            if len(cols) == 2:
                cultivar_text = cols[0].get_text(separator=" ", strip=True)
                quantidade_cell_text = cols[1].get_text(separator=" ", strip=True).replace('.', '')
                if not cultivar_text: continue
                raw_scraped_items.append(ProcessamentoScrapedItem(cultivar=cultivar_text, quantidade_str=quantidade_cell_text if quantidade_cell_text else "0", tipo_processamento=tipo_processamento_key)) 
    except requests.exceptions.RequestException as e: print(f"SERVICE ERROR (Processamento - {tipo_processamento_key}) ano {year}: {e}"); return []
    processed_data_list = _convert_processamento_scraped_to_item_data(raw_scraped_items, year, tipo_processamento_key)
    if processed_data_list:
        try: crud_processamento.create_or_replace_processamento_for_year_and_type(db=db, year=year, tipo_processamento=tipo_processamento_key, processamento_data_list=processed_data_list)
        except Exception as e: print(f"SERVICE ERROR (Processamento DB Save) ano {year}, tipo {tipo_processamento_key}: {e}")
    return processed_data_list

async def fetch_comercializacao_data(db: Session, year: int) -> List[ComercializacaoItemData]:
    params = {'opcao': 'opt_04', 'ano': year}
    raw_scraped_items: List[ComercializacaoScrapedItem] = []
    current_main_product: Optional[str] = None
    print(f"SERVICE: Iniciando scraping de Comercialização para o ano: {year}...")
    try:
        response = requests.get(EMBRAPA_INDEX_PHP_URL, params=params, headers=DEFAULT_HEADERS, timeout=EMBRAPA_REQUEST_TIMEOUT)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        data_table = soup.find('table', class_='tb_dados')
        if not data_table: return []
        table_body = data_table.find('tbody')
        if not table_body: return []
        rows = table_body.find_all('tr')
        for row in rows:
            cols = row.find_all('td')
            if len(cols) == 2:
                product_cell_text = cols[0].get_text(separator=" ", strip=True)
                quantidade_cell_text = cols[1].get_text(separator=" ", strip=True).replace('.', '')
                product_cell_class = cols[0].get('class', [])
                produto_nome: Optional[str] = None; sub_produto_nome: Optional[str] = None
                if 'tb_item' in product_cell_class: current_main_product = product_cell_text; produto_nome = current_main_product
                elif 'tb_subitem' in product_cell_class and current_main_product: produto_nome = current_main_product; sub_produto_nome = product_cell_text
                elif 'tb_subitem' not in product_cell_class and not current_main_product: current_main_product = product_cell_text; produto_nome = current_main_product
                elif 'tb_subitem' not in product_cell_class and current_main_product: current_main_product = product_cell_text; produto_nome = current_main_product
                else: continue
                raw_scraped_items.append(ComercializacaoScrapedItem(produto=produto_nome, sub_produto=sub_produto_nome, quantidade_str=quantidade_cell_text if quantidade_cell_text else "0"))
    except requests.exceptions.RequestException as e: print(f"SERVICE ERROR (Comercialização) ano {year}: {e}"); return []
    processed_data_list = _convert_comercializacao_scraped_to_item_data(raw_scraped_items, year)
    if processed_data_list:
        try: crud_comercializacao.create_or_replace_comercializacao_for_year(db=db, year=year, comercializacao_data_list=processed_data_list)
        except Exception as e: print(f"SERVICE ERROR (Comercialização DB Save) ano {year}: {e}")
    return processed_data_list

IMPORTACAO_TIPO_MAP = {"vinhos_mesa": None, "espumantes": "subopt_02", "uvas_frescas": "subopt_03", "uvas_passas": "subopt_04", "suco_uva": "subopt_05"}
async def fetch_importacao_data(db: Session, year: int, tipo_importacao_key: str) -> List[ImportacaoItemData]:
    if tipo_importacao_key not in IMPORTACAO_TIPO_MAP: return []
    subopcao = IMPORTACAO_TIPO_MAP[tipo_importacao_key]
    params = {'opcao': 'opt_05', 'ano': year}
    if subopcao: params['subopcao'] = subopcao
    raw_scraped_items: List[ImportacaoScrapedItem] = []
    print(f"SERVICE: Iniciando scraping de Importação ({tipo_importacao_key}) para o ano: {year} com params: {params}...")
    try:
        response = requests.get(EMBRAPA_INDEX_PHP_URL, params=params, headers=DEFAULT_HEADERS, timeout=EMBRAPA_REQUEST_TIMEOUT)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        data_table = soup.find('table', class_='tb_dados')
        if not data_table: return []
        table_body = data_table.find('tbody')
        if not table_body: return []
        rows = table_body.find_all('tr')
        for row in rows:
            cols = row.find_all('td')
            if len(cols) == 3:
                pais_text = cols[0].get_text(separator=" ", strip=True)
                quantidade_cell_text = cols[1].get_text(separator=" ", strip=True).replace('.', '')
                valor_cell_text = cols[2].get_text(separator=" ", strip=True).replace('.', '')
                if not pais_text: continue
                raw_scraped_items.append(ImportacaoScrapedItem(pais=pais_text, quantidade_str=quantidade_cell_text if quantidade_cell_text else "0", valor_str=valor_cell_text if valor_cell_text else "0", tipo_importacao=tipo_importacao_key))
            elif len(cols) !=0: print(f"SERVICE: Linha com número inesperado de colunas ({len(cols)}) em Importação ({tipo_importacao_key}): {row}")
    except requests.exceptions.RequestException as e: print(f"SERVICE ERROR (Importação - {tipo_importacao_key}) ano {year}: {e}"); return []
    processed_data_list = _convert_importacao_scraped_to_item_data(raw_scraped_items, year, tipo_importacao_key)
    if processed_data_list:
        try: crud_importacao.create_or_replace_importacao_for_year_and_type(db=db, year=year, tipo_importacao=tipo_importacao_key, importacao_data_list=processed_data_list)
        except Exception as e: print(f"SERVICE ERROR (Importação DB Save) ano {year}, tipo {tipo_importacao_key}: {e}")
    return processed_data_list

EXPORTACAO_TIPO_MAP = {"vinhos_mesa": None, "espumantes": "subopt_02", "uvas_frescas": "subopt_03", "suco_uva": "subopt_04"}
async def fetch_exportacao_data(db: Session, year: int, tipo_exportacao_key: str) -> List[ExportacaoItemData]:
    if tipo_exportacao_key not in EXPORTACAO_TIPO_MAP: return []
    subopcao = EXPORTACAO_TIPO_MAP[tipo_exportacao_key]
    params = {'opcao': 'opt_06', 'ano': year}
    if subopcao: params['subopcao'] = subopcao
    raw_scraped_items: List[ExportacaoScrapedItem] = []
    print(f"SERVICE: Iniciando scraping de Exportação ({tipo_exportacao_key}) para o ano: {year} com params: {params}...")
    try:
        response = requests.get(EMBRAPA_INDEX_PHP_URL, params=params, headers=DEFAULT_HEADERS, timeout=EMBRAPA_REQUEST_TIMEOUT)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        data_table = soup.find('table', class_='tb_dados')
        if not data_table: return []
        table_body = data_table.find('tbody')
        if not table_body: return []
        rows = table_body.find_all('tr')
        for row in rows:
            cols = row.find_all('td')
            if len(cols) == 3:
                pais_text = cols[0].get_text(separator=" ", strip=True)
                quantidade_cell_text = cols[1].get_text(separator=" ", strip=True).replace('.', '')
                valor_cell_text = cols[2].get_text(separator=" ", strip=True).replace('.', '')
                if not pais_text: continue
                raw_scraped_items.append(ExportacaoScrapedItem(pais=pais_text, quantidade_str=quantidade_cell_text if quantidade_cell_text else "0", valor_str=valor_cell_text if valor_cell_text else "0", tipo_exportacao=tipo_exportacao_key))
            elif len(cols) !=0: print(f"SERVICE: Linha com número inesperado de colunas ({len(cols)}) em Exportação ({tipo_exportacao_key}): {row}")
    except requests.exceptions.RequestException as e: print(f"SERVICE ERROR (Exportação - {tipo_exportacao_key}) ano {year}: {e}"); return []
    processed_data_list = _convert_exportacao_scraped_to_item_data(raw_scraped_items, year, tipo_exportacao_key)
    if processed_data_list:
        try: crud_exportacao.create_or_replace_exportacao_for_year_and_type(db=db, year=year, tipo_exportacao=tipo_exportacao_key, exportacao_data_list=processed_data_list)
        except Exception as e: print(f"SERVICE ERROR (Exportação DB Save) ano {year}, tipo {tipo_exportacao_key}: {e}")
    return processed_data_list