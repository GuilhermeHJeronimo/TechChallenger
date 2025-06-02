from decouple import config
from typing import List

PROJECT_NAME: str = config("PROJECT_NAME", default="Vitibrasil Embrapa API")
API_VERSION: str = config("API_VERSION", default="0.1.0")
API_DESCRIPTION: str = config(
    "API_DESCRIPTION",
    default="API para consulta de dados de Vitivinicultura da Embrapa."
)

ALLOWED_HOSTS_STR: str = config("ALLOWED_HOSTS", default="http://localhost,http://127.0.0.1")

ALLOWED_HOSTS: List[str] = [host.strip() for host in ALLOWED_HOSTS_STR.split(',')]

SECRET_KEY: str = config("SECRET_KEY", default="seu_super_segredo_aqui_mude_isso_no_env")

ALGORITHM: str = config("ALGORITHM", default="HS256")

EMBRAPA_BASE_URL: str = config("EMBRAPA_BASE_URL", default="http://vitibrasil.cnpuv.embrapa.br")

EMBRAPA_INDEX_PHP_URL: str = f"{EMBRAPA_BASE_URL}/index.php"

EMBRAPA_REQUEST_TIMEOUT: int = config("EMBRAPA_REQUEST_TIMEOUT", default=15, cast=int)

print(f"Carregando configurações para: {PROJECT_NAME}")
if SECRET_KEY == "seu_super_segredo_aqui_mude_isso_no_env":
    print("AVISO: SECRET_KEY está usando o valor padrão. Para produção, defina uma SECRET_KEY segura no seu arquivo .env.")
