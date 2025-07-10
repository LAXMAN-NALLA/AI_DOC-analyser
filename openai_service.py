
# openai_service.py
import os
import json
import re
import asyncio
import logging
from typing import Any, Dict
from dotenv import load_dotenv
import openai

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4")
client = openai.AsyncOpenAI(api_key=OPENAI_API_KEY)

MAX_RETRIES = 3

async def analyze_document(text: str) -> Dict[str, Any]:
    prompt = (
        "Analyze this document and extract:\n"
        "- Document type\n"
        "- Summary (2-3 lines)\n"
        "- Reference number\n"
        "- Total due\n"
        "- Filing status\n"
        "- Deadlines (type and date)\n"
        "- Recommendations\n\n"
        "Respond ONLY with a valid JSON object. No explanation, no extra text.\n\n"
        f"Document:\n{text}"
    )

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            logging.info(f"Attempt {attempt}: Sending to OpenAI...")
            response = await client.chat.completions.create(
                model=OPENAI_MODEL,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.2
            )
            content = response.choices[0].message.content.strip()
            logging.info(f"OpenAI response: {content}")

            try:
                return json.loads(content)
            except json.JSONDecodeError:
                logging.warning("Initial JSON parsing failed. Trying regex recovery...")
                match = re.search(r"\{[\s\S]*\}", content)
                if match:
                    try:
                        return json.loads(match.group())
                    except json.JSONDecodeError:
                        logging.error("Even recovered JSON is invalid.")
                else:
                    logging.error("No JSON structure found in response.")

        except Exception as e:
            logging.error(f"OpenAI API error: {e}")

        await asyncio.sleep(1)

    return {"error": "Failed to get valid JSON after 3 attempts"}