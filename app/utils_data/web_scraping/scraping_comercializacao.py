from ..web_scraping.scraping_base import ScraperBase
from unidecode import unidecode
import pandas as pd

class ComercializacaoScraper(ScraperBase):
    def __init__(self, anos=range(1970, 2023), botao=None):
        """
        Inicializa o ComercializacaoScraper com a URL e os anos de interesse.

        :param anos: Intervalo de anos para obter os dados. Padrão é de 1970 a 2023.
        :param botao: Botão opcional para adicionar aos dados.
        """
        url = 'http://vitibrasil.cnpuv.embrapa.br/index.php?opcao=opt_04'
        self.csv_url = ['http://vitibrasil.cnpuv.embrapa.br/download/Comercio.csv']
        self.tipo = 'Comerc'
        super().__init__(url, anos)
        self.botao = botao

    def get_params(self, ano, botao=None):
        """
        Obtém os parâmetros de requisição para um determinado ano e botão.

        :param ano: Ano para o qual obter os parâmetros.
        :param botao: Botão opcional para incluir nos parâmetros.
        :return: Dicionário de parâmetros de requisição.
        """
        return {'ano': ano}

    def get_botoes(self):
        """
        Obtém a lista de botões a serem iterados durante a raspagem.

        :return: Lista de botões.
        """
        return []
    
    def transform_data(self):
        """
        Transforma os dados raspados aplicando normalização de texto, 
        remoção de caracteres especiais e ordenação de colunas.
        """
        def normalize_text(text):
            if isinstance(text, str):
                if text.strip() == "-" or text.strip()=="*":
                    return "0"
                else:
                    return unidecode(text).upper()
            else:
                return text


        for col in self.dados.select_dtypes(include='object'):
            self.dados[col] = self.dados[col].map(normalize_text)


        self.dados = self.dados.rename(columns={'Quantidade (L.)': 'Quantidade'})


        self.dados['Quantidade'] = self.dados['Quantidade'].astype(str).str.replace('.', '')
        

        self.dados['Quantidade'] = pd.to_numeric(self.dados['Quantidade'], errors='coerce').fillna(0).astype(int)



        colunas = ['Produto', 'Classificação', 'Ano', 'Quantidade']
        self.dados = self.dados[colunas]


        self.dados = self.dados.loc[(self.dados['Produto'] != 'TOTAL') | (self.dados['Classificação'] != 'TOTAL')]
    

    def run(self):
        """
        Executa o processo de raspagem e transformação de dados, 
        incluindo download, parsing, extração e transformação dos dados.
        """
        super().run() 
        self.transform_data() 