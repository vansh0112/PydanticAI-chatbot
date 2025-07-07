# pinecone_utils.py

import os
from dotenv import load_dotenv
from pinecone import Pinecone, ServerlessSpec
from langchain_pinecone import PineconeVectorStore
from langchain_openai import OpenAIEmbeddings

load_dotenv()

PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_ENVIRONMENT = os.getenv("PINECONE_ENVIRONMENT", "us-east-1")
PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME", "langchain-docs")

from langchain.embeddings import HuggingFaceEmbeddings

embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-mpnet-base-v2"
)

def init_pinecone_and_index():
    pc = Pinecone(api_key=PINECONE_API_KEY)
    existing = pc.list_indexes().names()
    if PINECONE_INDEX_NAME not in existing:
        pc.create_index(
            name=PINECONE_INDEX_NAME,
            dimension=768,
            metric="cosine",
            spec=ServerlessSpec(cloud="aws", region=PINECONE_ENVIRONMENT),
        )
        print(f"[Pinecone] Created index {PINECONE_INDEX_NAME}")
    else:
        print(f"[Pinecone] Using existing index {PINECONE_INDEX_NAME}")


def store_documents_in_pinecone(documents, batch_size=32):
    from pinecone import Pinecone
    import uuid

    pc = Pinecone(api_key=PINECONE_API_KEY)
    index = pc.Index(PINECONE_INDEX_NAME)

    texts = [doc.page_content for doc in documents]

    print(f"[Embedding] Creating embeddings in batches of {batch_size}...")

    # Batch the texts and embeddings
    for i in range(0, len(texts), batch_size):
        batch_texts = texts[i:i + batch_size]
        
        # Inject page_content into metadata
        batch_metadatas = [
            {**documents[i + j].metadata, "page_content": batch_texts[j]}
            for j in range(len(batch_texts))
        ]

        # Get embeddings using HuggingFace (already defined above)
        vectors = embeddings.embed_documents(batch_texts)

        # Prepare items to upsert
        pinecone_vectors = []
        for j, (vector, metadata) in enumerate(zip(vectors, batch_metadatas)):
            vector_id = f"doc-{i + j}"
            pinecone_vectors.append((vector_id, vector, metadata))

        index.upsert(vectors=pinecone_vectors)
        print(f"[✅] Upserted batch {i // batch_size + 1} with {len(pinecone_vectors)} vectors")

    print(f"[✅] Uploaded total {len(documents)} chunks to Pinecone")

