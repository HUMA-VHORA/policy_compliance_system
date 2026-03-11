# compliance/embedding_engine.py

from sentence_transformers import SentenceTransformer
import numpy as np
import faiss

# ==============================
# Load Sentence Transformer Model
# ==============================
model = SentenceTransformer("all-MiniLM-L6-v2")

# Embedding dimension for all-MiniLM-L6-v2
DIMENSION = 384

# ==============================
# Create FAISS Index
# ==============================
index = faiss.IndexFlatL2(DIMENSION)


# ==============================
# Generate Embedding
# ==============================
def generate_embedding(text: str) -> np.ndarray:
    """
    Generate embedding vector for a given text.
    """
    vector = model.encode(text)
    return vector.astype("float32")


# ==============================
# Generate Multiple Embeddings
# ==============================
def generate_embeddings(text_dict: dict) -> dict:
    """
    Generate embeddings for multiple paragraphs.

    Args:
        text_dict (dict): {paragraph_id: paragraph_text}

    Returns:
        dict: {paragraph_id: embedding_vector}
    """
    embeddings = {}

    for pid, text in text_dict.items():
        vector = generate_embedding(text)
        embeddings[pid] = vector

    return embeddings


# ==============================
# FAISS Operations
# ==============================
def add_to_faiss(vector: np.ndarray) -> None:
    """
    Add single vector to FAISS index.
    """
    vector = np.array([vector], dtype="float32")
    index.add(vector)


def add_multiple_to_faiss(vectors: list) -> None:
    """
    Add multiple vectors to FAISS index.
    """
    vectors = np.array(vectors).astype("float32")
    index.add(vectors)


def search_similar(vector: np.ndarray, top_k: int = 3):
    """
    Search top_k similar vectors in FAISS index.
    """
    vector = np.array([vector], dtype="float32")
    distances, indices = index.search(vector, top_k)
    return distances, indices


def reset_index():
    """
    Clear FAISS index.
    """
    global index
    index = faiss.IndexFlatL2(DIMENSION)