# RAG-Based AI Assistant (Mistral-7B)

## Overview
A minimalist Retrieval-Augmented Generation (RAG) system using FastAPI, Mistral-7B API, and TF-IDF for context retrieval.
Upload text, retrieve relevant passages, and ask AI questions with Mistral-powered responses!

## Features
- FastAPI Backend – Lightweight API
- Mistral-7B API Integration – Uses Mistral-Tiny (can be configured)
- TF-IDF Context Retrieval – Extracts relevant snippets before AI processing
- Live Token Counter – Displays tokens used vs. 32,768 max in real time (token limit for the Mistral model)
- Minimalist UI – Clean and responsive frontend with a simple interface
- Rate Limiting – Prevents API abuse with SlowAPI
- No Authentication Required

## Installation
1. Clone this repository.
2. Create a virtual environment and activate it.
3. Install dependencies in requirements.txt:
    pip install -r requirements.txt
4. Running the App
    uvicorn app.main:app --host 0.0.0.0 --port 8000

## Technologies Used
FastAPI – Lightweight Python API
Mistral API – AI model
TF-IDF (Scikit-Learn) – Retrieves relevant text
Jinja2 & JavaScript – Frontend for UI
SlowAPI – Rate limiting (prevents spam)
HTML, CSS
