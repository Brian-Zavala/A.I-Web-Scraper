import streamlit as st
from streamlit_lottie import st_lottie
import requests
from scraper import scrape_website, extract_url, clean_url, batch_max_url, parse_with_progress
from llm_parser import ollama_parser
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import time
import base64
import logging

st.set_page_config(layout="wide", page_title="AI Web Scraper & Analyzer", page_icon="🌐", initial_sidebar_state="expanded")

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Download necessary NLTK data
@st.cache_resource
def download_nltk_data():
    nltk.download('punkt', quiet=True)
    nltk.download('stopwords', quiet=True)


download_nltk_data()

# Set page config

# Initialize session state variables
if 'cleaned_content' not in st.session_state:
    st.session_state.cleaned_content = None
if 'data_bits' not in st.session_state:
    st.session_state.data_bits = None
if 'parsed_result' not in st.session_state:
    st.session_state.parsed_result = None
if 'url' not in st.session_state:
    st.session_state.url = ""
if 'scraping_complete' not in st.session_state:
    st.session_state.scraping_complete = False
if 'parser_input' not in st.session_state:
    st.session_state.parser_input = ""


# Function to load Lottie animation
def load_lottieurl(url: str):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()


# Function to get image as base64
def get_image_as_base64(file):
    with open(file, "rb") as f:
        return base64.b64encode(f.read()).decode()

# Set background image
background_image = get_image_as_base64("gradient_blue.jpg")
st.markdown(
    f"""
    <style>
    .stApp {{
        background-image: url("data:image/jpg;base64,{background_image}");
        background-size: cover;
    }}
    </style>
    """,
    unsafe_allow_html=True
)


# Function to generate word cloud
def generate_wordcloud(text):
    try:
        stop_words = set(stopwords.words('english'))
        word_tokens = word_tokenize(text)
        filtered_text = [word.lower() for word in word_tokens if word.isalnum() and word.lower() not in stop_words]
        wordcloud = WordCloud(width=800, height=400, background_color='white').generate(' '.join(filtered_text))
        return wordcloud
    except Exception as e:
        logger.error(f"Error in word cloud generation: {str(e)}")
        return None


# Function to scrape website with progress updates
def scrape_with_progress(url, progress_callback):
    progress_callback(0, "Initializing scraper...")
    time.sleep(1)  # Simulate initialization time

    progress_callback(20, "Fetching webpage...")
    html_content = scrape_website(url)

    progress_callback(40, "Extracting content...")
    extracted_content = extract_url(html_content)

    progress_callback(60, "Cleaning data...")
    cleaned_content = clean_url(extracted_content)

    progress_callback(80, "Preparing for analysis...")
    data_bits = batch_max_url(cleaned_content)

    progress_callback(100, "Scraping complete!")

    return cleaned_content, data_bits


# Custom CSS for animations and styling
st.markdown("""
<style>
@keyframes pulse {
    0% { transform: scale(1); }
    50% { transform: scale(1.05); }
    100% { transform: scale(1); }
}
.pulse {
    animation: pulse 2s infinite;
}
.stButton>button {
    color: #4F8BF9;
    border-radius: 20px;
    height: 3em;
    width: 200px;
}
.stTextInput>div>div>input {
    color: #4F8BF9;
}
</style>
""", unsafe_allow_html=True)


def main():
    def main():
        st.title("AI-Powered Web Scraper & Analyzer")

        url = st.text_input("Enter a URL to scrape:", "https://example.com")
        parse_description = st.text_area("What should I look for in this data?", "Extract all product names and prices")

        if st.button('Scrape and Analyze'):
            progress_bar = st.progress(0)
            status_text = st.empty()

            def progress_callback(progress, status):
                progress_bar.progress(progress)
                status_text.text(status)

            scraped_content = scrape_with_progress(url, progress_callback)

            if scraped_content:
                st.success("Scraping completed successfully!")
                st.subheader("Scraped Content Preview")
                st.text(scraped_content[:500] + "...")  # Show first 500 characters

                st.subheader("Parsing Content")
                result = parse_with_progress(scraped_content, parse_description, progress_callback)

                if result:
                    st.success("Parsing completed successfully!")
                    st.subheader("Generic Data")
                    st.write(result['generic_data'])
                    st.subheader("Specific Parsed Data")
                    st.write(result['specific_data'])
                else:
                    st.error("Failed to parse the scraped content.")
            else:
                st.error("Failed to scrape the website. Please try a different URL or try again later.")

    if __name__ == "__main__":
        main()