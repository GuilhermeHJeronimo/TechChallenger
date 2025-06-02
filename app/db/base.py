from sqlalchemy.orm import declarative_base

Base = declarative_base()

from app.models.user import User
from app.models.producao_model import Producao
from app.models.processamento_model import Processamento
from app.models.comercializacao_model import Comercializacao
from app.models.importacao_model import Importacao
from app.models.exportacao_model import Exportacao