import logging
from selenium.webdriver import Remote, ChromeOptions
from selenium.webdriver.chromium.remote_connection import ChromiumRemoteConnection
import requests
from bs4 import BeautifulSoup
import os
from dotenv import load_dotenv
import time

load_dotenv()

SBR_WEBDRIVER = os.getenv('CLOUD_DRIVER')

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def scrape_website(site):
    logger.info(f"Scraping website: {site}")

    # First, try a simple request
    try:
        response = requests.get(site, timeout=30)
        if response.status_code == 200:
            logger.info("Successfully fetched the website using requests")
            return response.text
    except Exception as e:
        logger.warning(f"Failed to fetch website using requests: {str(e)}")

    # If simple request fails, try with Selenium
    chrome_options = ChromeOptions()
    try:
        sbr_connection = ChromiumRemoteConnection(SBR_WEBDRIVER, 'goog', 'chrome')
        with Remote(sbr_connection, options=chrome_options) as driver:
            driver.get(site)
            logger.info('Waiting for page to load...')
            time.sleep(10)  # Wait for 10 seconds
            page_source = driver.page_source
            if page_source:
                logger.info("Successfully scraped the website using Selenium")
                return page_source
            else:
                logger.error("Failed to get page source")
    except Exception as e:
        logger.error(f"Error during Selenium scraping: {str(e)}")

    return None


def scrape_with_progress(url, progress_callback):
    try:
        progress_callback(0, "Initializing scraper...")
        time.sleep(1)  # Simulate initialization time

        progress_callback(10, "Connecting to website...")
        DOM = scrape_website(url)
        if DOM is None:
            raise Exception("Failed to retrieve page content")

        progress_callback(40, "Extracting content...")
        page_content = extract_url(DOM)
        if not page_content:
            raise Exception("Failed to extract content from DOM")

        progress_callback(70, "Cleaning and processing data...")
        clean_page = clean_url(page_content)
        if not clean_page:
            raise Exception("Failed to clean and process data")

        progress_callback(90, "Finalizing...")
        time.sleep(1)  # Simulate finalization time
        progress_callback(100, "Scraping complete!")

        return clean_page
    except Exception as e:
        logger.error(f"Error during scraping: {str(e)}")
        progress_callback(100, f"Error: {str(e)}")
        return None


def extract_url(page):
    if not page:
        return ""
    soup = BeautifulSoup(page, 'html.parser')
    return str(soup.body) if soup.body else ""


def clean_url(body_text):
    if not body_text:
        return ""
    soup = BeautifulSoup(body_text, 'html.parser')
    for element in soup(["style", "script"]):
        element.decompose()
    return '\n'.join(line.strip() for line in soup.get_text(separator='\n').splitlines() if line.strip())


def batch_max_url(content, max_length=512):
    return [content[i:i + max_length] for i in range(0, len(content), max_length)]
