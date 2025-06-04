from decouple import config
from typing import List
import os
from dotenv import load_dotenv
from pathlib import Path
import os


env_path = Path(__file__).resolve().parents[2] / ".env"
load_dotenv(dotenv_path=env_path)

print("DEBUG - ENV FILE LOADED")
print("DEBUG - RAW ENV DATABASE_URL:", os.getenv("DATABASE_URL"))




PROJECT_NAME: str = config("PROJECT_NAME", default="Vitibrasil Embrapa API")
API_VERSION: str = config("API_VERSION", default="0.1.0")
API_DESCRIPTION: str = config(
    "API_DESCRIPTION",
    default="API para consulta de dados de Vitivinicultura da Embrapa."
)

ALLOWED_HOSTS_STR: str = config("ALLOWED_HOSTS", default="http://localhost,http://127.0.0.1")

ALLOWED_HOSTS: List[str] = [host.strip() for host in ALLOWED_HOSTS_STR.split(',')]

SECRET_KEY: str = config("SECRET_KEY", default="admGuilhermeJeronimo2611")

ALGORITHM: str = config("ALGORITHM", default="HS256")

EMBRAPA_BASE_URL: str = config("EMBRAPA_BASE_URL", default="http://vitibrasil.cnpuv.embrapa.br")

EMBRAPA_INDEX_PHP_URL: str = f"{EMBRAPA_BASE_URL}/index.php"

EMBRAPA_REQUEST_TIMEOUT: int = config("EMBRAPA_REQUEST_TIMEOUT", default=15, cast=int)

DATABASE_URL: str = config("DATABASE_URL", default="sqlite:///./sql_app.db")

print(f"Carregando configurações para: {PROJECT_NAME}")
if SECRET_KEY == "admGuilhermeJeronimo2611":
    print("AVISO: SECRET_KEY está usando o valor padrão. Para produção, defina uma SECRET_KEY segura no seu arquivo .env.")
