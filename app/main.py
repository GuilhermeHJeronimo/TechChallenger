from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.docs import get_swagger_ui_html, get_swagger_ui_oauth2_redirect_html
from app.db.base import Base
from app.db.session import engine
from app.api.v1.routers import (
    producao_router, processamento_router, comercializacao_router,
    importacao_router, exportacao_router, auth_router
)

# Caminhos resolvidos
BASE_DIR = Path(__file__).resolve().parent.parent
TEMPLATES_DIR = BASE_DIR / "templates"
STATIC_DIR = BASE_DIR / "static"

# Inicialização do banco
def create_db_and_tables():
    print("MAIN: Criando tabelas do banco de dados (se não existirem)...")
    Base.metadata.create_all(bind=engine)
    print("MAIN: Tabelas do banco de dados verificadas/criadas.")

@asynccontextmanager
async def lifespan(app_instance: FastAPI):
    print("MAIN: Iniciando aplicação...")
    create_db_and_tables()
    yield
    print("MAIN: Finalizando aplicação...")

app = FastAPI(
    title="Vitibrasil Embrapa API",
    description="API para dados de vitivinicultura 🍇",
    version="0.1.0",
    lifespan=lifespan,
    docs_url=None,
    redoc_url=None 
)

app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Página principal
@app.get("/", response_class=HTMLResponse)
async def homepage(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# Swagger UI customizado
@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    return get_swagger_ui_html(
        openapi_url=app.openapi_url,
        title="Vitibrasil Embrapa API Docs",
        swagger_js_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui-bundle.js",
        swagger_css_url="/static/css/swagger-ui.css"
    )

@app.get("/docs/oauth2-redirect", include_in_schema=False)
async def swagger_ui_redirect():
    return get_swagger_ui_oauth2_redirect_html()

# Rotas da API
API_PREFIX = "/api/v1"
app.include_router(auth_router.router, prefix=f"{API_PREFIX}/auth", tags=["Autenticação"])
app.include_router(producao_router.router, prefix=f"{API_PREFIX}/producao", tags=["Produção"])
app.include_router(processamento_router.router, prefix=f"{API_PREFIX}/processamento", tags=["Processamento"])
app.include_router(comercializacao_router.router, prefix=f"{API_PREFIX}/comercializacao", tags=["Comercialização"])
app.include_router(importacao_router.router, prefix=f"{API_PREFIX}/importacao", tags=["Importação"])
app.include_router(exportacao_router.router, prefix=f"{API_PREFIX}/exportacao", tags=["Exportação"])

# Rota de saúde
@app.get("/health", tags=["Saúde"])
async def health():
    return {"status": "ok"}
