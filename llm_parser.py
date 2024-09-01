import asyncio
from langchain_ollama import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate
from bs4 import BeautifulSoup
import re

template = (
    "You are tasked with extracting specific information from the following text content: {dom_content}. "
    "Please follow these instructions carefully: \n\n"
    "1. **Extract Information:** Only extract the information that directly matches the provided description: {parsed_data}. "
    "2. **No Extra Content:** Do not include any additional text, comments, or explanations in your response. "
    "3. **Empty Response:** If no information matches the description, return an empty string ('')."
    "4. **Direct Data Only:** Your output should contain only the data that is explicitly requested, with no other text."
)

model = OllamaLLM(model="llama3.1")


def parse_generic_content(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    return {
        'title': extract_title(soup),
        'description': extract_description(soup),
        'prices': extract_prices(soup),
        'products': extract_products(soup),
        'articles': extract_articles(soup),
        'links': extract_links(soup)
    }


def extract_title(soup):
    title = soup.title.string if soup.title else None
    if not title:
        title = soup.find('h1')
        title = title.text.strip() if title else None
    return title


def extract_description(soup):
    meta_desc = soup.find('meta', attrs={'name': 'description'})
    if meta_desc:
        return meta_desc.get('content')
    first_p = soup.find('p')
    return first_p.text.strip() if first_p else None


def extract_prices(soup):
    price_patterns = [
        r'\$\d+(?:\.\d{2})?',
        r'USD\s*\d+(?:\.\d{2})?',
        r'\d+(?:\.\d{2})?\s*(?:USD|dollars)'
    ]
    prices = []
    for pattern in price_patterns:
        prices.extend(re.findall(pattern, soup.text))
    return list(set(prices))


def extract_products(soup):
    products = []
    product_containers = soup.find_all(['div', 'li'], class_=lambda x: x and 'product' in x.lower())
    for container in product_containers:
        product = {}
        product['name'] = container.find(['h2', 'h3', 'h4'])
        product['name'] = product['name'].text.strip() if product['name'] else None
        product['price'] = container.find(text=re.compile(r'\$\d+(?:\.\d{2})?'))
        product['description'] = container.find('p')
        product['description'] = product['description'].text.strip() if product['description'] else None
        if product['name'] or product['price']:
            products.append(product)
    return products


def extract_articles(soup):
    articles = []
    article_containers = soup.find_all(['article', 'div'], class_=lambda x: x and 'article' in x.lower())
    for container in article_containers:
        article = {}
        article['title'] = container.find(['h2', 'h3'])
        article['title'] = article['title'].text.strip() if article['title'] else None
        article['summary'] = container.find('p')
        article['summary'] = article['summary'].text.strip() if article['summary'] else None
        article['link'] = container.find('a')
        article['link'] = article['link']['href'] if article['link'] and article['link'].has_attr('href') else None
        if article['title'] or article['summary']:
            articles.append(article)
    return articles


def extract_links(soup):
    return [{'text': a.text.strip(), 'href': a['href']} for a in soup.find_all('a', href=True)]


async def async_ollama_parser(data_bits, parsed_data, progress_callback=None):
    prompt = ChatPromptTemplate.from_template(template)
    chain = prompt | model

    async def process_bit(bits, i):
        response = await chain.ainvoke({"dom_content": bits, "parsed_data": parsed_data})
        if progress_callback:
            progress = int((i / total_bits) * 100)
            progress_callback(progress, f"Parsing batch {i} of {total_bits}")
        return response

    total_bits = len(data_bits)
    tasks = [process_bit(bits, i) for i, bits in enumerate(data_bits, start=1)]
    results = await asyncio.gather(*tasks)

    if progress_callback:
        progress_callback(100, "Parsing complete!")

    return "\n".join(results)


def ollama_parser(data_bits, parsed_data, progress_callback=None):
    return asyncio.run(async_ollama_parser(data_bits, parsed_data, progress_callback))


async def async_parse_with_progress(html_content, parsed_data, progress_callback):
    try:
        progress_callback(0, "Starting parsing...")
        generic_data = parse_generic_content(html_content)

        progress_callback(50, "Performing specific parsing...")
        specific_data = await async_ollama_parser([html_content], parsed_data, progress_callback)

        progress_callback(100, "Parsing complete!")

        return {
            'generic_data': generic_data,
            'specific_data': specific_data
        }
    except Exception as e:
        progress_callback(100, f"Error during parsing: {str(e)}")
        return None


def parse_with_progress(html_content, parsed_data, progress_callback):
    return asyncio.run(async_parse_with_progress(html_content, parsed_data, progress_callback))