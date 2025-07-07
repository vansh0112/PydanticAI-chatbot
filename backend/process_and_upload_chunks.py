# process_and_upload_chunks.py

import json
import asyncio
from langchain.schema import Document
from processing_utils import process_chunks_batched
from pinecone_utils import init_pinecone_and_index, store_documents_in_pinecone

CHUNKS_PATH = "chunks.json"

async def load_and_process_chunks():
    with open(CHUNKS_PATH, "r", encoding="utf-8") as f:
        chunks = json.load(f)

    print(f"[Load] Loaded {len(chunks)} chunks")

    docs = await process_chunks_batched(chunks)

    print(f"[Process] Processed {len(docs)} chunks")

    store_documents_in_pinecone(docs)


async def main():
    init_pinecone_and_index()
    await load_and_process_chunks()


if __name__ == "__main__":
    asyncio.run(main())
