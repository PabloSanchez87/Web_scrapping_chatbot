import os  # Import the OS module to interact with the operating system
import requests  # Import requests module for making HTTP requests
from lxml import etree  # Import lxml for XML parsing
import re  # Import the regular expression module for string manipulation
from urllib.parse import urljoin  # Import urljoin for URL parsing and joining
from requests.adapters import HTTPAdapter  # Import HTTPAdapter for configuring HTTP sessions
from urllib3.util.retry import Retry  # Import Retry for handling retries in HTTP requests
import time  # Import time module to handle delays
import random  # Import random module for generating random numbers
from bs4 import BeautifulSoup  # Import BeautifulSoup for parsing HTML
from dotenv import load_dotenv  # Import function to load environment variables from a .env file

# Load environment variables from a .env file
load_dotenv()

# Configuration
sitemap_file_path = 'sitemap.xml'  # Path to the sitemap file
domain = os.getenv('URL_DOMAIN')  # Get the domain URL from environment variables
output_dir = "pdf_reports"  # Directory to save the PDFs
error_log_path = 'errores.txt'  # Path to the error log file
os.makedirs(output_dir, exist_ok=True)  # Create the output directory if it doesn't exist

# List of User-Agents for rotation
user_agents = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36",
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:89.0) Gecko/20100101 Firefox/89.0"
]

# Function to clean the XML content
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
        
        # Filter URLs containing '/reports/'
        urls = [loc.text for loc in loc_tags if '/reports/' in loc.text]
        print(f"Filtered URLs extracted from sitemap: {len(urls)}")
        return urls
    except Exception as e:
        print(f"Error reading the sitemap: {e}")
        return []

# Function to download PDF with SSL verification
def download_pdf(url, output_path):
    try:
        # Configure the HTTP session with retries
        session = requests.Session()
        retries = Retry(total=5, backoff_factor=1, status_forcelist=[502, 503, 504])
        session.mount('https://', HTTPAdapter(max_retries=retries))
        headers = {'User-Agent': random.choice(user_agents)}
        response = session.get(url, headers=headers, verify=True)
        if response.status_code == 200:
            with open(output_path, 'wb') as f:
                f.write(response.content)
            print(f"Downloaded PDF: {output_path}")
        else:
            log_error(url, f"Status Code: {response.status_code}")
    except requests.exceptions.RequestException as e:
        log_error(url, str(e))
    except requests.exceptions.SSLError as ssl_e:
        log_error(url, f"SSL Error: {ssl_e}")

# Function to log errors
def log_error(url, error_message):
    with open(error_log_path, 'a') as f:
        f.write(f"{url}: {error_message}\n")
    print(f"Logged error: {url} - {error_message}")

# Function to scrape and download PDFs from a page
def scrape_and_download_pdfs(page_url):
    try:
        headers = {'User-Agent': random.choice(user_agents)}
        response = requests.get(page_url, headers=headers)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            pdf_links = soup.find_all('a', href=True)
            if not pdf_links:
                log_error(page_url, "No PDF links found")
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

# Get all the URLs from the sitemap
filtered_sitemap_urls = get_filtered_sitemap_urls(sitemap_file_path)

print(f"Extracted URLs from sitemap: {len(filtered_sitemap_urls)}")

# Process each URL and download the PDFs
for url in filtered_sitemap_urls:
    print(f"Processing URL: {url}")
    scrape_and_download_pdfs(url)
    # Introduce a random delay between 3 and 7 seconds
    time.sleep(random.uniform(3, 7))
