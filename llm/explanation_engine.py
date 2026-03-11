from google import genai
import os

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))


def explain_gap(bank_text, vendor_text, similarity_score):

    prompt = f"""
You are a compliance analyst.

BANK REQUIREMENT:
{bank_text}

VENDOR CLAUSE:
{vendor_text}

Similarity Score: {round(similarity_score*100,2)}%

Explain the compliance gap in 2 sentences.
"""

    try:

        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt
        )

        return response.text.strip()

    except Exception as e:

        print("Explanation error:", e)

        return "AI explanation unavailable."