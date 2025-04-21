from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sklearn.feature_extraction.text import TfidfVectorizer
from pydantic import BaseModel
import numpy as np
from slowapi import Limiter
from slowapi.util import get_remote_address
import nltk
from nltk.tokenize import sent_tokenize
import requests
import re

app = FastAPI()

# Configure static files and templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="ui")

# API Rate Limiting (prevent abuse)
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

# Store user-provided context
documents = []

# Mistral AI Configuration
MISTRAL_API_KEY = "your_mistral_api_key"  # Replace with actual API key
MISTRAL_API_URL = "https://api.mistral.ai/v1/chat/completions"
MAX_TOKENS = 32768  # Model limit

@app.get("/", response_class=HTMLResponse)
async def serve_frontend(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# Submitting Context
class ContextInput(BaseModel):
    context: str

@app.post("/submit-context")
async def submit_context(context_input: ContextInput):
    global documents
    documents = [context_input.context]
    return {"status": "Context updated successfully"}

# Asking a question
class QuestionRequest(BaseModel):
    question: str
    context: str = None  # Optional

@app.post("/ask")
async def ask_question(request: QuestionRequest):
    question = request.question
    context = request.context or ""  # Default empty context

    ai_response = send_to_mistral(question, context)
    return {"answer": ai_response}

def send_to_mistral(question, context):
    payload = {
        "model": "mistral-tiny",  # Free-tier model (try "mistral-7b" if available)
        "messages": [
            {"role": "system", "content": "Use the provided context to answer the user's question."},
            {"role": "user", "content": f"Context: {context}\nQuestion: {question}"}
        ],
        "temperature": 0.7
    }

    headers = {
        "Authorization": f"Bearer {MISTRAL_API_KEY}",
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(MISTRAL_API_URL, json=payload, headers=headers)
        response_data = response.json()

        if "choices" in response_data:
            return response_data["choices"][0]["message"]["content"]
        else:
            return f"Error: {response_data.get('error', 'Unknown error')}"
    
    except Exception as e:
        return f"API Connection Error: {str(e)}"

# Document retrieval
nltk.download("punkt")

def get_relevant_passages(query, top_n=3, window_size=3):
    if not documents or not documents[0]:
        return ["No relevant passages found. Please provide context first."]

    doc_text = documents[0]  # Single user-provided document
    sentences = sent_tokenize(doc_text)

    # Remove irrelevant sections
    irrelevant_pattern = re.compile(r"(table of contents|introduction|preface|foreword|chapter \d+|section \d+)", re.IGNORECASE)
    sentences = [s for s in sentences if not irrelevant_pattern.search(s)]

    if not sentences:
        return ["No relevant passages found. Please submit valid content."]

    # Use TF-IDF to rank relevance
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(sentences + [query])

    # Compute cosine similarity between query and sentences
    query_vector = tfidf_matrix[-1]
    sentence_vectors = tfidf_matrix[:-1]
    scores = np.dot(sentence_vectors, query_vector.T).toarray().flatten()

    # Rank sentences based on similarity scores
    sorted_indices = scores.argsort()[::-1]  # Highest to lowest
    best_snippets = []

    for i in sorted_indices[:top_n]:
        if scores[i] > 0:
            start_idx = max(0, i - window_size)
            end_idx = min(len(sentences), i + window_size)
            snippet = " ".join(sentences[start_idx:end_idx])
            best_snippets.append(snippet)

    if not best_snippets:
        return sentences[:3]  # Return first 3 meaningful sentences

    return best_snippets
