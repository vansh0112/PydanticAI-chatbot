# processing_utils.py
import os
import json
from typing import List, Dict, Any
from dataclasses import dataclass
from datetime import datetime, timezone

from langchain.schema import Document
from dotenv import load_dotenv

from sentence_transformers import SentenceTransformer
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline

load_dotenv()

# Hugging Face models
EMBEDDING_MODEL = SentenceTransformer("sentence-transformers/all-mpnet-base-v2", use_auth_token=os.getenv("HF_TOKEN"))
HF_TOKEN = os.getenv("HF_TOKEN")
tokenizer = AutoTokenizer.from_pretrained("google/flan-t5-base")
TITLE_GEN_PIPE = pipeline(
    "text2text-generation",
    model="google/flan-t5-base",
    tokenizer=tokenizer,
)

@dataclass
class ProcessedChunk:
    chunk_number: int
    title: str
    content: str
    metadata: Dict[str, Any]
    embedding: List[float]


def smart_chunk_text(text: str, chunk_size: int = 5000) -> List[str]:
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        if end >= len(text):
            chunks.append(text[start:].strip())
            break

        chunk = text[start:end]
        code_block = chunk.rfind("```")
        if code_block != -1 and code_block > chunk_size * 0.3:
            end = start + code_block
        elif "\n\n" in chunk:
            last_break = chunk.rfind("\n\n")
            if last_break > chunk_size * 0.3:
                end = start + last_break
        elif ". " in chunk:
            last_period = chunk.rfind(". ")
            if last_period > chunk_size * 0.3:
                end = start + last_period + 1

        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)

        start = max(start + 1, end)

    return chunks



def truncate_to_fit(text: str, max_total_tokens: int = 512, reserved_prompt_tokens: int = 30) -> str:
    max_chunk_tokens = max_total_tokens - reserved_prompt_tokens
    input_ids = tokenizer.encode(text, truncation=True, max_length=max_chunk_tokens)
    return tokenizer.decode(input_ids, skip_special_tokens=True)

def get_titles_batched(chunks: List[str], batch_size: int = 8) -> List[str]:
    prompts = [
        f"Generate a short, meaningful title for the following documentation text:\n\n{truncate_to_fit(c)}\nTitle:"
        for c in chunks
    ]
    responses = []
    for i in range(0, len(prompts), batch_size):
        batch = prompts[i:i + batch_size]
        outputs = TITLE_GEN_PIPE(batch, max_new_tokens=20)
        responses.extend([r["generated_text"].strip() for r in outputs])
    return responses



def get_embeddings_batched(chunks: List[str], batch_size: int = 16) -> List[List[float]]:
    try:
        return EMBEDDING_MODEL.encode(chunks, batch_size=batch_size, show_progress_bar=True).tolist()
    except Exception as e:
        print(f"[Embedding Error] {e}")
        return [[0.0] * 768 for _ in chunks]



async def process_chunks_batched(chunks: List[str]) -> List[Document]:
    titles = get_titles_batched(chunks)
    embeddings = get_embeddings_batched(chunks)

    documents = []
    for i, (chunk, title, embedding) in enumerate(zip(chunks, titles, embeddings)):
        metadata = {
            "title": title,
            "chunk_number": i,
            "source": "pydantic.ai",
            "chunk_size": len(chunk),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        documents.append(Document(page_content=chunk, metadata=metadata))
    return documents