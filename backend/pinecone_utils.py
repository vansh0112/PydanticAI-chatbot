# pinecone_utils.py

import os
import uuid
from dotenv import load_dotenv
from pinecone import Pinecone, ServerlessSpec
from langchain_pinecone import PineconeVectorStore
from langchain.embeddings import HuggingFaceEmbeddings

load_dotenv()

PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_ENVIRONMENT = os.getenv("PINECONE_ENVIRONMENT", "us-east-1")
PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME", "langchain-docs")

# Use HuggingFace for high-quality open-source embeddings
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
    pc = Pinecone(api_key=PINECONE_API_KEY)
    index = pc.Index(PINECONE_INDEX_NAME)

    print(f"[Embedding] Creating embeddings and uploading in batches of {batch_size}...")

    for i in range(0, len(documents), batch_size):
        batch_docs = documents[i:i + batch_size]
        batch_texts = [doc.page_content for doc in batch_docs]

        # Embed texts
        vectors = embeddings.embed_documents(batch_texts)

        # Add page_content directly into metadata
        pinecone_vectors = []
        for j, (vector, doc) in enumerate(zip(vectors, batch_docs)):
            vector_id = f"doc-{i + j}"
            metadata = {
                **doc.metadata,
                "page_content": doc.page_content.strip()
            }
            pinecone_vectors.append((vector_id, vector, metadata))

        # Upsert to Pinecone
        index.upsert(vectors=pinecone_vectors)
        print(f"[✅] Upserted batch {i // batch_size + 1} with {len(pinecone_vectors)} vectors")

    print(f"[🎉 DONE] Uploaded total {len(documents)} chunks to Pinecone (with full page_content)")
