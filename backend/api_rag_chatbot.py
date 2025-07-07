import os
import requests
from typing import List
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from fastapi.security import OAuth2AuthorizationCodeBearer
from starlette.middleware.sessions import SessionMiddleware
from pydantic import BaseModel
from sentence_transformers import SentenceTransformer
from pinecone import Pinecone
from authlib.integrations.starlette_client import OAuth

# Load environment
load_dotenv()
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME")
MODEL = "mistralai/mistral-7b-instruct:free"
EMBEDDING_MODEL_NAME = "sentence-transformers/all-mpnet-base-v2"

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
SECRET_KEY = os.getenv("SECRET_KEY", "supersecret")

# === FastAPI app ===
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(SessionMiddleware, secret_key=SECRET_KEY)

# === OAuth Setup ===
oauth = OAuth()
oauth.register(
    name='google',
    client_id=GOOGLE_CLIENT_ID,
    client_secret=GOOGLE_CLIENT_SECRET,
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={'scope': 'openid email profile'}
)

# === Vector setup ===
embedding_model = SentenceTransformer(EMBEDDING_MODEL_NAME)
pc = Pinecone(api_key=PINECONE_API_KEY)
index = pc.Index(PINECONE_INDEX_NAME)

# === Request model ===
class QueryRequest(BaseModel):
    question: str

# === Embedding and Retrieval ===
def get_query_embedding(query: str) -> List[float]:
    return embedding_model.encode([query])[0].tolist()

def retrieve_top_chunks(query_embedding: List[float], top_k: int = 3) -> List[dict]:
    results = index.query(vector=query_embedding, top_k=top_k, include_metadata=True)
    return results.get("matches", [])

def build_context_from_matches(matches: List[dict]) -> str:
    context_sections = []
    for i, match in enumerate(matches):
        metadata = match.get("metadata", {})
        title = metadata.get("title", f"Chunk {i+1}")
        content = metadata.get("page_content", "[No content]")
        score = match.get("score", 0.0)

        context_sections.append(
            f"📌 Title: {title}\n💡 Score: {score:.4f}\n🧾 Content:\n{content}"
        )
    return "\n\n".join(context_sections)

def build_prompt(context: str, question: str) -> str:
    return f"""
You are a highly accurate technical assistant specialized in answering questions about **Pydantic AI**, based solely on the provided documentation context.

🔒 Strict Rules:
- Use ONLY the documentation context below — do NOT use external knowledge or guess.
- If the answer is not found in the context, respond with: "❓ The answer is not available in the provided documentation."
- Be detailed and exhaustive in your answer. Do not merge unrelated information from multiple chunks unless necessary.

📝 Instructions:
- Provide a well-structured, informative, and technically accurate answer.
- Use bullet points, steps, or examples where helpful.
- Format code as **indented blocks**, not using triple backticks.
- Minimize unnecessary line breaks for readability.

📚 Context:
{context}

❓ Question:
{question}

✅ Detailed Answer:
""".strip()

def query_openrouter(prompt: str, question: str) -> str:
    system_message = (
        "You are a helpful AI assistant specialized in answering technical questions about Pydantic AI.\n"
        "Use ONLY the provided documentation context to answer questions.\n"
        "• Do NOT guess or use external knowledge.\n"
        "• If the answer is not present in the context, reply with: '❓ The answer is not available in the provided documentation.'\n"
        "• Respond in a concise and accurate manner. Format code using indentation only — do NOT use triple backticks.\n"
    )

    user_message = f"""📚 Context:\n{prompt}\n\n❓ Question:\n{question}"""
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": system_message},
            {"role": "user", "content": user_message}
        ]
    }

    response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=payload)
    try:
        return response.json()["choices"][0]["message"]["content"].strip()
    except Exception as e:
        print("❌ Error parsing OpenRouter response:", e)
        print("Raw response:", response.text)
        return "[Error generating response]"

# === Routes ===
@app.post("/ask")
def ask_question(request: QueryRequest):
    if not request.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty.")
    
    query_embedding = get_query_embedding(request.question)
    matches = retrieve_top_chunks(query_embedding)

    if not matches:
        raise HTTPException(status_code=404, detail="No relevant chunks found.")
    
    context = build_context_from_matches(matches)
    prompt = build_prompt(context, request.question)
    answer = query_openrouter(prompt, request.question)

    return {
        "question": request.question,
        "context_chunks": context,
        "answer": answer
    }

# === OAuth Endpoints ===
@app.get("/login")
async def login(request: Request):
    redirect_uri = request.url_for("auth_callback")
    return await oauth.google.authorize_redirect(request, redirect_uri)

@app.get("/auth/callback")
async def auth_callback(request: Request):
    token = await oauth.google.authorize_access_token(request)
    user = await oauth.google.parse_id_token(request, token)
    request.session['user'] = dict(user)
    return RedirectResponse(url="/me")

@app.get("/me")
async def get_user_info(request: Request):
    user = request.session.get("user")
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return user
