from ..web_scraping.scraping_base import ScraperBase
from unidecode import unidecode
import pandas as pd

class ImportacaoScraper(ScraperBase):
    def __init__(self, anos=range(1970, 2023), botao=None):
        """
        Inicializa o ImportacaoScraper com a URL e os anos de interesse.

        :param anos: Intervalo de anos para obter os dados. Padrão é de 1970 a 2023.
        :param botao: Botão opcional para adicionar aos dados.
        """
        url = 'http://vitibrasil.cnpuv.embrapa.br/index.php?opcao=opt_05'  # Definindo a URL como um atributo de classe
        self.csv_url = ['http://vitibrasil.cnpuv.embrapa.br/download/ImpVinhos.csv',
                        'http://vitibrasil.cnpuv.embrapa.br/download/ImpEspumantes.csv',
                        'http://vitibrasil.cnpuv.embrapa.br/download/ImpFrescas.csv',
                        'http://vitibrasil.cnpuv.embrapa.br/download/ImpPassas.csv',
                        'http://vitibrasil.cnpuv.embrapa.br/download/ImpSuco.csv']
        self.tipo = 'Imp'
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


        self.dados['Valor (US$)'] = self.dados['Valor (US$)'].astype(str).str.replace('.', '')


        self.dados['Valor (US$)'] = pd.to_numeric(self.dados['Valor (US$)'], errors='coerce').fillna(0).astype(int)


        # Ordenar as colunas
        colunas = ['Países', 'Ano', 'Quantidade', 'Valor (US$)', 'Botao']
        self.dados = self.dados[colunas]


        self.dados = self.dados.loc[(self.dados['Países'] != 'TOTAL') | (self.dados['Países'] != 'TOTAL')]
        
    def get_botoes(self):
        """
        Obtém a lista de botões a serem iterados durante a raspagem.

        :return: Lista de botões.
        """
        if self.botao:
            return [self.botao]
        else:
            return [
                {'name': 'subopcao', 'value': 'subopt_01', 'classificacao_botao': 'VINHOS DE MESA'},
                {'name': 'subopcao', 'value': 'subopt_02', 'classificacao_botao': 'ESPUMANTES'},
                {'name': 'subopcao', 'value': 'subopt_03', 'classificacao_botao': 'UVAS FRESCAS'},
                {'name': 'subopcao', 'value': 'subopt_04', 'classificacao_botao': 'UVAS PASSAS'},
                {'name': 'subopcao', 'value': 'subopt_05', 'classificacao_botao': 'SUCO DE UVA'}
            ]
    
    def run(self):
        """
        Executa o processo de raspagem e transformação de dados, 
        incluindo download, parsing, extração e transformação dos dados.
        """
        super().run()
        self.transform_data()
        
