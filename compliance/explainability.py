# compliance/explainability.py

import numpy as np

def explain_gap(bank_text: str, vendor_text: str, similarity_score: float) -> str:
    """
    Generate an explanation for partial compliance or gap between bank and vendor paragraphs.

    Args:
        bank_text (str): Paragraph from the bank policy
        vendor_text (str): Paragraph from the vendor policy
        similarity_score (float): Cosine similarity score between embeddings

    Returns:
        str: Explanation text
    """

    # If similarity is very low, it's a clear gap
    if similarity_score < 0.4:
        explanation = (
            "Major gap detected: Vendor paragraph does not match bank requirements. "
            "Significant differences exist in terms of compliance expectations."
        )
    # Partial similarity
    elif similarity_score < 0.85:
        explanation = (
            "Partial compliance: Vendor paragraph covers some aspects of the bank requirement "
            "but misses or differs on certain points. "
            f"Similarity score: {similarity_score:.2f}."
        )
    else:
        # Should not normally reach here (fully compliant handled elsewhere)
        explanation = "Vendor paragraph is mostly compliant."

    # Optionally, highlight differences (simple token-based)
    bank_tokens = set(bank_text.lower().split())
    vendor_tokens = set(vendor_text.lower().split())

    missing_tokens = bank_tokens - vendor_tokens

    if missing_tokens:
        missing_summary = ', '.join(list(missing_tokens)[:10])  # show up to 10 words
        explanation += f" Key missing/altered terms: {missing_summary}."

    return explanation