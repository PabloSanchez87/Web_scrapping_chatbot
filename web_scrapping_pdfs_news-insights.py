import os
import re
import asyncio
from pyppeteer import launch
from lxml import etree
import time
import random

# Configuración
sitemap_file_path = 'sitemap.xml'
output_dir_pdfs = "pdf_news_insights"
error_log_path = 'errores.txt'
os.makedirs(output_dir_pdfs, exist_ok=True)

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
        
        urls = [loc.text for loc in loc_tags if '/news-insights/' in loc.text]
        print(f"URLs extraídas y filtradas del sitemap: {len(urls)}")
        return urls
    except Exception as e:
        print(f"Error al leer el sitemap: {e}")
        return []

# Función para registrar errores
def log_error(url, error_message):
    with open(error_log_path, 'a') as f:
        f.write(f"{url}: {error_message}\n")
    print(f"Error registrado: {url} - {error_message}")

async def save_page_as_pdf(url):
    try:
        # Configuración de pyppeteer
        browser = await launch(headless=True)
        page = await browser.newPage()
        await page.goto(url, {'waitUntil': 'networkidle2'})
        
        # Eliminar los logos del encabezado y del móvil del DOM
        await page.evaluate('''() => {
            const headerLogo = document.querySelector('header .Header-branding-logo');
            if (headerLogo) {
                headerLogo.remove();
            }
            const mobileLogo = document.querySelector('.Mobile-bar-branding-logo');
            if (mobileLogo) {
                mobileLogo.remove();
            }
        }''')

        # Obtener el nombre del archivo PDF
        pdf_name = re.sub(r'\W+', '_', url) + '.pdf'
        output_path = os.path.join(output_dir_pdfs, pdf_name)
        
        # Guardar la página como PDF con márgenes personalizados
        await page.pdf({
            'path': output_path,
            'format': 'A4',
            'printBackground': True,
            'scale': 0.6,
        })
        print(f"PDF guardado: {output_path}")
        
        await browser.close()
    except Exception as e:
        log_error(url, str(e))

# Obtener todas las URLs del sitemap
filtered_sitemap_urls = get_filtered_sitemap_urls(sitemap_file_path)

print(f"URLs extraídas del sitemap: {len(filtered_sitemap_urls)}")

# Procesar cada URL y guardar como PDF
async def main():
    for url in filtered_sitemap_urls:
        print(f"Procesando URL: {url}")
        await save_page_as_pdf(url)
        time.sleep(random.uniform(3, 7))  # Introduce un retardo aleatorio mayor entre 3 y 7 segundos

asyncio.get_event_loop().run_until_complete(main())
