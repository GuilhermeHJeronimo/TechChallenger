from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.db.base import Base
from app.db.session import engine
from app.api.v1.routers import producao_router
from app.api.v1.routers import processamento_router
from app.api.v1.routers import comercializacao_router
from app.api.v1.routers import importacao_router
from app.api.v1.routers import exportacao_router
from app.api.v1.routers import auth_router

# --- Lógica para criar tabelas no banco de dados ---
def create_db_and_tables():
    print("MAIN: Criando tabelas do banco de dados (se não existirem)...")
    Base.metadata.create_all(bind=engine)
    print("MAIN: Tabelas do banco de dados verificadas/criadas.")

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("MAIN: Iniciando aplicação...")
    create_db_and_tables()
    yield
    print("MAIN: Finalizando aplicação...")

description = """
API para consulta de dados de Vitivinicultura da Embrapa. 🍇

**Você poderá consultar dados sobre:**
* Produção
* Processamento (Viniferas, Americanas e Híbridas, Uvas de Mesa, Sem Classificação)
* Comercialização
* Importação (Vinhos de Mesa, Espumantes, Uvas Frescas, Uvas Passas, Suco de Uva)
* Exportação (Vinhos de Mesa, Espumantes, Uvas Frescas, Suco de Uva)

"""

app = FastAPI(
    title="Vitibrasil Embrapa API",
    description=description,
    version="0.1.0",
    openapi_tags=[
    ],
    lifespan=lifespan
)

origins = [
    "http://localhost",
    "http://localhost:3000",
    "http://127.0.0.1",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router.router, prefix="/api/v1/auth", tags=["Autenticação"])
app.include_router(producao_router.router, prefix="/api/v1/producao", tags=["Produção"])
app.include_router(processamento_router.router, prefix="/api/v1/processamento", tags=["Processamento"])
app.include_router(comercializacao_router.router, prefix="/api/v1/comercializacao", tags=["Comercialização"])
app.include_router(importacao_router.router, prefix="/api/v1/importacao", tags=["Importação"])
app.include_router(exportacao_router.router, prefix="/api/v1/exportacao", tags=["Exportação"])


@app.get("/", tags=["Saúde"])
async def root():
    return {"message": "Bem-vindo à API de Dados de Vitivinicultura da Embrapa!"}