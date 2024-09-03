import logging

import streamlit
from selenium.webdriver import Remote, ChromeOptions
from selenium.webdriver.chromium.remote_connection import ChromiumRemoteConnection
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, WebDriverException
from bs4 import BeautifulSoup
import os
import time
from typing import Callable, Tuple, List
from retrying import retry
import random

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Get WebDriver URL from environment variable
SBR_WEBDRIVER = os.getenv('CLOUD_DRIVER')

user_agents = [
    'Mozilla/5.0 (Windows NT 11.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 11.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
    'Mozilla/5.0 (Windows NT 11.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 14_3_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 14_3_0) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15',
    'Mozilla/5.0 (X11; Linux x86_64; rv:121.0) Gecko/20100101 Firefox/121.0',
    'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:121.0) Gecko/20100101 Firefox/121.0',
    'Mozilla/5.0 (iPhone; CPU iPhone OS 17_2_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1',
    'Mozilla/5.0 (iPad; CPU OS 17_2_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1',
    'Mozilla/5.0 (Linux; Android 14; Pixel 8) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.6099.230 Mobile Safari/537.36'
]

languages = ['en-US,en;q=0.9', 'en-GB,en;q=0.8', 'es-ES,es;q=0.9']

@retry(stop_max_attempt_number=3, wait_fixed=2000)
def scrape_website(site: str) -> str:
    logger.info(f"Scraping website: {site}")
    chrome_options = ChromeOptions()
    chrome_options.add_argument(f"--user-agent={random.choice(user_agents)}")
    chrome_options.add_argument(f"--lang={random.choice(languages)}")
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.page_load_strategy = 'eager'
    chrome_options.platform_name = 'any'

    try:
        logger.info(f"Connecting to remote WebDriver: {SBR_WEBDRIVER}")
        sbr_connection = ChromiumRemoteConnection(SBR_WEBDRIVER, 'goog', 'chrome')
        with Remote(sbr_connection, options=chrome_options) as driver:
            logger.info("Successfully connected to remote WebDriver")
            logger.info(f"Navigating to: {site}")
            driver.get(site)

            wait = WebDriverWait(driver, 20)
            wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))

            page_source = driver.page_source
            if page_source is None:
                logger.error("Failed to get page source: page_source is None")
                return None

            if "access denied" in page_source.lower() or "captcha" in page_source.lower():
                logger.error("Possible blocking detected")
                return None

            logger.info("Successfully scraped the website using Selenium")



            return page_source
    except TimeoutException:
        logger.error("Timeout while loading the page")
    except WebDriverException as e:
        logger.error(f"WebDriver error: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        logger.error(f"URL being scraped: {site}")

    return None


def scrape_with_progress(url: str, progress_callback: Callable[[int, str], None]) -> Tuple[str, List[str]]:
    logger.info(f"Starting scrape_with_progress for URL: {url}")
    progress_callback(0, "Initializing scraper...")
    time.sleep(1)  # Simulate initialization time

    progress_callback(20, "Fetching webpage...")
    html_content = scrape_website(url)
    logger.info(f"HTML content fetched, length: {len(html_content) if html_content else 'None'}")
    if html_content is None:
        logger.error("Failed to fetch webpage content")
        progress_callback(100, "Scraping failed")
        raise Exception("Failed to fetch webpage content")

    progress_callback(40, "Extracting content...")
    extracted_content = extract_url(html_content)
    logger.info(f"Extracted content length: {len(extracted_content)}")

    progress_callback(60, "Cleaning data...")
    cleaned_content = clean_url(extracted_content)
    logger.info(f"Cleaned content length: {len(cleaned_content)}")

    progress_callback(80, "Preparing for analysis...")
    data_bits = batch_max_url(cleaned_content)
    logger.info(f"Number of data bits: {len(data_bits)}")

    progress_callback(100, "Scraping complete!")
    logger.info("Scraping process completed successfully")

    return cleaned_content, data_bits


def extract_url(page: str) -> str:
    if not page:
        return ""
    soup = BeautifulSoup(page, 'html.parser')
    return str(soup.body) if soup.body else ""


def clean_url(body_text: str) -> str:
    if not body_text:
        return ""
    soup = BeautifulSoup(body_text, 'html.parser')
    for element in soup(["style", "script"]):
        element.decompose()
    return '\n'.join(line.strip() for line in soup.get_text(separator='\n').splitlines() if line.strip())


def batch_max_url(content: str, max_length: int = 6000) -> List[str]:
    return [content[i:i + max_length] for i in range(0, len(content), max_length)]


if __name__ == "__main__":
    def print_progress(progress: int, message: str):
        print(f"Progress: {progress}% - {message}")


    url_to_scrape = "https://www.example.com"
    try:
        content, bits = scrape_with_progress(url_to_scrape, print_progress)
        print(f"Scraped content length: {len(content)}")
        print(f"Number of data bits: {len(bits)}")
    except Exception as e:
        print(f"Scraping failed: {str(e)}")