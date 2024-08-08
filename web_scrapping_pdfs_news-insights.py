import os  # Import the OS module to interact with the operating system
import re  # Import the regular expression module for string manipulation
import asyncio  # Import asyncio for asynchronous programming
from pyppeteer import launch  # Import pyppeteer for controlling headless browsers
from lxml import etree  # Import lxml for XML and HTML parsing
import time  # Import time module to handle delays
import random  # Import random module for generating random numbers

# Configuration
sitemap_file_path = 'sitemap.xml'  # Path to the sitemap file
output_dir_pdfs = "pdf_news_insights"  # Directory to save the PDFs
error_log_path = 'errores.txt'  # Path to the error log file
os.makedirs(output_dir_pdfs, exist_ok=True)  # Create the output directory if it doesn't exist

# Function to clean the content of the XML file
def clean_xml_content(content):
    # Remove any invalid entity references
    content = re.sub(r'&(?!(amp|lt|gt|quot|apos);)', '&amp;', content)
    return content

# Function to extract URLs from the sitemap
def get_filtered_sitemap_urls(file_path):
    try:
        cleaned_content = ""
        with open(file_path, 'r', encoding='utf-8') as file:
            for line in file:
                if line.strip().startswith("<"):
                    cleaned_content += line
        
        cleaned_content = clean_xml_content(cleaned_content)
        
        # Print the first 500 characters of the cleaned sitemap content
        print(f"Cleaned sitemap file content:\n{cleaned_content[:500]}...")
        
        # Parse the cleaned content with lxml
        root = etree.fromstring(cleaned_content.encode('utf-8'))
        
        # Define the XML namespaces
        namespaces = {
            'ns': 'http://www.sitemaps.org/schemas/sitemap/0.9',
            'image': 'http://www.google.com/schemas/sitemap-image/1.1',
            'xhtml': 'http://www.w3.org/1999/xhtml'
        }
        
        # Find <loc> tags within the specified namespace
        loc_tags = root.xpath('//ns:loc', namespaces=namespaces)
        print(f"Number of <loc> tags found: {len(loc_tags)}")
        
        # Filter URLs containing '/news-insights/'
        urls = [loc.text for loc in loc_tags if '/news-insights/' in loc.text]
        print(f"Filtered URLs extracted from sitemap: {len(urls)}")
        return urls
    except Exception as e:
        print(f"Error reading the sitemap: {e}")
        return []

# Function to log errors
def log_error(url, error_message):
    with open(error_log_path, 'a') as f:
        f.write(f"{url}: {error_message}\n")
    print(f"Logged error: {url} - {error_message}")

# Asynchronous function to save a web page as a PDF
async def save_page_as_pdf(url):
    try:
        # Configure pyppeteer to launch a headless browser
        browser = await launch(headless=True)
        page = await browser.newPage()
        await page.goto(url, {'waitUntil': 'networkidle2'})
        
        # Remove logos from the header and mobile view
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

        # Generate the PDF file name by replacing non-alphanumeric characters with underscores
        pdf_name = re.sub(r'\W+', '_', url) + '.pdf'
        output_path = os.path.join(output_dir_pdfs, pdf_name)
        
        # Save the page as a PDF with custom margins
        await page.pdf({
            'path': output_path,
            'format': 'A4',
            'printBackground': True,
            'scale': 0.6,
        })
        print(f"Saved PDF: {output_path}")
        
        await browser.close()
    except Exception as e:
        log_error(url, str(e))

# Get all the URLs from the sitemap
filtered_sitemap_urls = get_filtered_sitemap_urls(sitemap_file_path)

print(f"Extracted URLs from sitemap: {len(filtered_sitemap_urls)}")

# Process each URL and save as PDF
async def main():
    for url in filtered_sitemap_urls:
        print(f"Processing URL: {url}")
        await save_page_as_pdf(url)
        # Introduce a random delay between 3 and 7 seconds
        time.sleep(random.uniform(3, 7))

# Run the main function asynchronously
asyncio.get_event_loop().run_until_complete(main())
