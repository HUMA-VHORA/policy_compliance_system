from google import genai
import os
import json

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))


def generate_audit_questions(text):

    prompt = f"""
You are a compliance auditor.

Generate 3 audit questions for this policy clause.

Return strictly JSON:

{{
 "questions": [
   "question1",
   "question2",
   "question3"
 ]
}}

Clause:
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
            return {"questions": [result]}

    except Exception as e:

        print("Audit question error:", e)

        return {"questions": []}