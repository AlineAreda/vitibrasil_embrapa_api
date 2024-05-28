from ..web_scraping.scraping_base import ScraperBase
from unidecode import unidecode
import pandas as pd

class ProcessamentoScraper(ScraperBase):
    def __init__(self, anos=range(1970, 2022), botao=None):
        """
        Inicializa o ProcessamentoScraper com a URL e os anos de interesse.

        :param anos: Intervalo de anos para obter os dados. Padrão é de 1970 a 2022.
        :param botao: Botão opcional para adicionar aos dados.
        """
        url = 'http://vitibrasil.cnpuv.embrapa.br/index.php?opcao=opt_03'
        self.csv_url = ['http://vitibrasil.cnpuv.embrapa.br/download/ProcessaViniferas.csv',
                        'http://vitibrasil.cnpuv.embrapa.br/download/ProcessaAmericanas.csv',
                        'http://vitibrasil.cnpuv.embrapa.br/download/ProcessaMesa.csv',
                        'http://vitibrasil.cnpuv.embrapa.br/download/ProcessaSemclass.csv']
        self.tipo = 'Proces'
        super().__init__(url, anos)
        self.botao = botao

    def get_params(self, ano, botao=None):
        """
        Obtém os parâmetros de requisição para um determinado ano e botão.

        :param ano: Ano para o qual obter os parâmetros.
        :param botao: Botão opcional para incluir nos parâmetros.
        :return: Dicionário de parâmetros de requisição.
        """
        params = {'ano': ano}
        if botao:
            params[botao['name']] = botao['value']
        return params

    def transform_data(self):
        """
        Transforma os dados raspados aplicando normalização de texto, 
        remoção de caracteres especiais e ordenação de colunas.
        """
        super().transform_data()
        
        if 'Cultivar' not in self.dados.columns and 'Classificação' in self.dados.columns:
            self.dados['Cultivar'] = self.dados['Classificação']


        if 'Sem definição' in self.dados.columns:
            if 'Cultivar' in self.dados.columns:

                mask = self.dados['Sem definição'].notna() & self.dados['Cultivar'].isna()
                self.dados.loc[mask, 'Cultivar'] = self.dados.loc[mask, 'Sem definição']

            self.dados.drop(columns=['Sem definição'], inplace=True)


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


        self.dados = self.dados.rename(columns={'Quantidade (Kg)': 'Quantidade'})


        self.dados['Quantidade'] = self.dados['Quantidade'].astype(str).str.replace('.', '')
        

        self.dados['Quantidade'] = pd.to_numeric(self.dados['Quantidade'], errors='coerce').fillna(0).astype(int)
        

        colunas = ['Cultivar', 'Classificação', 'Ano', 'Quantidade', 'Botao']
        self.dados = self.dados[colunas]


        self.dados = self.dados.loc[(self.dados['Cultivar'] != 'TOTAL') | (self.dados['Classificação'] != 'TOTAL')]
    def get_botoes(self):
        """
        Obtém a lista de botões a serem iterados durante a raspagem.

        :return: Lista de botões.
        """
        if self.botao:
            return [self.botao]
        else:
            return [
                {'name': 'subopcao', 'value': 'subopt_01', 'classificacao_botao': 'VINIFERAS'},
                {'name': 'subopcao', 'value': 'subopt_02', 'classificacao_botao': 'AMERICANAS E HIBRIDAS'},
                {'name': 'subopcao', 'value': 'subopt_03', 'classificacao_botao': 'UVAS DE MESA'},
                {'name': 'subopcao', 'value': 'subopt_04', 'classificacao_botao': 'SEM CLASSIFICACAO'}
            ]
            

    def run(self):
        """
        Executa o processo de raspagem e transformação de dados, 
        incluindo download, parsing, extração e transformação dos dados.
        """
        super().run()
        self.transform_data()

