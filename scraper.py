from selenium.webdriver import Remote, ChromeOptions
from selenium.webdriver.chromium.remote_connection import ChromiumRemoteConnection
from bs4 import BeautifulSoup
import os
from dotenv import load_dotenv
from functools import lru_cache
import time

load_dotenv()

SBR_WEBDRIVER = os.getenv('CLOUD_DRIVER')


@lru_cache(maxsize=32)
def scrape_website(site):
    print("Scraping website...")
    sbr_connection = ChromiumRemoteConnection(SBR_WEBDRIVER, 'goog', 'chrome')
    with Remote(sbr_connection, options=ChromeOptions()) as driver:
        driver.get(site)
        print('Waiting for CAPTCHA to solve...')
        solve_res = driver.execute('executeCdpCommand', {
            'cmd': 'Captcha.waitForSolve',
            'params': {'detectTimeout': 10000},
        })
        print('CAPTCHA solve status:', solve_res['value']['status'])
        print('Navigated! Scraping page content...')
        return driver.page_source

def extract_url(page):
    soup = BeautifulSoup(page, 'html.parser')
    return str(soup.body) if soup.body else ""

def clean_url(body_text):
    soup = BeautifulSoup(body_text, 'html.parser')
    for element in soup(["style", "script"]):
        element.decompose()
    return '\n'.join(line.strip() for line in soup.get_text(separator='\n').splitlines() if line.strip())

def batch_max_url(content, max_length=6000):
    return [content[i:i+max_length] for i in range(0, len(content), max_length)]


def scrape_with_progress(url, progress_callback):
    progress_callback(0, "Initializing scraper...")
    time.sleep(1)  # Simulate initialization time

    progress_callback(10, "Connecting to website...")
    DOM = scrape_website(url)
    progress_callback(40, "Extracting content...")

    page_content = extract_url(DOM)
    progress_callback(70, "Cleaning and processing data...")

    clean_page = clean_url(page_content)
    progress_callback(90, "Finalizing...")

    time.sleep(1)  # Simulate finalization time
    progress_callback(100, "Scraping complete!")

    return clean_page