import pandas as pd
import requests
from io import StringIO

from app.utils_data.csv.transform_csv import transform_csv


def infer_delimiter(text):
    """
    Infere o delimitador de um texto CSV.

    :param text: Texto do CSV.
    :return: Delimitador inferido.
    """
    delimiters = [';', '\t', ',']
    for delimiter in delimiters:
        sample = text.splitlines()[0]
        if delimiter in sample:
            return delimiter
    return ','


def download_and_process_csv(csv_urls, tipo):
    """
    Faz o download e processa os arquivos CSV fornecidos.

    :param csv_urls: Lista de URLs dos arquivos CSV.
    :param tipo: Tipo de dados a serem processados.
    :return: DataFrame combinado com os dados processados.
    """
    dataframes = []

    for csv_url in csv_urls:
        print('Pegando o csv do site: ' + csv_url)
        response = requests.get(csv_url)
        response.raise_for_status()
        csv_data = StringIO(response.text)


        first_line = response.text.split('\n', 1)[0]
        delimiter = infer_delimiter(first_line)


        df = pd.read_csv(csv_data, delimiter=delimiter, encoding='utf-8')

        formated = transform_csv(df, tipo)
        

        if tipo == 'Proces': 
            if csv_url.endswith("ProcessaViniferas.csv"):
                formated['Botao'] = 'VINIFERAS'
            elif csv_url.endswith("ProcessaAmericanas.csv"):
                formated['Botao'] = 'AMERICANAS E HIBRIDAS'
            elif csv_url.endswith("ProcessaMesa.csv"):
                formated['Botao'] = 'UVAS DE MESA'
            elif csv_url.endswith("ProcessaSemclass.csv"):
                formated['Botao'] = 'SEM CLASSIFICACAO'

        elif tipo == 'Imp': 
            if csv_url.endswith("ImpVinhos.csv"):
                formated['Botao'] = 'VINHOS DE MESA'
            elif csv_url.endswith("ImpEspumantes.csv"):
                formated['Botao'] = 'ESPUMANTES'
            elif csv_url.endswith("ImpFrescas.csv"):
                formated['Botao'] = 'UVAS FRESCAS'
            elif csv_url.endswith("ImpPassas.csv"):
                formated['Botao'] = 'UVAS PASSAS'
            elif csv_url.endswith("ImpSuco.csv"):
                formated['Botao'] = 'SUCO DE UVA'
        
        elif tipo == 'Exp': 
            if csv_url.endswith("ExpVinho.csv"):
                formated['Botao'] = 'VINHOS DE MESA'
            elif csv_url.endswith("ExpEspumantes.csv"):
                formated['Botao'] = 'ESPUMANTES'
            elif csv_url.endswith("ExpUva.csv"):
                formated['Botao'] = 'UVAS FRESCAS'
            elif csv_url.endswith("ExpSuco.csv"):
                formated['Botao'] = 'SUCO DE UVA'


        dataframes.append(formated)
                      

        
    
    combined_df = pd.concat(dataframes, ignore_index=True)
    
    return combined_df