import requests

def check_robots_txt(url):
    robots_url = f"{url}/robots.txt"
    response = requests.get(robots_url)
    if response.status_code == 200:
        print(response.text)
    else:
        print("No se pudo acceder al archivo robots.txt")

# Verifica el archivo robots.txt del dominio
check_robots_txt("https://www.oakdenehollins.com")
