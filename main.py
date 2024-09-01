import streamlit as st
from streamlit_lottie import st_lottie
import requests
from scraper import scrape_website, extract_url, clean_url, batch_max_url
from llm_parser import ollama_parser
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import PunktTokenizer
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
        word_tokens = PunktTokenizer(text)
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


# Main app
def main():
    # Sidebar for navigation
    st.sidebar.title("Navigation")
    page = st.sidebar.radio("Go to", ["Home", "Scraper & Analyzer", "About"])

    # Load Lottie animation
    lottie_url = "https://assets5.lottiefiles.com/packages/lf20_fcfjwiyb.json"
    lottie_json = load_lottieurl(lottie_url)

    if page == "Home":
        st.title("Welcome to AI-Powered Web Scraper & Analyzer")
        st.write("This app combines the power of web scraping, Llama 3.1, and interactive visualizations.")
        st_lottie(lottie_json, speed=1, height=300, key="lottie")

        st.markdown("""
        ### 🚀 Explore the Web with AI

        Our advanced tool allows you to:
        - 🕷️ Scrape websites with ease
        - 🧠 Analyze content using cutting-edge AI
        - 📊 Visualize insights with interactive charts

        Get started by navigating to the 'Scraper & Analyzer' page!
        """)

    elif page == "Scraper & Analyzer":
        st.title("🌐 AI-Powered Web Scraper & Analyzer")

        # Scraping section
        st.markdown("<h3 class='pulse'>Enter a URL to begin your web exploration journey!</h3>", unsafe_allow_html=True)
        st.session_state.url = st.text_input("", value=st.session_state.url, placeholder="https://example.com")

        if st.button('🚀 Launch Scraper', key='scrape_button'):
            if st.session_state.url:
                progress_bar = st.progress(0)
                status_text = st.empty()

                def update_progress(progress, status):
                    progress_bar.progress(progress)
                    status_text.text(status)

                try:
                    st.session_state.cleaned_content, st.session_state.data_bits = scrape_with_progress(
                        st.session_state.url, update_progress)
                    st.success("🎉 Scraping completed successfully!")
                    st.session_state.scraping_complete = True

                    # Display a sample of the cleaned content
                    with st.expander("View Scraped Content Sample"):
                        st.text_area("Cleaned Content Sample", st.session_state.cleaned_content[:500] + "...",
                                     height=200)

                except Exception as e:
                    logger.error(f"Error during scraping: {str(e)}")
                    st.error(f"🚫 Oops! An error occurred during scraping: {str(e)}")
                    st.session_state.scraping_complete = False

        # Analysis section
        if st.session_state.get('scraping_complete', False):
            st.session_state.parser_input = st.text_area("🧠 What should I look for in this data?",
                                                         value=st.session_state.parser_input,
                                                         placeholder="e.g., Extract all product names and prices")

            if st.button('🔮 Analyze', key='parse_button'):
                if st.session_state.parser_input:
                    with st.expander("🔬 Analysis Dashboard", expanded=True):
                        st.markdown("<h3 class='pulse'>🧙‍♂️ The AI is weaving its magic...</h3>",
                                    unsafe_allow_html=True)
                        progress_bar = st.progress(0)
                        status_text = st.empty()

                        def update_progress(progress, status):
                            progress_bar.progress(progress)
                            status_text.text(status)

                        try:
                            logger.info(f"Number of data bits: {len(st.session_state.data_bits)}")
                            logger.info(f"Parser input: {st.session_state.parser_input}")

                            st.session_state.parsed_result = ollama_parser(st.session_state.data_bits,
                                                                           st.session_state.parser_input,
                                                                           update_progress)

                            st.success("✨ Analysis complete! Behold the insights!")

                            # Display parsed result
                            st.subheader("🎨 Parsed Insights")
                            st.write(st.session_state.parsed_result)

                            # Word Cloud
                            st.subheader("☁️ Word Cloud")
                            wordcloud = generate_wordcloud(st.session_state.parsed_result)
                            if wordcloud:
                                plt.figure(figsize=(10, 5))
                                plt.imshow(wordcloud, interpolation='bilinear')
                                plt.axis('off')
                                st.pyplot(plt)
                            else:
                                st.warning(
                                    "🌪️ Oops! The word cloud generator hit a snag. But don't worry, the show must go on!")

                            # Interactive Analysis Tools
                            st.subheader("🛠️ Interactive Analysis Tools")
                            tool = st.selectbox("Select an analysis tool",
                                                ["Sentiment Analysis", "Named Entity Recognition", "Topic Modeling"])

                            if tool == "Sentiment Analysis":
                                if st.button("📊 Analyze Sentiment"):
                                    with st.spinner("🎭 Detecting the mood of the text..."):
                                        sentiment_prompt = f"Analyze the sentiment of the following text and categorize it as positive, negative, or neutral. Provide a brief explanation for your categorization: {st.session_state.parsed_result[:1000]}..."
                                        sentiment_result = ollama_parser([sentiment_prompt], "Sentiment analysis")
                                        st.write(sentiment_result)

                            elif tool == "Named Entity Recognition":
                                if st.button("🏷️ Recognize Entities"):
                                    with st.spinner("🕵️ Identifying key players in the text..."):
                                        ner_prompt = f"Perform named entity recognition on the following text. Identify and list all person names, organizations, locations, and dates: {st.session_state.parsed_result[:1000]}..."
                                        ner_result = ollama_parser([ner_prompt], "Named Entity Recognition")
                                        st.write(ner_result)

                            elif tool == "Topic Modeling":
                                num_topics = st.slider("Number of topics", 2, 10, 5)
                                if st.button("🗂️ Generate Topics"):
                                    with st.spinner("🧩 Uncovering hidden themes..."):
                                        topic_prompt = f"Perform topic modeling on the following text. Identify {num_topics} main topics and list the top 5 keywords for each topic: {st.session_state.parsed_result}"
                                        topics = ollama_parser([topic_prompt], "Topic Modeling")
                                        st.write(topics)

                        except Exception as e:
                            logger.error(f"Error during parsing: {str(e)}")
                            st.error(f"🚫 The crystal ball clouded: {str(e)}")
                else:
                    st.warning("Please enter a request for analysis.")

    elif page == "About":
        st.title("About This App")
        st.write("""
        This advanced web scraper and analyzer combines cutting-edge technologies to provide insights from web content:

        - **Web Scraping**: Extracts content from any website you specify.
        - **Llama 3.1 Integration**: Utilizes the power of Llama 3.1 for natural language processing tasks.
        - **Interactive Visualizations**: Presents data through word clouds and interactive charts.
        - **Sentiment Analysis**: Determines the overall sentiment of the scraped content.
        - **Named Entity Recognition**: Identifies important entities in the text.
        - **Topic Modeling**: Discovers the main themes in the content.

        Enjoy exploring the web with AI-powered analysis!
        """)

        # Team info with avatars
        st.subheader("Our Team")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.image("https://api.dicebear.com/6.x/avataaars/svg?seed=Felix", width=150)
            st.write("Llama - AI Expert")
        with col2:
            st.image("https://api.dicebear.com/6.x/avataaars/svg?seed=Sophia", width=150)
            st.write("Claudia - Web Developer")
        with col3:
            st.image("https://api.dicebear.com/6.x/avataaars/svg?seed=Oliver", width=150)
            st.write("Brian - Data Scientist")

    # Footer
    st.markdown("""
    <style>
    .footer {
        position: fixed;
        left: 0;
        bottom: 0;
        width: 100%;
        background-color: #0E1117;
        color: white;
        text-align: center;
        padding: 10px;
        font-size: 14px;
    }
    </style>
    <div class="footer">
        🚀 Powered by AI magic and human curiosity | © 2024 Web Explorer
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()