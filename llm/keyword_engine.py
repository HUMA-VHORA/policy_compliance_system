from google import genai
import os
import json

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))


def extract_keywords(text):

    prompt = f"""
Extract important compliance keywords from the text.

Return strictly JSON format:

{{
 "keywords": ["keyword1","keyword2","keyword3"]
}}

TEXT:
{text}
"""

    try:

        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt
        )

        result = response.text.strip()

        try:
            return json.loads(result)

        except:
            return {"keywords": [result]}

    except Exception as e:

        print("Keyword error:", e)

        return {"keywords": []}