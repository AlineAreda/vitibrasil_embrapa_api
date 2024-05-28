import requests

# Verificar se o site está disponível
def health_check_site(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        return True
    except requests.exceptions.RequestException:
        return False
    


