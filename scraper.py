import logging
from selenium.webdriver import Remote, ChromeOptions
from selenium.webdriver.chromium.remote_connection import ChromiumRemoteConnection
import requests
from bs4 import BeautifulSoup
import os
from dotenv import load_dotenv
import time
from typing import Callable, Tuple, List

load_dotenv()

SBR_WEBDRIVER = os.getenv('CLOUD_DRIVER')

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def scrape_website(site):
    logger.info(f"Scraping website: {site}")

     # try with Selenium
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


def scrape_with_progress(url: str, progress_callback: Callable[[int, str], None]) -> Tuple[str, List[str]]:
    progress_callback(0, "Initializing scraper...")
    time.sleep(1)  # Simulate initialization time

    progress_callback(20, "Fetching webpage...")
    html_content = scrape_website(url)
    if html_content is None:
        raise Exception("Failed to fetch webpage content")

    progress_callback(40, "Extracting content...")
    extracted_content = extract_url(html_content)

    progress_callback(60, "Cleaning data...")
    cleaned_content = clean_url(extracted_content)

    progress_callback(80, "Preparing for analysis...")
    data_bits = batch_max_url(cleaned_content)

    progress_callback(100, "Scraping complete!")

    return cleaned_content, data_bits


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
