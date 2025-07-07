import os
import json
from dotenv import load_dotenv
from pinecone import Pinecone

load_dotenv()

PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME", "langchain-docs")
CHUNKS_PATH = "chunks.json"

pc = Pinecone(api_key=PINECONE_API_KEY)
index = pc.Index(PINECONE_INDEX_NAME)

with open(CHUNKS_PATH, "r", encoding="utf-8") as f:
    chunks = json.load(f)

batch_size = 32
print("[🛠️] Safely updating 'page_content' into existing Pinecone metadata...")

for i in range(0, len(chunks), batch_size):
    ids = [f"doc-{i + j}" for j in range(min(batch_size, len(chunks) - i))]
    existing = index.fetch(ids=ids).vectors

    for j, vector_id in enumerate(ids):
        if vector_id not in existing:
            continue  # Skip missing (but we just verified none are missing)

        metadata = existing[vector_id].metadata or {}
        metadata["page_content"] = chunks[i + j].strip()

        index.update(id=vector_id, set_metadata=metadata)

    print(f"[✅] Batch {i // batch_size + 1} updated.")

print(f"[🎉 DONE] All {len(chunks)} entries updated with 'page_content'.")
