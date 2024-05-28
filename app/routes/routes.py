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
    """
    Obtém dados usando a classe de raspagem fornecida, tenta primeiro obter dados do site,
    se falhar, tenta obter dados de um arquivo CSV.

    :param scraper_class: Classe de raspagem a ser usada.
    :param start_year: Ano de início para os dados.
    :param end_year: Ano de término para os dados.
    :param botao: Opção de botão para filtrar dados, se aplicável.
    :return: Dados raspados ou baixados e processados, em formato de lista de dicionários.
    """
    data = scraper_class(range(start_year, end_year + 1), botao)
    url = data.url
    csv_url = data.csv_url
    tipo = data.tipo 

    try:
        if health_check_site(url):
            print('Tentativa através do Site')
            attempt = 0
            retries = 2
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
    """
    Endpoint para obter dados de produção de um intervalo de anos especificado.

    :param start_year: Ano de início para os dados de produção.
    :param end_year: Ano de término para os dados de produção.
    :param current_user: Usuário atual autenticado.
    :return: Lista de dicionários contendo os dados de produção.
    """
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
    """
    Endpoint para obter dados de processamento de um intervalo de anos especificado, com filtro opcional.

    :param start_year: Ano de início para os dados de processamento.
    :param end_year: Ano de término para os dados de processamento.
    :param botao_opcao: Opção de filtro para os dados de processamento.
    :param current_user: Usuário atual autenticado.
    :return: Lista de dicionários contendo os dados de processamento.
    """
    authorize_user(current_user, "GET", "/processamento")
    botao = opcoes_botoes_processamento.get(botao_opcao)
    return get_data(ProcessamentoScraper, start_year, end_year, botao)

@router.get("/comercializacao", 
        tags=["Comercialização"], 
        summary='Obter dados de Comercialização', 
        description='Retorna os dados de Comercialização de um intervalo de anos especificado')
async def get_comercializacao_data(start_year: int = 1970, end_year: int = 2023, current_user: dict = Depends(get_current_user)) -> list:
    """
    Endpoint para obter dados de comercialização de um intervalo de anos especificado.

    :param start_year: Ano de início para os dados de comercialização.
    :param end_year: Ano de término para os dados de comercialização.
    :param current_user: Usuário atual autenticado.
    :return: Lista de dicionários contendo os dados de comercialização.
    """
    authorize_user(current_user, "GET", "/comercializacao")
    return get_data(ComercializacaoScraper, start_year, end_year)

@router.get("/importacao", 
        tags=["Importação"], 
        summary='Obter dados de Importação', 
        description='Retorna os dados de Importação de um intervalo de anos especificado e de forma opcional com as opções no site.')
async def get_importacao_data(
    start_year: int = 1970, 
    end_year: int = 2023,
    botao_opcao: str = Query(None, description="Opção do botão (VINHOS_DE_MESA, ESPUMANTES, UVAS_FRESCAS, UVAS_PASSAS, SUCO_DE_UVA)"),
    current_user: dict = Depends(get_current_user)
) -> list:
    """
    Endpoint para obter dados de importação de um intervalo de anos especificado, com filtro opcional.

    :param start_year: Ano de início para os dados de importação.
    :param end_year: Ano de término para os dados de importação.
    :param botao_opcao: Opção de filtro para os dados de importação.
    :param current_user: Usuário atual autenticado.
    :return: Lista de dicionários contendo os dados de importação.
    """
    authorize_user(current_user, "GET", "/importacao"
)
    botao = opcoes_botoes_importacao.get(botao_opcao)
    return get_data(ImportacaoScraper, start_year, end_year, botao)

@router.get("/exportacao", 
        tags=["Exportação"], 
        summary='Obter dados de Exportação', 
        description='Retorna os dados de Exportação de um intervalo de anos especificado e de forma opcional com as opções no site.')
async def get_exportacao_data(
    start_year: int = 1970, 
    end_year: int = 2023,
    botao_opcao: str = Query(None, description="Opção do botão (VINHOS_DE_MESA, ESPUMANTES, UVAS_FRESCAS, SUCO_DE_UVA)"),
    current_user: dict = Depends(get_current_user)
) -> list:
    """
    Endpoint para obter dados de exportação de um intervalo de anos especificado, com filtro opcional.

    :param start_year: Ano de início para os dados de exportação.
    :param end_year: Ano de término para os dados de exportação.
    :param botao_opcao: Opção de filtro para os dados de exportação.
    :param current_user: Usuário atual autenticado.
    :return: Lista de dicionários contendo os dados de exportação.
    """
    authorize_user(current_user, "GET", "/exportacao"
)
    botao = opcoes_botoes_exportacao.get(botao_opcao)
    return get_data(ExportacaoScraper, start_year, end_year, botao)

