# compliance/comparison_engine.py

import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from compliance.explainability import explain_gap


# =====================================
# Convert NumPy Types to JSON Safe
# =====================================
def convert_to_serializable(obj):
    """
    Recursively convert NumPy types to Python native types for JSON serialization.
    """
    if isinstance(obj, (np.float32, np.float64)):
        return float(obj)
    elif isinstance(obj, (np.int32, np.int64)):
        return int(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, dict):
        return {k: convert_to_serializable(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_to_serializable(i) for i in obj]
    else:
        return obj


# =====================================
# Main Comparison Function
# =====================================
def compare_embeddings(
    bank_embeddings: dict,
    vendor_embeddings: dict,
    bank_paragraphs: dict,
    vendor_paragraphs: dict
):
    """
    Compare bank and vendor embeddings using cosine similarity.

    Returns:
        list: JSON-safe comparison results
    """

    results = []

    for bank_id, bank_vector in bank_embeddings.items():

        similarities = []

        for vendor_id, vendor_vector in vendor_embeddings.items():

            # Compute cosine similarity
            score = cosine_similarity(
                bank_vector.reshape(1, -1),
                vendor_vector.reshape(1, -1)
            )[0][0]

            similarities.append((vendor_id, score))

        # Get best matching vendor paragraph
        best_match = max(similarities, key=lambda x: x[1])
        matched_vendor_id = best_match[0]
        similarity_score = float(best_match[1])  # Convert to Python float

        # ==============================
        # Compliance Decision Logic
        # ==============================
        if similarity_score >= 0.85:
            compliance_status = "Fully Compliant"
            explanation = "Vendor fully satisfies the bank requirement."

        else:
            if similarity_score >= 0.6:
                compliance_status = "Partially Compliant"
            else:
                compliance_status = "Gap"

            # Call explainability module
            explanation = explain_gap(
                bank_paragraphs[bank_id],
                vendor_paragraphs[matched_vendor_id],
                similarity_score
            )

        # ==============================
        # Store Result
        # ==============================
        results.append({
            "bank_paragraph_id": bank_id,
            "matched_vendor_paragraph_id": matched_vendor_id,
            "similarity_score": similarity_score,
            "compliance_status": compliance_status,
            "explanation": explanation
        })

    # Final JSON-safe conversion
    return convert_to_serializable(results)