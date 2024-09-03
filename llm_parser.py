import asyncio
import json

import streamlit
from groq import AsyncGroq
import os

api_key = os.environ.get("GROQ_API_KEY")
if api_key is None:
    raise ValueError("GROQ_API_KEY environment variable is not set")


def parse_response(response):
    try:
        # First, try to parse as JSON
        return json.loads(response)
    except json.JSONDecodeError:
        # If it's not valid JSON, return the raw text
        return {"raw_response": response}


@streamlit.cache_resource
class GroqParser:
    def __init__(self):
        self.client = AsyncGroq(api_key=api_key)

    async def analyze_text(self, text, instruction):
        prompt = self.get_prompt(text, instruction)

        chat_completion = await self.client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": "You are an AI assistant specialized in analyzing and extracting information from text based on specific instructions."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            model="llama3-8b-8192",
        )

        return parse_response(chat_completion.choices[0].message.content)

    def get_prompt(self, text, instruction):
        return f"Analyze the following text and {instruction}. Provide your response in a clear, structured format:\n\n{text}"


async def async_groq_parser(data_bits, instruction, progress_callback=None):
    parser = GroqParser()

    async def process_bit(bit, i):
        try:
            result = await parser.analyze_text(bit, instruction)
            if progress_callback:
                progress = int((i / total_bits) * 100)
                progress_callback(progress, f"Analyzing batch {i} of {total_bits}")
            return result
        except Exception as e:
            print(f"Error processing batch {i}: {str(e)}")
            return {"error": f"Error in batch {i}: {str(e)}"}

    total_bits = len(data_bits)
    tasks = [process_bit(bit, i) for i, bit in enumerate(data_bits, start=1)]
    results = await asyncio.gather(*tasks)

    if progress_callback:
        progress_callback(100, "Analysis complete!")

    return results


def format_parsed_result(result, format_type='txt'):
    if isinstance(result, list):
        if format_type == 'json':
            return json.dumps(result, indent=2)
        else:
            return "\n".join(str(item) for item in result)
    elif isinstance(result, dict):
        if format_type == 'json':
            return json.dumps(result, indent=2)
        else:
            return "\n".join(f"{k}: {v}" for k, v in result.items())
    else:
        return str(result)

def get_preview(content, max_lines=5):
    lines = content.split('\n')
    preview = '\n'.join(lines[:max_lines])
    if len(lines) > max_lines:
        preview += '\n...'
    return preview


def groq_parser(data_bits, instruction, progress_callback=None):
    try:
        return asyncio.run(async_groq_parser(data_bits, instruction, progress_callback))
    except Exception as e:
        error_message = f"An error occurred during parsing: {str(e)}"
        print(error_message)
        return [{"error": error_message}]
