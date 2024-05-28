import pandas as pd
from unidecode import unidecode

def remover_acentos(text):
    return unidecode(text)
    """
    Remove acentuação de um texto.
    
    :param text: Texto para remover acentuação.
    :return: Texto sem acentuação.
    """

def fix_characters(text):
    """
    Remove caracteres especiais de um texto e substitui por caracteres corretos.
    
    :param text: Texto para corrigir caracteres especiais.
    :return: Texto com caracteres especiais corrigidos.
    """
    replacements = {
        'Ã¡': 'Á', 'Ã©': 'É', 'Ã­': 'Í', 'Ã³': 'Ó', 'Ãº': 'Ú', 'Ã ': 'À', 'Ã¢': 'Â', 'Ã£': 'Ã',
        'Ã§': 'Ç', 'Ãª': 'Ê', 'Ã«': 'Ë', 'Ã¬': 'Ì', 'Ã®': 'Î', 'Ã¯': 'Ï', 'Ã´': 'Ô', 'Ã¶': 'Ö',
        'Ã¹': 'Ù', 'Ã¼': 'Ü', 'Ã½': 'Ý', 'Ã¿': 'Ÿ', 'Ã‘': 'Ñ', 'Ã‘': 'Ñ', 'Ã²': 'Ò',
        'â€™': "'", 'â€œ': '"', 'â€': '"', 'â€“': '-', 'â€˜': "'", 'â€¢': '•', 'â€¡': '‡',
        'â‚¬': '€', 'â„¢': '™', 'âˆž': '∞', 'âˆ†': '∆', 'âˆ†': '∆', 'âˆ‰': '∩', 'â‹…': '⋅',
        'âˆ’': '−', 'âˆ—': '*', 'âˆ…': '∅', 'âˆ': '∑', 'âˆ•': '/', 'âˆ•': '/', 'âˆš': '√',
        'â‰¥': '≥', 'â‰¤': '≤', 'â‰': '≠', 'â‰¤': '≤', 'âˆ›': '∧', 'âˆª': '∪', 'âˆ«': '∫',
        'âˆ‡': '∇', 'âˆµ': 'µ', 'âˆƒ': '∃', 'âˆˆ': '∈', 'âˆ†': '∆', 'âˆ‚': '∂', '': ''
    }
    for key, value in replacements.items():
        text = text.replace(key, value)
    return text


def transform_csv(csv, tipo):
    """
    Padroniza e transforma os dados de um DataFrame CSV de acordo com o tipo especificado.

    :param csv: DataFrame CSV a ser transformado.
    :param tipo: Tipo de dados a ser transformado ('Prod', 'Proces', 'Comerc', 'Imp', 'Exp').
    :return: DataFrame transformado.
    """
    def common_transformations(csv_df, column_mapping, control_transform, id_vars):
        """
        Aplica transformações comuns aos dados do DataFrame CSV.

        :param csv_df: DataFrame CSV a ser transformado.
        :param column_mapping: Mapeamento das colunas para renomear.
        :param control_transform: Função de transformação aplicada à coluna 'control'.
        :param id_vars: Variáveis de identificação para manter durante a transformação.
        :return: DataFrame transformado e remodelado.
        """
        csv_df = csv_df.drop(columns='id')
        csv_df = csv_df.rename(columns=column_mapping)
        primary_column = list(column_mapping.values())[0]
        csv_df = csv_df[[primary_column] + [col for col in csv_df.columns if col != primary_column]]
        csv_df['control'] = csv_df['control'].apply(control_transform)
        csv_df = csv_df.rename(columns={'control': 'Classificação'})
        csv_df[primary_column] = csv_df[primary_column].str.upper().str.strip()
        csv_df['Classificação'] = csv_df['Classificação'].str.upper().str.strip()
        df_melted = pd.melt(csv_df, id_vars=id_vars, var_name='Ano', value_name='Quantidade')
        df_melted['Ano'] = df_melted['Ano'].astype(int)
        df_melted['Quantidade'] = pd.to_numeric(df_melted['Quantidade'], errors='coerce').fillna(0).astype(int)
        return df_melted

    if tipo == 'Prod':
        def prod_transform(valor):
            if valor.startswith('vm_'):
                return 'VINHO DE MESA'
            elif valor.startswith('vv_'):
                return 'VINHO FINO DE MESA (VINIFERA)'
            elif valor.startswith('su_'):
                return 'SUCO'
            elif valor.startswith('de_'):
                return 'DERIVADOS'
            else:
                return valor
        return common_transformations(
            csv, 
            {'produto': 'Produto'}, 
            prod_transform, 
            ['Produto', 'Classificação']
        )
    
    elif tipo == 'Proces':
        def proces_transform(valor):
            if valor.startswith('ti_'):
                return 'TINTAS'
            elif valor.startswith('br_'):
                return 'BRANCAS E ROSADAS'
            elif valor.startswith('sc'):
                return 'SEM CLASSIFICACAO'
            else:
                return valor
        return common_transformations(
            csv, 
            {'cultivar': 'Cultivar'}, 
            proces_transform, 
            ['Cultivar', 'Classificação']
        )
    
    elif tipo == 'Comerc':
        def comerc_transform(valor):
            if valor.startswith('vm_'):
                return 'VINHO DE MESA'
            elif valor.startswith('vv_'):
                return 'VINHO FINO DE MESA'
            elif valor.startswith('ve_'):
                return 'VINHO ESPECIAL'
            elif valor.startswith('es_'):
                return 'ESPUMANTES'
            elif valor.startswith('su_'):
                return 'SUCO DE UVAS'
            elif valor.startswith('ou_'):
                return 'OUTROS PRODUTOS COMERCIALIZADOS'
            else:
                return valor
        csv_df = csv.drop(columns='id').rename(columns={'produto': 'Produto'})
        csv_df = csv_df[['Produto'] + [col for col in csv_df.columns if col != 'Produto']]
        csv_df['control'] = csv_df.apply(
            lambda row: row['Produto'] if pd.isna(row['control']) or row['control'] == '' else row['control'], 
            axis=1
        )
        csv_df['control'] = csv_df['control'].apply(comerc_transform)
        csv_df = csv_df.rename(columns={'control': 'Classificação'})
        csv_df['Produto'] = csv_df['Produto'].str.upper().str.strip()
        csv_df['Classificação'] = csv_df['Classificação'].str.upper().str.strip()
        df_melted = pd.melt(csv_df, id_vars=['Produto', 'Classificação'], var_name='Ano', value_name='Quantidade')
        df_melted['Ano'] = df_melted['Ano'].astype(int)
        return df_melted
    
    elif tipo == 'Imp' or tipo == 'Exp':
        column_name = 'Países'
        csv_df = csv.drop(columns='Id')
        csv_df.columns = [column_name] + list(csv_df.columns[1:])
        csv_df = csv_df[[column_name] + [col for col in csv_df.columns if col != column_name]]
        csv_df[column_name] = csv_df[column_name].str.upper().str.strip()

        csv_df[column_name] = csv_df[column_name].apply(fix_characters)
        csv_df[column_name] = csv_df[column_name].apply(remover_acentos)

        df_melted = pd.melt(csv_df, id_vars=[column_name], var_name='Ano', value_name='Quantidade')
        df_melted['Valor (US$)'] = None 
        df_melted = df_melted[[column_name, 'Ano', 'Quantidade', 'Valor (US$)']]
        df_melted['Ano'] = df_melted['Ano'].str.split('.').str[0].astype(int)
        return df_melted
    
    else:
        raise ValueError("Tipo não suportado: escolha entre 'Prod', 'Proces', 'Comerc', 'Imp' ou 'Exp'.")