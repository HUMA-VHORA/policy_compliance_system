# llm/gemini_client.py

from google import genai
import os

API_KEY = os.getenv("GEMINI_API_KEY")

client = genai.Client(api_key=API_KEY)


def generate_content(prompt: str) -> str:
    """
    Sends prompt to Gemini and returns response text.
    """
    try:
        response = client.models.generate_content(
            model="gemini-1.5-flash",
            contents=prompt
        )

        if response and response.text:
            return response.text.strip()

        return "No response generated."

    except Exception as e:
        print("Gemini API error:", e)
        return "LLM service unavailable."