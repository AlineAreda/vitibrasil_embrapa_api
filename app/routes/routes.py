from fastapi import APIRouter, Query, Depends, HTTPException, status
from app.auth import get_current_user, authorize_user
from requests.exceptions import ConnectionError, RequestException
import time

from app.utils_data.utils import health_check_site 
from app.utils_data.csv.download_csv import download_and_process_csv

from app.utils_data.web_scraping.scraping_producao import ProducaoScraper
from app.utils_data.web_scraping.scraping_processamento import ProcessamentoScraper
from app.utils_data.web_scraping.scraping_exportacao import ExportacaoScraper
from app.utils_data.web_scraping.scraping_importacao import ImportacaoScraper
from app.utils_data.web_scraping.scraping_comercializacao import ComercializacaoScraper
from app.utils_data.constants import opcoes_botoes_exportacao, opcoes_botoes_processamento, opcoes_botoes_importacao

router = APIRouter()

def get_data(scraper_class, start_year: int, end_year: int, botao=None):
    data = scraper_class(range(start_year, end_year + 1), botao)
    url = data.url
    csv_url = data.csv_url
    tipo = data.tipo # Verificar qual site é

    # Verificação de quais dados estão disponíveis, primeiro há tentativa do site, depois do csv
    try:
        if health_check_site(url):
            print('Tentativa através do Site')
            attempt = 0
            retries = 2  # tentativas
            while attempt < retries:
                try:
                    data.run()
                    return data.dados.to_dict(orient="records")
                except ConnectionError as e:
                    print(f"Tentativa {attempt + 1} falhou: {str(e)}")
                    attempt += 1
                    time.sleep(2)
                    if attempt == retries:
                        raise e
        else:
            raise RequestException("Site não disponível")
    except (ConnectionError, RequestException) as e:
        print('Erro ao conectar ao site para download CSV')
        
        try:
            data = download_and_process_csv(csv_url, tipo)
            data_filtered = data[(data['Ano'] >= start_year) & (data['Ano'] <= end_year)]
            
            if botao is not None: 
                classificacao_botao = botao['classificacao_botao']
                data_filtered = data_filtered[data_filtered['Botao'] == classificacao_botao]

            return data_filtered.to_dict(orient="records")
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=f"Erro ao baixar e processar o CSV: {str(e)}")

@router.get("/producao", 
        tags=["Produção"], 
        summary='Obter dados de Produção', 
        description='Retorna os dados de Produção de um intervalo de anos especificado'
        )
async def get_producao_data(start_year: int = 1970, end_year: int = 2023, current_user: dict = Depends(get_current_user)) -> list:
    authorize_user(current_user, "GET", "/producao"
)
    return get_data(ProducaoScraper, start_year, end_year)

@router.get("/processamento", 
        tags=["Processamento"], 
        summary='Obter dados de Processamento', 
        description='Retorna os dados de Processamento em um intervalo de anos especificado de forma opcional com as opções no site.')
async def get_processamento_data(
    start_year: int = 1970, 
    end_year: int = 2022,
    botao_opcao: str = Query(None, description="Opção para filtro: (VINIFERA, AMERICANAS_E_HIBRIDA, UVA_DE_MESA, SEM_CLASSIFICACAO)"),
    current_user: dict = Depends(get_current_user)
) -> list: 
    authorize_user(current_user, "GET", "/processamento")
    botao = opcoes_botoes_processamento.get(botao_opcao)
    return get_data(ProcessamentoScraper, start_year, end_year, botao)

@router.get("/comercializacao", 
        tags=["Comercialização"], 
        summary='Obter dados de Comercialização', 
        description='Retorna os dados de Comercialização de um intervalo de anos especificado')
async def get_comercializacao_data(start_year: int = 1970, end_year: int = 2023, current_user: dict = Depends(get_current_user)) -> list:
    authorize_user(current_user, "GET", "/comercializacao"
)
    return get_data(ComercializacaoScraper, start_year, end_year)

@router.get("/importacao"
, 
        tags=["Importação"], 
        summary='Obter dados de Importação', 
        description='Retorna os dados de Importação de um intervalo de anos especificado e de forma opcional com as opções no site.')
async def get_importacao_data(
    start_year: int = 1970, 
    end_year: int = 2023,
    botao_opcao: str = Query(None, description="Opção do botão (VINHOS_DE_MESA, ESPUMANTES, UVAS_FRESCAS, UVAS_PASSAS, SUCO_DE_UVA)"),
    current_user: dict = Depends(get_current_user)
) -> list: 
    authorize_user(current_user, "GET", "/importacao"
)
    botao = opcoes_botoes_importacao.get(botao_opcao)
    return get_data(ImportacaoScraper, start_year, end_year, botao)

@router.get("/exportacao"
, 
        tags=["Exportação"], 
        summary='Obter dados de Exportação', 
        description='Retorna os dados de Exportação de um intervalo de anos especificado e de forma opcional com as opções no site.')
async def get_exportacao_data(
    start_year: int = 1970, 
    end_year: int = 2023,
    botao_opcao: str = Query(None, description="Opção do botão (VINHOS_DE_MESA, ESPUMANTES, UVAS_FRESCAS, SUCO_DE_UVA)"),
    current_user: dict = Depends(get_current_user)
) -> list: 
    authorize_user(current_user, "GET", "/exportacao"
)
    botao = opcoes_botoes_exportacao.get(botao_opcao)
    return get_data(ExportacaoScraper, start_year, end_year, botao)

