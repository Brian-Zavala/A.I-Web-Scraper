from langchain_ollama import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate

# Optimized template for more precise parsing
template = """
You are an advanced AI assistant specializing in extracting and analyzing web content. Your task is to process the following text content from a webpage and provide a concise, accurate response based on the specific request.

Webpage Content:
{dom_content}

User Request:
{parsed_data}

Instructions:
1. Carefully analyze the webpage content.
2. Focus solely on extracting information that directly answers the user's request.
3. Provide a structured and concise response.
4. If the requested information is not present, clearly state that it's not available.
5. Do not include any additional commentary or explanations unless specifically requested.
6. Format your response for easy readability (use bullet points or numbered lists if appropriate).
7. If asked to summarize, aim for brevity while capturing key points.
8. For numerical data, present it clearly and, if possible, in a tabular format.
9. For named entities, ensure accurate identification and grouping (e.g., people, organizations, locations).
10. Maintain objectivity and avoid inferring information not explicitly stated in the content.

Your response:
"""

model = OllamaLLM(model="llama3.1")


def ollama_parser(data_bits, parsed_data, progress_callback=None):
    prompt = ChatPromptTemplate.from_template(template)
    chain = prompt | model

    results = []
    total_bits = len(data_bits)

    for i, bits in enumerate(data_bits, start=1):
        if progress_callback:
            progress = int((i / total_bits) * 100)
            progress_callback(progress, f"Parsing batch {i} of {total_bits}")

        response = chain.invoke(
            {"dom_content": bits, "parsed_data": parsed_data}
        )
        results.append(response.content)

    if progress_callback:
        progress_callback(100, "Parsing complete!")

    return "\n".join(results)