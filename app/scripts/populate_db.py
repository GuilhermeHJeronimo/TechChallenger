import asyncio
import sys
import os
from datetime import datetime
from sqlalchemy.orm import Session

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT_DIR = os.path.dirname(os.path.dirname(SCRIPT_DIR)) 
sys.path.append(PROJECT_ROOT_DIR)

from app.db.session import SessionLocal, engine
from app.db.base import Base
from app.services import embrapa_scraper 

# --- Configurações para a Coleta de Dados ---
START_YEAR = 1970

END_YEAR = datetime.now().year

async def populate_data_for_year(db: Session, year: int):

    print(f"\nPOPULATE_DB: Iniciando coleta de dados para o ano {year}...")
    
    # Produção
    print(f"POPULATE_DB: Coletando e salvando dados de Produção para {year}...")
    await embrapa_scraper.fetch_producao_data(db=db, year=year)
    print(f"POPULATE_DB: Dados de Produção para {year} processados e salvos.")

    # Comercialização
    print(f"POPULATE_DB: Coletando e salvando dados de Comercialização para {year}...")
    await embrapa_scraper.fetch_comercializacao_data(db=db, year=year)
    print(f"POPULATE_DB: Dados de Comercialização para {year} processados e salvos.")

    # Processamento
    for tipo_proc_key in embrapa_scraper.PROCESSAMENTO_TIPO_MAP.keys():
        print(f"POPULATE_DB: Coletando e salvando dados de Processamento ({tipo_proc_key}) para {year}...")
        await embrapa_scraper.fetch_processamento_data(db=db, year=year, tipo_processamento_key=tipo_proc_key)
        print(f"POPULATE_DB: Dados de Processamento ({tipo_proc_key}) para {year} processados e salvos.")

    # Importação
    for tipo_imp_key in embrapa_scraper.IMPORTACAO_TIPO_MAP.keys():
        print(f"POPULATE_DB: Coletando e salvando dados de Importação ({tipo_imp_key}) para {year}...")
        await embrapa_scraper.fetch_importacao_data(db=db, year=year, tipo_importacao_key=tipo_imp_key)
        print(f"POPULATE_DB: Dados de Importação ({tipo_imp_key}) para {year} processados e salvos.")

    # Exportação
    for tipo_exp_key in embrapa_scraper.EXPORTACAO_TIPO_MAP.keys():
        print(f"POPULATE_DB: Coletando e salvando dados de Exportação ({tipo_exp_key}) para {year}...")
        await embrapa_scraper.fetch_exportacao_data(db=db, year=year, tipo_exportacao_key=tipo_exp_key)
        print(f"POPULATE_DB: Dados de Exportação ({tipo_exp_key}) para {year} processados e salvos.")
    
    print(f"POPULATE_DB: Coleta para o ano {year} concluída.")

async def main_populate_all_years():
    """
    Função principal para popular o banco de dados com todos os anos definidos.
    """
    print("POPULATE_DB: Iniciando script de população completa do banco de dados...")
    
    # Garante que todas as tabelas definidas nos modelos SQLAlchemy existam
    print("POPULATE_DB: Verificando/Criando todas as tabelas do banco de dados...")
    Base.metadata.create_all(bind=engine)
    print("POPULATE_DB: Tabelas verificadas/criadas.")

    db: Session = SessionLocal()
    try:
        years_to_process = list(range(START_YEAR, END_YEAR + 1))
        total_years = len(years_to_process)
        print(f"POPULATE_DB: Serão processados {total_years} anos, de {START_YEAR} a {END_YEAR}.")

        for i, year_to_fetch in enumerate(years_to_process):
            print(f"\nPOPULATE_DB: Processando ano {year_to_fetch} ({i+1}/{total_years})...")
            await populate_data_for_year(db, year_to_fetch)
            

            if i < total_years - 1:
                sleep_duration = 5
                print(f"POPULATE_DB: Aguardando {sleep_duration} segundos antes de processar o próximo ano...")
                await asyncio.sleep(sleep_duration)
                
        print("\nPOPULATE_DB: População de todos os anos concluída com sucesso!")
    except Exception as e:
        import traceback
        print(f"POPULATE_DB: Ocorreu um erro durante o processo de população: {e}")
        print(traceback.format_exc())
    finally:
        db.close()
        print("POPULATE_DB: Sessão do banco de dados fechada.")

if __name__ == "__main__":
    print("=====================================================================")
    print("Executando script de população do banco de dados Embrapa Viticultura...")
    print("=====================================================================")

    asyncio.run(main_populate_all_years())
    print("=====================================================================")
    print("Script de população do banco de dados concluído.")
    print("=====================================================================")