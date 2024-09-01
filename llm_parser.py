import asyncio
from langchain_ollama import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate
import logging

logger = logging.getLogger(__name__)

template = (
    "You are tasked with extracting specific information from the following text content: {dom_content}. "
    "Please follow these instructions carefully: \n\n"
    "1. **Extract Information:** Only extract the information that directly matches the provided description: {parsed_data}. "
    "2. **No Extra Content:** Do not include any additional text, comments, or explanations in your response. "
    "3. **Empty Response:** If no information matches the description, return an empty string ('')."
    "4. **Direct Data Only:** Your output should contain only the data that is explicitly requested, with no other text."
)

model = OllamaLLM(model="llama3.1")


async def async_ollama_parser(data_bits, parsed_data, progress_callback=None):
    prompt = ChatPromptTemplate.from_template(template)
    chain = prompt | model

    async def process_bit(bits, i):
        try:
            response = await chain.ainvoke({"dom_content": bits, "parsed_data": parsed_data})
            if progress_callback:
                progress = int((i / total_bits) * 100)
                progress_callback(progress, f"Parsing batch {i} of {total_bits}")
            return response
        except Exception as e:
            logger.error(f"Error processing batch {i}: {str(e)}")
            return f"Error in batch {i}: {str(e)}"

    total_bits = len(data_bits)
    tasks = [process_bit(bits, i) for i, bits in enumerate(data_bits, start=1)]
    results = await asyncio.gather(*tasks)

    if progress_callback:
        progress_callback(100, "Parsing complete!")

    return "\n".join(str(r) for r in results)


def ollama_parser(data_bits, parsed_data, progress_callback=None):
    try:
        return asyncio.run(async_ollama_parser(data_bits, parsed_data, progress_callback))
    except Exception as e:
        error_message = f"An error occurred during parsing: {str(e)}"
        logger.error(error_message)
        return error_message
