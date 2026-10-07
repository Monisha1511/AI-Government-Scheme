from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

# Load embedding model
model = SentenceTransformer("all-MiniLM-L6-v2")


def retrieve_relevant_schemes(user_query, schemes, top_k=3):

    scheme_texts = []

    for s in schemes:
        text = f"{s['scheme_name']} {s['benefits']} {s['category']}"
        scheme_texts.append(text)

    # Convert to embeddings
    scheme_embeddings = model.encode(scheme_texts)
    query_embedding = model.encode([user_query])

    # Compute similarity
    scores = cosine_similarity(query_embedding, scheme_embeddings)[0]

    # Get top schemes
    top_indices = scores.argsort()[-top_k:][::-1]

    return [schemes[i] for i in top_indices]