import os
import requests
from lxml import etree
import re
from urllib.parse import urljoin
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import time
import random
from bs4 import BeautifulSoup

# Configuración
sitemap_file_path = 'sitemap.xml'
domain = "https://www.oakdenehollins.com"
output_dir = "pdf_reports"
error_log_path = 'errores.txt'
os.makedirs(output_dir, exist_ok=True)

# Lista de User-Agents para rotación
user_agents = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36",
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:89.0) Gecko/20100101 Firefox/89.0"
]

# Función para limpiar el contenido del XML
def clean_xml_content(content):
    # Eliminar cualquier referencia de entidad no válida
    content = re.sub(r'&(?!(amp|lt|gt|quot|apos);)', '&amp;', content)
    return content

# Función para extraer URLs del sitemap
def get_filtered_sitemap_urls(file_path):
    try:
        cleaned_content = ""
        with open(file_path, 'r', encoding='utf-8') as file:
            for line in file:
                if line.strip().startswith("<"):
                    cleaned_content += line
        
        cleaned_content = clean_xml_content(cleaned_content)
        
        print(f"Contenido del archivo sitemap (limpio):\n{cleaned_content[:500]}...")  # Imprimir los primeros 500 caracteres del archivo limpio
        
        # Parsear el contenido con lxml
        root = etree.fromstring(cleaned_content.encode('utf-8'))
        
        # Definir el espacio de nombres
        namespaces = {
            'ns': 'http://www.sitemaps.org/schemas/sitemap/0.9',
            'image': 'http://www.google.com/schemas/sitemap-image/1.1',
            'xhtml': 'http://www.w3.org/1999/xhtml'
        }
        
        # Buscar las etiquetas <loc> con el espacio de nombres
        loc_tags = root.xpath('//ns:loc', namespaces=namespaces)
        print(f"Número de etiquetas <loc> encontradas: {len(loc_tags)}")
        
        urls = [loc.text for loc in loc_tags if '/reports/' in loc.text]
        print(f"URLs extraídas y filtradas del sitemap: {len(urls)}")
        return urls
    except Exception as e:
        print(f"Error al leer el sitemap: {e}")
        return []

# Función para descargar PDF con verificación SSL
def download_pdf(url, output_path):
    try:
        session = requests.Session()
        retries = Retry(total=5, backoff_factor=1, status_forcelist=[502, 503, 504])
        session.mount('https://', HTTPAdapter(max_retries=retries))
        headers = {'User-Agent': random.choice(user_agents)}
        response = session.get(url, headers=headers, verify=True)
        if response.status_code == 200:
            with open(output_path, 'wb') as f:
                f.write(response.content)
            print(f"PDF descargado: {output_path}")
        else:
            log_error(url, f"Status Code: {response.status_code}")
    except requests.exceptions.RequestException as e:
        log_error(url, str(e))
    except requests.exceptions.SSLError as ssl_e:
        log_error(url, f"SSL Error: {ssl_e}")

# Función para registrar errores
def log_error(url, error_message):
    with open(error_log_path, 'a') as f:
        f.write(f"{url}: {error_message}\n")
    print(f"Error registrado: {url} - {error_message}")

# Función para hacer scraping y descargar PDFs
def scrape_and_download_pdfs(page_url):
    try:
        headers = {'User-Agent': random.choice(user_agents)}
        response = requests.get(page_url, headers=headers)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            pdf_links = soup.find_all('a', href=True)
            if not pdf_links:
                log_error(page_url, "No se encontraron enlaces a PDFs")
            for link in pdf_links:
                href = link['href']
                if href.endswith('.pdf'):
                    pdf_url = urljoin(domain, href)
                    pdf_name = pdf_url.split('/')[-1]
                    output_path = os.path.join(output_dir, pdf_name)
                    download_pdf(pdf_url, output_path)
        else:
            log_error(page_url, f"Status Code: {response.status_code}")
    except requests.exceptions.RequestException as e:
        log_error(page_url, str(e))

# Obtener todas las URLs del sitemap
filtered_sitemap_urls = get_filtered_sitemap_urls(sitemap_file_path)

print(f"URLs extraídas del sitemap: {len(filtered_sitemap_urls)}")

# Procesar cada URL y descargar los PDFs
for url in filtered_sitemap_urls:
    print(f"Procesando URL: {url}")
    scrape_and_download_pdfs(url)
    time.sleep(random.uniform(3, 7))  # Introduce un retardo aleatorio mayor entre 3 y 7 segundos
