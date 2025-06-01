import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Optional
from app.schemas.producao_schemas import ProducaoScrapedItem
from app.schemas.processamento_schemas import ProcessamentoScrapedItem
from app.schemas.comercializacao_schemas import ComercializacaoScrapedItem
from app.schemas.importacao_schemas import ImportacaoScrapedItem
from app.schemas.exportacao_schemas import ExportacaoScrapedItem

from app.core.config import EMBRAPA_INDEX_PHP_URL, EMBRAPA_REQUEST_TIMEOUT

DEFAULT_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

# --- Função para Produção ---
async def fetch_producao_data(year: int) -> List[ProducaoScrapedItem]:
    params = {
        'opcao': 'opt_02',
        'ano': year
    }
    scraped_data: List[ProducaoScrapedItem] = []
    current_main_product: Optional[str] = None
    print(f"SERVICE: Iniciando scraping de Produção para o ano: {year}...")
    try:
        response = requests.get(
            EMBRAPA_INDEX_PHP_URL, params=params, headers=DEFAULT_HEADERS, timeout=EMBRAPA_REQUEST_TIMEOUT
        )
        response.raise_for_status()
        print(f"SERVICE: Requisição para Embrapa (Produção) bem-sucedida. Status: {response.status_code}")
        soup = BeautifulSoup(response.content, 'html.parser')
        data_table = soup.find('table', class_='tb_dados')
        if not data_table:
            print(f"SERVICE: Tabela de dados 'tb_dados' (Produção) não encontrada para o ano {year}.")
            return []
        table_body = data_table.find('tbody')
        if not table_body:
            print(f"SERVICE: Corpo da tabela (tbody) (Produção) não encontrado para o ano {year}.")
            return []
        rows = table_body.find_all('tr')
        print(f"SERVICE: Encontradas {len(rows)} linhas na tabela de Produção para o ano {year}.")
        for row in rows:
            cols = row.find_all('td')
            if len(cols) == 2:
                product_cell_text = cols[0].get_text(separator=" ", strip=True)
                quantidade_cell_text = cols[1].get_text(separator=" ", strip=True).replace('.', '')
                product_cell_class = cols[0].get('class', [])
                produto_nome: Optional[str] = None
                sub_produto_nome: Optional[str] = None
                
                if 'tb_item' in product_cell_class:
                    current_main_product = product_cell_text
                    produto_nome = current_main_product
                elif 'tb_subitem' in product_cell_class and current_main_product:
                    produto_nome = current_main_product
                    sub_produto_nome = product_cell_text
                elif 'tb_subitem' not in product_cell_class and not current_main_product:
                    current_main_product = product_cell_text
                    produto_nome = current_main_product
                elif 'tb_subitem' not in product_cell_class and current_main_product:
                    current_main_product = product_cell_text
                    produto_nome = current_main_product
                else:
                    print(f"SERVICE: Linha com formato de produto/subproduto inesperado (Produção): {row}")
                    continue
                
                item = ProducaoScrapedItem(
                    produto=produto_nome, 
                    sub_produto=sub_produto_nome,
                    quantidade_str=quantidade_cell_text if quantidade_cell_text else "0"
                )
                scraped_data.append(item)
            elif len(cols) != 0:
                 print(f"SERVICE: Linha com número inesperado de colunas ({len(cols)}) em Produção: {row}")

    except requests.exceptions.Timeout:
        print(f"SERVICE ERROR: Timeout (Produção) para o ano {year}.")
        return []
    except requests.exceptions.RequestException as e:
        print(f"SERVICE ERROR: Erro na requisição (Produção) para o ano {year}: {e}")
        return []
    print(f"SERVICE: Scraping de Produção para o ano {year} concluído. {len(scraped_data)} itens extraídos.")
    return scraped_data

# --- Função para Processamento ---
PROCESSAMENTO_TIPO_MAP = {
    "viniferas": "subopt_01",
    "americanas_hibridas": "subopt_02",
    "uvas_mesa": "subopt_03",
    "sem_classificacao": "subopt_04",
}
async def fetch_processamento_data(year: int, tipo_processamento_key: str) -> List[ProcessamentoScrapedItem]:
    if tipo_processamento_key not in PROCESSAMENTO_TIPO_MAP:
        print(f"SERVICE ERROR: Tipo de processamento inválido: {tipo_processamento_key}")
        return []
    subopcao = PROCESSAMENTO_TIPO_MAP[tipo_processamento_key]
    params = {
        'opcao': 'opt_03',
        'subopcao': subopcao,
        'ano': year
    }
    scraped_data: List[ProcessamentoScrapedItem] = []
    print(f"SERVICE: Iniciando scraping de Processamento ({tipo_processamento_key}) para o ano: {year}...")
    try:
        response = requests.get(
            EMBRAPA_INDEX_PHP_URL, params=params, headers=DEFAULT_HEADERS, timeout=EMBRAPA_REQUEST_TIMEOUT
        )
        response.raise_for_status()
        print(f"SERVICE: Requisição para Embrapa (Processamento - {tipo_processamento_key}) bem-sucedida. Status: {response.status_code}")
        soup = BeautifulSoup(response.content, 'html.parser')
        data_table = soup.find('table', class_='tb_dados')
        if not data_table:
            print(f"SERVICE: Tabela de dados 'tb_dados' (Processamento - {tipo_processamento_key}) não encontrada para o ano {year}.")
            return []
        table_body = data_table.find('tbody')
        if not table_body:
            print(f"SERVICE: Corpo da tabela (tbody) (Processamento - {tipo_processamento_key}) não encontrado para o ano {year}.")
            return []
        rows = table_body.find_all('tr')
        print(f"SERVICE: Encontradas {len(rows)} linhas na tabela de Processamento ({tipo_processamento_key}) para o ano {year}.")
        for row in rows:
            cols = row.find_all('td')
            if len(cols) == 2:
                cultivar_text = cols[0].get_text(separator=" ", strip=True)
                quantidade_cell_text = cols[1].get_text(separator=" ", strip=True).replace('.', '')
                if not cultivar_text:
                    print(f"SERVICE: Linha com cultivar vazio (Processamento - {tipo_processamento_key}): {row}")
                    continue
                item = ProcessamentoScrapedItem(
                    cultivar=cultivar_text,
                    quantidade_str=quantidade_cell_text if quantidade_cell_text else "0",
                    tipo_processamento=tipo_processamento_key
                )
                scraped_data.append(item)
            elif len(cols) != 0:
                print(f"SERVICE: Linha com número inesperado de colunas ({len(cols)}) em Processamento ({tipo_processamento_key}): {row}")
    except requests.exceptions.Timeout:
        print(f"SERVICE ERROR: Timeout (Processamento - {tipo_processamento_key}) para o ano {year}.")
        return []
    except requests.exceptions.RequestException as e:
        print(f"SERVICE ERROR: Erro na requisição (Processamento - {tipo_processamento_key}) para o ano {year}: {e}")
        return []
    print(f"SERVICE: Scraping de Processamento ({tipo_processamento_key}) para o ano {year} concluído. {len(scraped_data)} itens extraídos.")
    return scraped_data

# --- Função para Comercialização ---
async def fetch_comercializacao_data(year: int) -> List[ComercializacaoScrapedItem]:
    params = {
        'opcao': 'opt_04',
        'ano': year
    }
    scraped_data: List[ComercializacaoScrapedItem] = []
    current_main_product: Optional[str] = None
    print(f"SERVICE: Iniciando scraping de Comercialização para o ano: {year}...")
    try:
        response = requests.get(
            EMBRAPA_INDEX_PHP_URL, params=params, headers=DEFAULT_HEADERS, timeout=EMBRAPA_REQUEST_TIMEOUT
        )
        response.raise_for_status()
        print(f"SERVICE: Requisição para Embrapa (Comercialização) bem-sucedida. Status: {response.status_code}")
        soup = BeautifulSoup(response.content, 'html.parser')
        data_table = soup.find('table', class_='tb_dados')
        if not data_table:
            print(f"SERVICE: Tabela de dados 'tb_dados' (Comercialização) não encontrada para o ano {year}.")
            return []
        table_body = data_table.find('tbody')
        if not table_body:
            print(f"SERVICE: Corpo da tabela (tbody) (Comercialização) não encontrado para o ano {year}.")
            return []
        rows = table_body.find_all('tr')
        print(f"SERVICE: Encontradas {len(rows)} linhas na tabela de Comercialização para o ano {year}.")
        for row in rows:
            cols = row.find_all('td')
            if len(cols) == 2:
                product_cell_text = cols[0].get_text(separator=" ", strip=True)
                quantidade_cell_text = cols[1].get_text(separator=" ", strip=True).replace('.', '')
                product_cell_class = cols[0].get('class', [])
                produto_nome: Optional[str] = None
                sub_produto_nome: Optional[str] = None

                if 'tb_item' in product_cell_class:
                    current_main_product = product_cell_text
                    produto_nome = current_main_product
                elif 'tb_subitem' in product_cell_class and current_main_product:
                    produto_nome = current_main_product
                    sub_produto_nome = product_cell_text
                elif 'tb_subitem' not in product_cell_class and not current_main_product:
                    current_main_product = product_cell_text
                    produto_nome = current_main_product
                elif 'tb_subitem' not in product_cell_class and current_main_product:
                    current_main_product = product_cell_text
                    produto_nome = current_main_product
                else:
                    print(f"SERVICE: Linha com formato de produto/subproduto inesperado (Comercialização): {row}")
                    continue
                
                item = ComercializacaoScrapedItem(
                    produto=produto_nome,
                    sub_produto=sub_produto_nome,
                    quantidade_str=quantidade_cell_text if quantidade_cell_text else "0"
                )
                scraped_data.append(item)
            elif len(cols) != 0:
                print(f"SERVICE: Linha com número inesperado de colunas ({len(cols)}) em Comercialização: {row}")

    except requests.exceptions.Timeout:
        print(f"SERVICE ERROR: Timeout (Comercialização) para o ano {year}.")
        return []
    except requests.exceptions.RequestException as e:
        print(f"SERVICE ERROR: Erro na requisição (Comercialização) para o ano {year}: {e}")
        return []
    print(f"SERVICE: Scraping de Comercialização para o ano {year} concluído. {len(scraped_data)} itens extraídos.")
    return scraped_data

# --- Função para Importação ---
IMPORTACAO_TIPO_MAP = {
    "vinhos_mesa": None,
    "espumantes": "subopt_02",
    "uvas_frescas": "subopt_03",
    "uvas_passas": "subopt_04",
    "suco_uva": "subopt_05",
}
async def fetch_importacao_data(year: int, tipo_importacao_key: str) -> List[ImportacaoScrapedItem]:
    if tipo_importacao_key not in IMPORTACAO_TIPO_MAP:
        print(f"SERVICE ERROR: Tipo de importação inválido: {tipo_importacao_key}")
        return []
    subopcao = IMPORTACAO_TIPO_MAP[tipo_importacao_key]
    params = {
        'opcao': 'opt_05',
        'ano': year
    }
    if subopcao:
        params['subopcao'] = subopcao
    scraped_data: List[ImportacaoScrapedItem] = []
    print(f"SERVICE: Iniciando scraping de Importação ({tipo_importacao_key}) para o ano: {year} com params: {params}...")
    try:
        response = requests.get(
            EMBRAPA_INDEX_PHP_URL, params=params, headers=DEFAULT_HEADERS, timeout=EMBRAPA_REQUEST_TIMEOUT
        )
        response.raise_for_status()
        print(f"SERVICE: Requisição para Embrapa (Importação - {tipo_importacao_key}) bem-sucedida. Status: {response.status_code}")
        soup = BeautifulSoup(response.content, 'html.parser')
        data_table = soup.find('table', class_='tb_dados')
        if not data_table:
            print(f"SERVICE: Tabela de dados 'tb_dados' (Importação - {tipo_importacao_key}) não encontrada para o ano {year}.")
            return []
        table_body = data_table.find('tbody')
        if not table_body:
            print(f"SERVICE: Corpo da tabela (tbody) (Importação - {tipo_importacao_key}) não encontrado para o ano {year}.")
            return []
        rows = table_body.find_all('tr')
        print(f"SERVICE: Encontradas {len(rows)} linhas na tabela de Importação ({tipo_importacao_key}) para o ano {year}.")
        for row in rows:
            cols = row.find_all('td')
            if len(cols) == 3:
                pais_text = cols[0].get_text(separator=" ", strip=True)
                quantidade_cell_text = cols[1].get_text(separator=" ", strip=True).replace('.', '')
                valor_cell_text = cols[2].get_text(separator=" ", strip=True).replace('.', '')
                if not pais_text:
                    print(f"SERVICE: Linha com país vazio (Importação - {tipo_importacao_key}): {row}")
                    continue
                item = ImportacaoScrapedItem(
                    pais=pais_text,
                    quantidade_str=quantidade_cell_text if quantidade_cell_text else "0",
                    valor_str=valor_cell_text if valor_cell_text else "0",
                    tipo_importacao=tipo_importacao_key
                )
                scraped_data.append(item)
            elif len(cols) != 0:
                print(f"SERVICE: Linha com número inesperado de colunas ({len(cols)}) em Importação ({tipo_importacao_key}): {row}")
    except requests.exceptions.Timeout:
        print(f"SERVICE ERROR: Timeout (Importação - {tipo_importacao_key}) para o ano {year}.")
        return []
    except requests.exceptions.RequestException as e:
        print(f"SERVICE ERROR: Erro na requisição (Importação - {tipo_importacao_key}) para o ano {year}: {e}")
        return []
    print(f"SERVICE: Scraping de Importação ({tipo_importacao_key}) para o ano {year} concluído. {len(scraped_data)} itens extraídos.")
    return scraped_data

# --- Função para Exportação ---
EXPORTACAO_TIPO_MAP = {
    "vinhos_mesa": None,
    "espumantes": "subopt_02",
    "uvas_frescas": "subopt_03",
    "suco_uva": "subopt_04",
}
async def fetch_exportacao_data(year: int, tipo_exportacao_key: str) -> List[ExportacaoScrapedItem]:
    if tipo_exportacao_key not in EXPORTACAO_TIPO_MAP:
        print(f"SERVICE ERROR: Tipo de exportação inválido: {tipo_exportacao_key}")
        return []
    subopcao = EXPORTACAO_TIPO_MAP[tipo_exportacao_key]
    params = {
        'opcao': 'opt_06',
        'ano': year
    }
    if subopcao:
        params['subopcao'] = subopcao
    scraped_data: List[ExportacaoScrapedItem] = []
    print(f"SERVICE: Iniciando scraping de Exportação ({tipo_exportacao_key}) para o ano: {year} com params: {params}...")
    try:
        response = requests.get(
            EMBRAPA_INDEX_PHP_URL,
            params=params,
            headers=DEFAULT_HEADERS,
            timeout=EMBRAPA_REQUEST_TIMEOUT
        )
        response.raise_for_status()
        print(f"SERVICE: Requisição para Embrapa (Exportação - {tipo_exportacao_key}) bem-sucedida. Status: {response.status_code}")
        soup = BeautifulSoup(response.content, 'html.parser')
        data_table = soup.find('table', class_='tb_dados')
        if not data_table:
            print(f"SERVICE: Tabela de dados 'tb_dados' (Exportação - {tipo_exportacao_key}) não encontrada para o ano {year}.")
            return []
        table_body = data_table.find('tbody')
        if not table_body:
            print(f"SERVICE: Corpo da tabela (tbody) (Exportação - {tipo_exportacao_key}) não encontrado para o ano {year}.")
            return []
        rows = table_body.find_all('tr')
        print(f"SERVICE: Encontradas {len(rows)} linhas na tabela de Exportação ({tipo_exportacao_key}) para o ano {year}.")
        for row in rows:
            cols = row.find_all('td')
            if len(cols) == 3:
                pais_text = cols[0].get_text(separator=" ", strip=True)
                quantidade_cell_text = cols[1].get_text(separator=" ", strip=True).replace('.', '') # Nome correto da variável
                valor_cell_text = cols[2].get_text(separator=" ", strip=True).replace('.', '')
                if not pais_text:
                    print(f"SERVICE: Linha com país vazio (Exportação - {tipo_exportacao_key}): {row}")
                    continue
                item = ExportacaoScrapedItem(
                    pais=pais_text,
                    quantidade_str=quantidade_cell_text if quantidade_cell_text else "0", # Uso correto da variável
                    valor_str=valor_cell_text if valor_cell_text else "0",
                    tipo_exportacao=tipo_exportacao_key
                )
                scraped_data.append(item)
            elif len(cols) != 0:
                print(f"SERVICE: Linha com número inesperado de colunas ({len(cols)}) em Exportação ({tipo_exportacao_key}): {row}")
    except requests.exceptions.Timeout:
        print(f"SERVICE ERROR: Timeout (Exportação - {tipo_exportacao_key}) para o ano {year}.")
        return []
    except requests.exceptions.RequestException as e:
        print(f"SERVICE ERROR: Erro na requisição (Exportação - {tipo_exportacao_key}) para o ano {year}: {e}")
        return []
    print(f"SERVICE: Scraping de Exportação ({tipo_exportacao_key}) para o ano {year} concluído. {len(scraped_data)} itens extraídos.")
    return scraped_data