import logging
from llm_parser import parse_with_progress
from selenium.webdriver import Remote, ChromeOptions
from selenium.webdriver.chromium.remote_connection import ChromiumRemoteConnection
from selenium.common.exceptions import WebDriverException, TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import os
from dotenv import load_dotenv
import time

load_dotenv()

SBR_WEBDRIVER = os.getenv('CLOUD_DRIVER')

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

MAX_RETRIES = 3
WAIT_TIME = 20


def scrape_website(site):
    logger.info(f"Scraping website: {site}")
    chrome_options = ChromeOptions()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--disable-javascript")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36")

    sbr_connection = ChromiumRemoteConnection(SBR_WEBDRIVER, 'goog', 'chrome')

    for attempt in range(MAX_RETRIES):
        try:
            with Remote(sbr_connection, options=chrome_options) as driver:
                driver.set_page_load_timeout(WAIT_TIME)
                driver.get(site)
                logger.info('Waiting for page to load...')

                # Wait for the body element to be present
                WebDriverWait(driver, WAIT_TIME).until(
                    EC.presence_of_element_located((By.TAG_NAME, "body"))
                )

                # Scroll the page multiple times to trigger lazy-loading content
                for _ in range(5):
                    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                    time.sleep(2)

                # Wait for specific Bloomberg content
                try:
                    WebDriverWait(driver, 20).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, ".story-list-story__info"))
                    )
                except TimeoutException:
                    logger.warning("Specific Bloomberg content not found. Page might not have loaded completely.")

                logger.info(f"Current URL: {driver.current_url}")

                # Get page source
                page_source = driver.execute_script("return document.documentElement.outerHTML;")

                if len(page_source) > 5000 and "Bloomberg" in page_source:
                    logger.info("Successfully scraped the website")
                    return page_source
                else:
                    logger.warning("Page source doesn't contain expected content.")

                logger.warning(f"Attempt {attempt + 1} failed. Retrying...")
                time.sleep(10)  # Increased wait time before retrying

        except TimeoutException:
            logger.error(f"Timeout waiting for page to load on attempt {attempt + 1}")
        except WebDriverException as e:
            logger.error(f"WebDriver exception on attempt {attempt + 1}: {str(e)}")

    logger.error("All attempts to scrape the website failed")
    return None


def scroll_page(driver):
    last_height = driver.execute_script("return document.body.scrollHeight")
    for i in range(3):  # Scroll 3 times
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)  # Wait for page to load
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height


def extract_url(page):
    if not page:
        return ""
    soup = BeautifulSoup(page, 'html.parser')
    return str(soup.body) if soup.body else ""


def clean_url(body_text):
    soup = BeautifulSoup(body_text, 'html.parser')
    for element in soup(["style", "script"]):
        element.decompose()
    return '\n'.join(line.strip() for line in soup.get_text(separator='\n').splitlines() if line.strip())


def batch_max_url(content, max_length=6000):
    return [content[i:i + max_length] for i in range(0, len(content), max_length)]


def scrape_and_parse(url, parsed_data, progress_callback):
    try:
        progress_callback(0, "Initializing scraper...")
        time.sleep(1)  # Simulate initialization time

        progress_callback(10, "Connecting to website...")
        DOM = scrape_website(url)
        if not DOM:
            raise Exception("Failed to retrieve page content")

        progress_callback(40, "Extracting content...")
        page_content = extract_url(DOM)
        if not page_content:
            raise Exception("Failed to extract content from DOM")

        progress_callback(70, "Cleaning and processing data...")
        clean_page = clean_url(page_content)
        if not clean_page:
            raise Exception("Failed to clean and process data")

        progress_callback(80, "Parsing data...")
        parsed_result = parse_with_progress(clean_page, parsed_data, progress_callback)

        progress_callback(100, "Scraping and parsing complete!")

        return parsed_result
    except Exception as e:
        logger.error("Error during scraping and parsing: %s", str(e))
        progress_callback(100, f"Error: {str(e)}")
        return None