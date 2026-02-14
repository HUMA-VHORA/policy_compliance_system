import numpy as np
from sklearn.metrics.pairwise import cosine_similarity


def compare_embeddings(bank_embeddings, vendor_embeddings):

    results = []

    for bank_id, bank_vector in bank_embeddings.items():

        similarities = []

        for vendor_id, vendor_vector in vendor_embeddings.items():

            score = cosine_similarity(
                bank_vector.reshape(1, -1),
                vendor_vector.reshape(1, -1)
            )[0][0]

            similarities.append((vendor_id, score))

        # Get highest similarity
        best_match = max(similarities, key=lambda x: x[1])

        results.append({
            "bank_paragraph_id": bank_id,
            "matched_vendor_paragraph_id": best_match[0],
            "similarity_score": float(best_match[1])
        })

    return results
