import requests  # Import requests module for making HTTP requests
from dotenv import load_dotenv  # Import function to load environment variables from a .env file
import os  # Import os module to interact with the operating system

# Load environment variables from a .env file
load_dotenv()

# Function to check the robots.txt file of a given URL
def check_robots_txt(url):
    robots_url = f"{url}/robots.txt"  # Construct the URL for robots.txt
    response = requests.get(robots_url)  # Send a GET request to the robots.txt URL
    if response.status_code == 200:  # Check if the request was successful
        print(response.text)  # Print the content of robots.txt
    else:
        print("Could not access the robots.txt file")  # Print an error message if the request failed

# Get the domain URL from environment variables
domain = os.getenv('URL_DOMAIN')
# Check the robots.txt file of the domain
check_robots_txt(domain)
