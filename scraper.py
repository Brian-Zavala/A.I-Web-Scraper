import logging
from selenium.webdriver import Remote, ChromeOptions
from selenium.webdriver.chromium.remote_connection import ChromiumRemoteConnection
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, WebDriverException
from bs4 import BeautifulSoup
import os
from dotenv import load_dotenv
import time
from typing import Callable, Tuple, List
from retrying import retry

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Get WebDriver URL from environment variable
SBR_WEBDRIVER = os.getenv('CLOUD_DRIVER')


@retry(stop_max_attempt_number=3, wait_fixed=2000)
def scrape_website(site: str) -> str:
    logger.info(f"Scraping website: {site}")

    chrome_options = ChromeOptions()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920x1080")
    chrome_options.page_load_strategy = 'eager'

    # Remove the performance logging capability as it's not supported in this environment
    # chrome_options.set_capability('goog:loggingPrefs', {'performance': 'ALL'})

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
    progress_callback(0, "Initializing scraper...")
    time.sleep(1)  # Simulate initialization time

    progress_callback(20, "Fetching webpage...")
    html_content = scrape_website(url)
    if html_content is None:
        progress_callback(100, "Scraping failed")
        raise Exception("Failed to fetch webpage content")

    progress_callback(40, "Extracting content...")
    extracted_content = extract_url(html_content)

    progress_callback(60, "Cleaning data...")
    cleaned_content = clean_url(extracted_content)

    progress_callback(80, "Preparing for analysis...")
    data_bits = batch_max_url(cleaned_content)

    progress_callback(100, "Scraping complete!")

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


def scrape_with_progress(url: str, progress_callback: Callable[[int, str], None]) -> Tuple[str, List[str]]:
    progress_callback(0, "Initializing scraper...")
    time.sleep(1)  # Simulate initialization time

    progress_callback(20, "Fetching webpage...")
    html_content = scrape_website(url)
    if html_content is None:
        progress_callback(100, "Scraping failed")
        raise Exception("Failed to fetch webpage content")

    progress_callback(40, "Extracting content...")
    extracted_content = extract_url(html_content)

    progress_callback(60, "Cleaning data...")
    cleaned_content = clean_url(extracted_content)

    progress_callback(80, "Preparing for analysis...")
    data_bits = batch_max_url(cleaned_content)

    progress_callback(100, "Scraping complete!")

    return cleaned_content, data_bits


# Example usage
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