from sentence_transformers import SentenceTransformer
import numpy as np
import faiss

model = SentenceTransformer("all-MiniLM-L6-v2")

dimension = 384  # dimension for this model
index = faiss.IndexFlatL2(dimension)


def generate_embedding(text):
    vector = model.encode(text)
    return vector


def add_to_faiss(vector):
    vector = np.array([vector]).astype("float32")
    index.add(vector)


def search_similar(vector, top_k=3):
    vector = np.array([vector]).astype("float32")
    distances, indices = index.search(vector, top_k)
    return distances, indices
