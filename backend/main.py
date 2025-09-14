# backend/main.py
import os
import json
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests

load_dotenv()  # loads .env

GEMINI_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_KEY:
    raise RuntimeError("Set GEMINI_API_KEY in backend/.env")

app = FastAPI(title="SimpleBooks MVP")

# Allow requests from the local frontend (adjust if different port)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5500", "http://127.0.0.1:5500"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class SimplifyRequest(BaseModel):
    text: str

# Corrected URL for a stable model version
GENAI_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"

@app.post("/simplify")
async def simplify(req: SimplifyRequest):
    prompt = f"Simplify the following text to very simple English, suitable for a beginner (CEFR A1-A2 level). Keep the original meaning perfectly intact and also dont shorten the paragraph length maintain the context.\n\nOriginal Text:\n{req.text}\n\nSimplified Text:"

    # The payload structure for the Gemini API
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "temperature": 0.2,
            "maxOutputTokens": 800
        }
    }

    headers = {
        "Content-Type": "application/json",
        "x-goog-api-key": GEMINI_KEY
    }

    try:
        resp = requests.post(GENAI_URL, headers=headers, json=payload, timeout=30)
        resp.raise_for_status()  # This will raise an exception for 4xx/5xx responses
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=502, detail=f"GenAI request error: {e}")

    data = resp.json()

    # Correct and safer way to extract the simplified text from the response
    try:
        simplified = data['candidates'][0]['content']['parts'][0]['text']
    except (KeyError, IndexError, TypeError):
        # Fallback if the response structure is unexpected
        error_detail = f"Could not parse GenAI response. Full response: {json.dumps(data)[:1000]}"
        raise HTTPException(status_code=500, detail=error_detail)

    return {"simplified": simplified.strip()}