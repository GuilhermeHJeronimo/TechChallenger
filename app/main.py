from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
import os
from app.db.base import Base
from app.db.session import engine

from app.api.v1.routers import producao_router
from app.api.v1.routers import processamento_router
from app.api.v1.routers import comercializacao_router
from app.api.v1.routers import importacao_router
from app.api.v1.routers import exportacao_router
from app.api.v1.routers import auth_router

PROJECT_ROOT_IN_CONTAINER = "/app"
TEMPLATES_DIR = os.path.join(PROJECT_ROOT_IN_CONTAINER, "templates")
STATIC_DIR = os.path.join(PROJECT_ROOT_IN_CONTAINER, "static")

def create_db_and_tables():
    print("MAIN.PY: Verificando e criando tabelas do banco de dados (se não existirem)...")
    Base.metadata.create_all(bind=engine)
    print("MAIN.PY: Tabelas do banco de dados prontas.")

@asynccontextmanager
async def lifespan(app_instance: FastAPI): 
    print("MAIN.PY: Evento de inicialização (lifespan) - Início.")


    print(f"MAIN.PY DEBUG: Caminho esperado para TEMPLATES_DIR: {TEMPLATES_DIR}")
    if not os.path.isdir(TEMPLATES_DIR):
        print(f"MAIN.PY ERROR CRÍTICO: Diretório de templates NÃO ENCONTRADO em: {TEMPLATES_DIR}")
    else:
        print(f"MAIN.PY INFO: Diretório de templates ENCONTRADO em: {TEMPLATES_DIR}")

    print(f"MAIN.PY DEBUG: Caminho esperado para STATIC_DIR: {STATIC_DIR}")
    if not os.path.isdir(STATIC_DIR):
        print(f"MAIN.PY ERROR CRÍTICO: Diretório de estáticos NÃO ENCONTRADO em: {STATIC_DIR}")
    else:
        print(f"MAIN.PY INFO: Diretório de estáticos ENCONTRADO em: {STATIC_DIR}")

    create_db_and_tables() # Cria as tabelas do banco de dados
    yield
    print("MAIN.PY: Evento de finalização (lifespan) - Fim.")


description = """
API para consulta de dados de Vitivinicultura da Embrapa. 🍇

**Funcionalidades:**

  * Consulta de dados de Produção, Processamento, Comercialização, Importação e Exportação.
  * Registro de usuários e autenticação via token JWT.
  * Página inicial interativa.

Acesse a documentação completa em `/docs` ou `/redoc`.
Para obter um token, registre-se em `/api/v1/auth/register` e faça login em `/api/v1/auth/token`.
"""
app = FastAPI(
    title="Vitibrasil Embrapa API",
    description=description,
    version="0.1.0",
    contact={
        "name": "Guilherme H. Jeronimo",
        "url": "https://github.com/GuilhermeHJeronimo/TechChallenger",
    },
    openapi_tags=[
        {"name": "Página Inicial", "description": "Página de boas-vindas da API."},
        {"name": "Autenticação", "description": "Operações de autenticação e registro."},
        {"name": "Produção", "description": "Dados de produção vitivinícola."},
        {"name": "Processamento", "description": "Dados de processamento de uvas."},
        {"name": "Comercialização", "description": "Dados de comercialização."},
        {"name": "Importação", "description": "Dados de importação de produtos vitivinícolas."},
        {"name": "Exportação", "description": "Dados de exportação de produtos vitivinícolas."},
        {"name": "Saúde", "description": "Verificação de status da API."}
    ],
    lifespan=lifespan
)

if os.path.isdir(STATIC_DIR):
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
    print(f"MAIN.PY INFO: Arquivos estáticos montados de '{STATIC_DIR}' em '/static'.")
else:
    print(f"MAIN.PY ALERTA: Diretório estático '{STATIC_DIR}' não existe. Arquivos estáticos não serão servidos. Verifique seu Dockerfile e a estrutura do projeto.")

templates = None
if os.path.isdir(TEMPLATES_DIR):
    templates = Jinja2Templates(directory=TEMPLATES_DIR)
    print(f"MAIN.PY INFO: Templates Jinja2 configurados para o diretório '{TEMPLATES_DIR}'.")
else:
    print(f"MAIN.PY ALERTA: Diretório de templates '{TEMPLATES_DIR}' não existe. A página inicial não será servida corretamente.")


origins = [
    "http://localhost",
    "http://localhost:8000",
    "http://127.0.0.1",
    "http://127.0.0.1:8000",
    "https://techchallenger.onrender.com",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/", response_class=HTMLResponse, tags=["Página Inicial"], include_in_schema=False)
async def read_root(request: Request):
    if templates:
        return templates.TemplateResponse("index.html", {"request": request})
    else:
        return HTMLResponse("<html><body><h1>Erro: Página inicial não pôde ser carregada (diretório de templates ausente).</h1></body></html>", status_code=500)

# --- Incluir os Routers da API ---

API_PREFIX = "/api/v1"
app.include_router(auth_router.router, prefix=f"{API_PREFIX}/auth", tags=["Autenticação"])
app.include_router(producao_router.router, prefix=f"{API_PREFIX}/producao", tags=["Produção"])
app.include_router(processamento_router.router, prefix=f"{API_PREFIX}/processamento", tags=["Processamento"])
app.include_router(comercializacao_router.router, prefix=f"{API_PREFIX}/comercializacao", tags=["Comercialização"])
app.include_router(importacao_router.router, prefix=f"{API_PREFIX}/importacao", tags=["Importação"])
app.include_router(exportacao_router.router, prefix=f"{API_PREFIX}/exportacao", tags=["Exportação"])

@app.get("/health", tags=["Saúde"], include_in_schema=True)
async def health_check():
    return {"status": "API online e operacional!"}