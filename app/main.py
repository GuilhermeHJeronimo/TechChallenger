from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.routers import producao_router
from app.api.v1.routers import processamento_router
from app.api.v1.routers import comercializacao_router
from app.api.v1.routers import importacao_router
from app.api.v1.routers import exportacao_router

description = """
API para consulta de dados de Vitivinicultura da Embrapa. 🍇

**Você poderá consultar dados sobre:**
* Produção
* Processamento (Viniferas, Americanas e Híbridas, Uvas de Mesa, Sem Classificação)
* Comercialização
* Importação (Vinhos de Mesa, Espumantes, Uvas Frescas, Uvas Passas, Suco de Uva)
* Exportação (Vinhos de Mesa, Espumantes, Uvas Frescas, Suco de Uva)

Futuramente, esta API alimentará uma base de dados para modelos de Machine Learning.
"""

app = FastAPI(
    title="Vitibrasil Embrapa API",
    description=description,
    version="0.1.0",
    openapi_tags=[
        {
            "name": "Autenticação",
            "description": "Operações de autenticação e gerenciamento de tokens.",
        },
        {
            "name": "Produção",
            "description": "Endpoints para dados de produção vitivinícola.",
        },
        {
            "name": "Processamento",
            "description": "Endpoints para dados de processamento de uvas.",
        },
        {
            "name": "Comercialização",
            "description": "Endpoints para dados de comercialização.",
        },
        {
            "name": "Importação",
            "description": "Endpoints para dados de importação de produtos vitivinícolas.",
        },
        {
            "name": "Exportação",
            "description": "Endpoints para dados de exportação de produtos vitivinícolas.",
        },
        {
            "name": "Saúde",
            "description": "Verificação de status da API.",
        }
    ]
)

# Configuração do CORS
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

app.include_router(producao_router.router, prefix="/api/v1/producao", tags=["Produção"])
app.include_router(processamento_router.router, prefix="/api/v1/processamento", tags=["Processamento"])
app.include_router(comercializacao_router.router, prefix="/api/v1/comercializacao", tags=["Comercialização"])
app.include_router(importacao_router.router, prefix="/api/v1/importacao", tags=["Importação"])
app.include_router(exportacao_router.router, prefix="/api/v1/exportacao", tags=["Exportação"])


@app.get("/", tags=["Saúde"])
async def root():
    return {"message": "Bem-vindo à API de Dados de Vitivinicultura da Embrapa!"}