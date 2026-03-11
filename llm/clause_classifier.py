# llm/clause_classifier.py

from llm.gemini_client import generate_content


def classify_clause(clause_text: str) -> str:
    """
    Classifies a policy clause into a category.
    """

    prompt = f"""
You are a compliance policy expert.

TASK:
Classify the following policy clause into ONE category.

Allowed Categories:
- Data Privacy
- Security
- Compliance
- Financial
- Legal
- Operational
- HR
- Other

INSTRUCTIONS:
- Return only the category name.
- Do not explain.
- Do not add extra text.

CLAUSE:
\"\"\"{clause_text}\"\"\"

CATEGORY:
"""

    return generate_content(prompt)