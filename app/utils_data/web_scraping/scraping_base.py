import requests
from bs4 import BeautifulSoup
import pandas as pd
from unidecode import unidecode

class ScraperBase:
    def __init__(self, url, anos):
        self.url = url
        self.anos = anos
        self.dados = pd.DataFrame()

    def fetch_data(self, url, params):
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.content

    def parse_html(self, html):
        return BeautifulSoup(html, 'html.parser')

    def extract_table(self, soup):
        return soup.find('table', class_='tb_base tb_dados')

    def extract_data(self, table, classificacao_botao=''):
        headers = [header.text.strip() for header in table.find_all('th')]
        headers.append('Classificação')
        if classificacao_botao:
            headers.append('Botao')

        classificacao_atual = ''
        penultimo_tb_item = ''
        rows = []

        tfoot = table.find('tfoot', class_='tb_total') #Verificando se é o TOTAL

        for row in table.find_all('tr')[1:]:
            cells = row.find_all('td')
            row_data = [cell.text.strip() for cell in cells]

            if tfoot and row in tfoot.find_all('tr'):
                row_data.append('Total')
            elif 'tb_item' in cells[0].get('class', []):
                classificacao_atual = row_data[0]
                penultimo_tb_item = classificacao_atual
                row_data.append(classificacao_atual)
            elif 'tb_subitem' in cells[0].get('class', []):
                row_data.append(penultimo_tb_item)
            else:
                row_data.append('')

            if classificacao_botao:
                row_data.append(classificacao_botao)
            rows.append(row_data)
        return pd.DataFrame(rows, columns=headers)

    def run(self):
        for ano in self.anos:
            botao_iteravel = self.get_botoes()
            if botao_iteravel:
                for botao in botao_iteravel:
                    params = self.get_params(ano, botao)
                    html = self.fetch_data(self.url, params)
                    soup = self.parse_html(html)
                    table = self.extract_table(soup)
                    if table:
                        df = self.extract_data(table, botao['classificacao_botao'])
                        df['Ano'] = ano
                        self.dados = pd.concat([self.dados, df], ignore_index=True)
                    else:
                        print(f'Tabela não encontrada para o ano {ano} e botão {botao["value"]}.')
            else:
                params = self.get_params(ano)
                html = self.fetch_data(self.url, params)
                soup = self.parse_html(html)
                table = self.extract_table(soup)
                if table:
                    df = self.extract_data(table)
                    df['Ano'] = ano
                    self.dados = pd.concat([self.dados, df], ignore_index=True)
                else:
                    print(f'Tabela não encontrada para o ano {ano}.')

        self.transform_data()

    def get_params(self, ano, botao=None):
        raise NotImplementedError

    def get_botoes(self):
        raise NotImplementedError
    
    def transform_data(self):
        # Remover acentuação e caracteres especiais e converter para maiúsculas
        def normalize_text(text):
            if isinstance(text, str):
                # Substituir "-" ou "*" por 0 e depois aplicar a normalização
                if text.strip() == "-" or text.strip()=="*":
                    return "0"
                else:
                    return unidecode(text).upper()
            else:
                return text

        # Aplicar normalização a todas as colunas de texto
        for col in self.dados.select_dtypes(include='object'):
            self.dados[col] = self.dados[col].map(normalize_text)