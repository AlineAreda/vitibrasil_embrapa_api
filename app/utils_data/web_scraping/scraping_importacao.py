from ..web_scraping.scraping_base import ScraperBase
from unidecode import unidecode
import pandas as pd

class ImportacaoScraper(ScraperBase):
    def __init__(self, anos=range(2020, 2024), botao=None):
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
        params = {'ano': ano}
        if botao:
            params[botao['name']] = botao['value']
        return params
    
    def transform_data(self):
        super().transform_data()  # Chama o método da classe base para as transformações comuns
    
        # Remover acentuação e caracteres especiais e converter para maiúsculas
        def normalize_text(text):
            if isinstance(text, str):
                if text.strip() == "-" or text.strip()=="*":
                    return "0"
                else:
                    return unidecode(text).upper()
            else:
                return text

        # Aplicar normalização a todas as colunas de texto
        for col in self.dados.select_dtypes(include='object'):
            self.dados[col] = self.dados[col].map(normalize_text)

        # Renomear a coluna 'Quantidade (Kg)' para 'Quantidade'
        self.dados = self.dados.rename(columns={'Quantidade (Kg)': 'Quantidade'})

        # Garantir que todos os valores na coluna 'Quantidade' sejam strings antes de remover os pontos
        self.dados['Quantidade'] = self.dados['Quantidade'].astype(str).str.replace('.', '')

        # Substituir valores não numéricos por zero antes de converter para inteiro
        self.dados['Quantidade'] = pd.to_numeric(self.dados['Quantidade'], errors='coerce').fillna(0).astype(int)

        # Garantir que todos os valores na coluna 'Valor (US$)' sejam strings antes de remover os pontos
        self.dados['Valor (US$)'] = self.dados['Valor (US$)'].astype(str).str.replace('.', '')

        # Substituir valores não numéricos por zero antes de converter para inteiro
        self.dados['Valor (US$)'] = pd.to_numeric(self.dados['Valor (US$)'], errors='coerce').fillna(0).astype(int)


        # Ordenar as colunas
        colunas = ['Países', 'Ano', 'Quantidade', 'Valor (US$)', 'Botao']
        self.dados = self.dados[colunas]

        # Remover as linhas que possuem o total do ano no Web Scraping
        self.dados = self.dados.loc[(self.dados['Países'] != 'TOTAL') | (self.dados['Países'] != 'TOTAL')]
        
    
    def run(self):
        super().run()  # Chama o método run da classe base
        self.transform_data()  # Aplica as transformações nos dados

    def get_botoes(self):
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