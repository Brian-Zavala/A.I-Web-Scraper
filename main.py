import streamlit as st
from streamlit_lottie import st_lottie
from JavaScript import brain_electrical_signals_background
import requests
from scraper import scrape_with_progress
from llm_parser import groq_parser, format_parsed_result, get_preview
import nltk
import ssl
from nltk.corpus import stopwords
from nltk.tokenize import PunktSentenceTokenizer, word_tokenize
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import base64
import logging

st.set_page_config(layout="wide", page_title="AI Web Scraper & Analyzer", page_icon="🌐", initial_sidebar_state="auto")

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def download_nltk_data():
    try:
        nltk.download('punkt', quiet=True, raise_on_error=True)
        nltk.download('punkt_tab', quiet=True, raise_on_error=True)
        nltk.download('stopwords', quiet=True, raise_on_error=True)
    except ssl.SSLError:
        st.error("SSL Error occurred. NLTK data couldn't be downloaded securely.")
        st.info("You may need to download NLTK data manually or check your internet connection.")
    except Exception as e:
        st.error(f"An error occurred while downloading NLTK data: {str(e)}")
        st.info("You may need to download NLTK data manually or check your internet connection.")


# Call this function at the start of your app
download_nltk_data()

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
if 'file_format' not in st.session_state:
    st.session_state.file_format = 'txt'


# Function to load Lottie animation
def load_lottieurl(url: str):
    try:
        r = requests.get(url)
        if r.status_code != 200:
            return None
        return r.json()
    except Exception as e:
        logger.error(f"Error loading Lottie animation: {str(e)}")
        return None


# Load Lottie animations
lottie_analyzing = load_lottieurl("https://lottie.host/e7b1797e-f02a-44be-b28f-c3e26c69fbd3/4PF5hVXPST.json")
lottie_robot = load_lottieurl("https://lottie.host/2945d2be-6612-4bc3-8ffc-4bbaa755045b/y0olOO2xO7.json")
lottie_sidebar = load_lottieurl("https://lottie.host/3af8aa11-aec4-4661-98a6-6396ff474e0f/YIpGN6tsQ9.json")


# Function to get image as base64
def get_image_as_base64(file):
    try:
        with open(file, "rb") as f:
            return base64.b64encode(f.read()).decode()
    except Exception as e:
        logger.error(f"Error loading background image: {str(e)}")
        return None


# Set background image
background_image = get_image_as_base64("gradient_blue.jpg")
if background_image:
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
        sent_tokenizer = PunktSentenceTokenizer()
        sentences = sent_tokenizer.tokenize(text)
        word_tokens = [word for sentence in sentences for word in word_tokenize(sentence)]
        filtered_text = [word.lower() for word in word_tokens if word.isalnum() and word.lower() not in stop_words]
        wordcloud = WordCloud(width=800, height=400, background_color='white').generate(' '.join(filtered_text))
        return wordcloud
    except Exception as e:
        st.error(f"An error occurred while generating the word cloud: {str(e)}")
        return None


# Add custom CSS
st.markdown("""
     <style>

     [data-testid="stHeader"] {
         background-color: rgba(0,0,0,0.5);
     }

     .stApp > header {
         background-color: transparent;
     }

     </style>
 """, unsafe_allow_html=True)

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

# Custom CSS for animations and styling
st.markdown("""
<style>
@keyframes float {
    0% { transform: translateY(0px); }
    50% { transform: translateY(-10px); }
    100% { transform: translateY(0px); }
}
.floating { animation: float 3s ease-in-out infinite; }
.stButton>button {
    color: #4F8BF9;
    border-radius: 20px;
    height: 3em;
    width: 100%;
}
</style>
""", unsafe_allow_html=True)

# Add this to the top of your main.py file, after the existing custom CSS

st.markdown("""
<style>

    .stApp > header {
        background-color: transparent;
    }
    .stApp {
        margin-top: -150px;
    }
    .stSidebar .sidebar-content {
        padding-top: 0rem;
    }
    .stSidebar {
        margin-top: 125px;
    }
    .stTitle {
        margin-top: -50px !important;
    }-
    h1 {
        margin-top: 10px;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 2px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: #0E1117;
        border-radius: 4px 4px 0 0;
        gap: 1px;
        padding-top: 10px;
        padding-bottom: 10px;
    }
    .stTabs [aria-selected="true"] {
        background-color: #262730;
    }
</style>
""", unsafe_allow_html=True)


# Main app
def main():
    # Sidebar for navigation
    with st.sidebar:
        page = st.sidebar.radio("Go to", ["Home", "Scraper & Analyzer", "About"])

        st.markdown("""
        <h1 style='text-align: center; color: #4F8BF9;'>Scrape websites with ease</h1>
        <h1 style='text-align: center; color: #4F8BF9;'>Analyze content using cutting-edge AI (powered by Groq)</h1>
        <h1 style='text-align: center; color: #4F8BF9;'>Visualize data with interactive charts</h1>
        """, unsafe_allow_html=True)

    if page == "Home":
        st.markdown("<h1 class='pulse'>Groq A.I Web Scraper & Visualizer</h1>", unsafe_allow_html=True)
        st.write("This app combines the power of web scraping, Groq AI, and interactive visualizations.")
        if lottie_robot:
            st_lottie(lottie_robot, quality="high", speed=1, height=300, key="robot")
        else:
            st.image("https://via.placeholder.com/300x200?text=AI+Web+Scraper", use_column_width=True)
        brain_electrical_signals_background()


    elif page == "Scraper & Analyzer":
        st.title("🌐 AI-Powered Web Scraper & Analyzer")

        # Scraping section
        st.markdown("<h3 class='pulse'>Enter a URL to begin your web exploration journey!</h3>", unsafe_allow_html=True)
        st.session_state.url = st.text_input("", value=st.session_state.url, placeholder="https://example.com")

        if st.button('🚀 Launch Scraper', key='scrape_button'):
            if st.session_state.url:
                progress_bar = st.progress(0)
                status_text = st.empty()
                st.info(
                    "Note: Some websites may block our scraper. If you encounter issues, try a different website or check back later.")

                def update_progress(progress, status):
                    progress_bar.progress(progress)
                    status_text.text(status)

                try:
                    with st.spinner("Scraping please wait..."):
                        st.session_state.cleaned_content, st.session_state.data_bits = scrape_with_progress(
                            st.session_state.url, update_progress)
                    if st.session_state.cleaned_content is None:
                        st.warning("⚠️ The website denied access to our scraper. Unable to retrieve content.")
                    else:
                        st.success("🎉 Scraping completed successfully!")
                        st.session_state.scraping_complete = True

                    # Display a sample of the cleaned content
                    with st.expander("View Scraped Content"):
                        st.text_area("Cleaned Content", st.session_state.cleaned_content[:1000] + "...",
                                     height=200)

                except Exception as e:
                    logger.error(f"Error during scraping: {str(e)}")
                    st.error(f"🚫 This website is stubborn please try another URL: {str(e)}")
                    st.session_state.scraping_complete = False

        # Analysis section
        if st.session_state.get('scraping_complete', False):
            st.subheader("🧠 AI-Powered Analysis")
            st.session_state.parser_input = st.text_area(
                "What information would you like to extract from the scraped content?",
                value=st.session_state.parser_input,
                placeholder="e.g., Extract all product names and prices, or summarize the main topics"
            )

            if st.button('🔮 Analyze', key='parse_button'):
                if st.session_state.parser_input:
                    with st.expander("🔬 Analysis Dashboard", expanded=True):
                        st.markdown("<h3 class='pulse'>🧙‍♂️ The AI is weaving its magic...</h3>",
                                    unsafe_allow_html=True)
                        if lottie_analyzing:
                            st_lottie(lottie_analyzing, speed=1, height=200, key="analyzing")
                    try:
                        progress_bar = st.progress(0)
                        status_text = st.empty()

                        def update_progress(progress, status):
                            progress_bar.progress(progress)
                            status_text.text(status)

                        st.session_state.parsed_result = groq_parser(
                            st.session_state.data_bits,
                            st.session_state.parser_input,
                            update_progress
                        )

                        if st.session_state.parsed_result:
                            st.success("✨ Analysis complete! Behold the insights!")
                            st.subheader("🎨 Scraped Insights")
                            st.write(st.session_state.parsed_result)

                            # Display any errors that occurred during analysis
                            errors = [result for result in st.session_state.parsed_result if "error" in result]
                            if errors:
                                st.warning("Some parts of the analysis encountered errors:")
                                for error in errors:
                                    st.error(error["error"])
                        else:
                            st.warning("The analysis did not produce any results. The parsed content might be empty.")
                    except Exception as e:
                        st.error(f"An error occurred during analysis: {str(e)}")
                        logger.exception("Error during analysis")

            # Display download options if parsed result exists
            if st.session_state.get('parsed_result'):
                st.subheader("📥 Download Options")

                # File format selector using radio buttons
                st.session_state.file_format = st.radio(
                    "Select file format for download",
                    options=['txt', 'json'],
                    format_func=lambda x: f".{x} file",
                    horizontal=True
                )

                # Format the parsed result for download
                formatted_result = format_parsed_result(st.session_state.parsed_result, st.session_state.file_format)

                # Check file size
                file_size = len(formatted_result.encode('utf-8'))
                max_size = 200 * 1024 * 1024  # 200 MB limit

                if file_size > max_size:
                    st.warning(
                        "⚠️ The parsed result is too large to download directly. Consider breaking it into smaller parts.")
                else:
                    # Preview of downloadable content
                    st.subheader("🔍 Preview of Downloadable Content")
                    st.code(get_preview(formatted_result), language=st.session_state.file_format)

                    # Add download button for parsed results
                    st.download_button(
                        label=f"📥 Download Parsed Results (.{st.session_state.file_format})",
                        data=formatted_result,
                        file_name=f"parsed_results.{st.session_state.file_format}",
                        mime=f"text/{st.session_state.file_format}"
                    )

            # Word Cloud
            if st.session_state.get('cleaned_content'):
                st.subheader("☁️ Word Cloud")
                wordcloud = generate_wordcloud(st.session_state.cleaned_content)
                if wordcloud:
                    plt.figure(figsize=(10, 5))
                    plt.imshow(wordcloud, interpolation='bilinear')
                    plt.axis('off')
                    st.pyplot(plt)
                else:
                    st.warning("🌪️ Oops! The word cloud generator hit a snag. But don't worry, the show must go on!")

    elif page == "About":
        st.markdown("<h1 class='pulse'>About</h1>", unsafe_allow_html=True)
        st.write("""
        This advanced web scraper and analyzer combines cutting-edge technologies to provide insights from web content:

        - **Web Scraping**: Extracts content from any website you specify.
        - **Groq AI Integration**: Utilizes the power of Groq AI for natural language processing tasks.
        - **Interactive Visualizations**: Presents data through word clouds and interactive charts.
        - **Custom Analysis**: Allows you to specify exactly what information you want to extract or analyze.

        Enjoy exploring the web with AI-powered analysis!
        """)

        # Team info with avatars
        st.subheader("Our Team")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.write("")
            st.image(
                "https://img.icons8.com/?size=100&id=GBu1KXnCZZ8j&format=png&color=000000", width=146)
            st.write("Groq - AI Expert")
        with col2:
            st.image("https://api.dicebear.com/9.x/personas/svg?seed=Maggie", width=150)
            st.write("Claudia - Web Developer")
        with col3:
            st.image("https://api.dicebear.com/9.x/personas/svg?seed=Bella", width=150)
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
        🚀 Powered by Groq AI | © 2024 Web Explorer
    </div>
    """, unsafe_allow_html=True)

st.markdown(
    """
    <style>
/* Animated Sidebar Styles */
.stSidebar {
    background: linear-gradient(145deg, #0e1117, #1a1f2c);
    box-shadow: 0 4px 30px rgba(0, 0, 0, 0.1);
    backdrop-filter: blur(5px);
    -webkit-backdrop-filter: blur(5px);
    border: 1px solid rgba(79, 139, 249, 0.3);
}

/* Glow effect for sidebar content */
.stSidebar [data-testid="stSidebarNav"] {
    position: relative;
    z-index: 1;
}

.stSidebar [data-testid="stSidebarNav"]::before {
    content: "";
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: radial-gradient(circle at center, rgba(79, 139, 249, 0.2) 0%, transparent 70%);
    filter: blur(20px);
    opacity: 0;
    z-index: -1;
    animation: glow 3s infinite alternate;
}

@keyframes glow {
    0% {
        opacity: 0.3;
        transform: scale(0.8);
    }
    100% {
        opacity: 0.7;
        transform: scale(1.2);
    }
}

/* Custom radio button styles */
.stRadio > div[role="radiogroup"] > label > div:first-child {
    background-color: transparent;
    border: 2px solid #4F8BF9;
}

.stRadio > div[role="radiogroup"] > label > div:first-child > div {
    background-color: transparent;
    border-color: transparent;
}

.stRadio > div[role="radiogroup"] > label input:checked + div:first-child {
    background-color: #4F8BF9;
}

.stRadio > div[role="radiogroup"] > label input:checked + div:first-child > div {
    background-color: white;
    border-color: white;
}

/* Animated radio buttons */
.stRadio > label {
    transition: all 0.3s ease;
}

.stRadio > label:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 8px rgba(79, 139, 249, 0.2);
}

.stRadio > label > div {
    position: relative;
    overflow: hidden;
}

.stRadio > label > div::after {
    content: "";
    position: absolute;
    top: 50%;
    left: 50%;
    width: 5px;
    height: 5px;
    background: rgba(79, 139, 249, 0.7);
    opacity: 0;
    border-radius: 100%;
    transform: scale(1);
    animation: ripple 1s infinite;
}

@keyframes ripple {
    0% {
        transform: scale(0);
        opacity: 1;
    }
    100% {
        transform: scale(20);
        opacity: 0;
    }
}

/* Enhance sidebar header */
.stSidebar [data-testid="stSidebarNav"] > div:first-child {
    background: linear-gradient(90deg, #4F8BF9, #3a7bd5);
    padding: 1rem;
    margin-bottom: 1rem;
    border-radius: 0.5rem;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.stSidebar [data-testid="stSidebarNav"] > div:first-child h1 {
    color: white;
    text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
    animation: colorShift 5s infinite alternate;
}

@keyframes colorShift {
    0% {
        color: #ffffff;
    }
    50% {
        color: #e0f7fa;
    }
    100% {
        color: #b3e5fc;
    }
}    </style>
    """,
    unsafe_allow_html=True
)


if __name__ == "__main__":
    main()
