import requests


def health_check_site(url):
    """
    Verifica a saúde do site fazendo uma requisição GET para a URL fornecida.

    :param url: URL do site a ser verificado.
    :return: True se o site estiver acessível, False caso contrário.
    """
    try:
        response = requests.get(url)
        response.raise_for_status()
        return True
    except requests.exceptions.RequestException:
        return False



