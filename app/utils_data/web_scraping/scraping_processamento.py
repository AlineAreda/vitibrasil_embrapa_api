from ..web_scraping.scraping_base import ScraperBase
from unidecode import unidecode
import pandas as pd

class ProcessamentoScraper(ScraperBase):
    def __init__(self, anos=range(1970, 2022), botao=None):
        url = 'http://vitibrasil.cnpuv.embrapa.br/index.php?opcao=opt_03'  # Definindo a URL como um atributo de classe
        self.csv_url = ['http://vitibrasil.cnpuv.embrapa.br/download/ProcessaViniferas.csv',
                        'http://vitibrasil.cnpuv.embrapa.br/download/ProcessaAmericanas.csv',
                        'http://vitibrasil.cnpuv.embrapa.br/download/ProcessaMesa.csv',
                        'http://vitibrasil.cnpuv.embrapa.br/download/ProcessaSemclass.csv']
        self.tipo = 'Proces'
        super().__init__(url, anos)
        self.botao = botao

    def get_params(self, ano, botao=None):
        params = {'ano': ano}
        if botao:
            params[botao['name']] = botao['value']
        return params

    def transform_data(self):
        super().transform_data()  # Chama o método da classe base para as transformações comuns

        # Verificar se a coluna 'Cultivar' existe, caso contrário criar e preencher com 'Classificação' - Caso do botão SEM CLASSIFICAÇÃO
        if 'Cultivar' not in self.dados.columns and 'Classificação' in self.dados.columns:
            self.dados['Cultivar'] = self.dados['Classificação']

        # Verificar se a coluna 'Sem definição' existe no DataFrame
        if 'Sem definição' in self.dados.columns:
            if 'Cultivar' in self.dados.columns:
                # Substituir os valores na coluna 'Cultivar' pelos valores da coluna 'Sem definição'
                mask = self.dados['Sem definição'].notna() & self.dados['Cultivar'].isna()
                self.dados.loc[mask, 'Cultivar'] = self.dados.loc[mask, 'Sem definição']
            # Removendo a coluna 'Sem definição' que aparece apenas no botão SEM CLASSIFICAÇÃO do Processamento, pois não tem a coluna 'Cultivar'
            self.dados.drop(columns=['Sem definição'], inplace=True)

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
        
        # Ordenar as colunas
        colunas = ['Cultivar', 'Classificação', 'Ano', 'Quantidade', 'Botao']
        self.dados = self.dados[colunas]

        # Remover as linhas que possuem o total do ano no Web Scraping
        self.dados = self.dados.loc[(self.dados['Cultivar'] != 'TOTAL') | (self.dados['Classificação'] != 'TOTAL')]
    
    def run(self):
        super().run()  # Chama o método run da classe base
        self.transform_data()  # Aplica as transformações nos dados

    def get_botoes(self):
        if self.botao:
            return [self.botao]
        else:
            return [
                {'name': 'subopcao', 'value': 'subopt_01', 'classificacao_botao': 'VINIFERAS'},
                {'name': 'subopcao', 'value': 'subopt_02', 'classificacao_botao': 'AMERICANAS E HIBRIDAS'},
                {'name': 'subopcao', 'value': 'subopt_03', 'classificacao_botao': 'UVAS DE MESA'},
                {'name': 'subopcao', 'value': 'subopt_04', 'classificacao_botao': 'SEM CLASSIFICACAO'}
            ]