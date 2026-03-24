from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
import openai
import os

app = FastAPI()

class ContextRequest(BaseModel):
    context: str

class NewsResponse(BaseModel):
    id: int
    title: str
    content: str
    url: str
    source: str
    trust_rating: float
    reasoning: str
    sources: List[str]

@app.post("/process", response_model=NewsResponse)
async def process_context(request: ContextRequest):
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return NewsResponse(
            id=123,
            title="Breaking: Scientists Discover New Planet",
            content="Researchers have found evidence of a new exoplanet...",
            url="https://news.example.com/planet-discovery",
            source="Science News",
            trust_rating=0.85,
            reasoning="High credibility based on scientific sources",
            sources=["https://source1.com", "https://source2.com"]
        )

    openai.api_key = api_key

    # Промпт для ИИ модели
    prompt = f"""
Based on the following page context, generate a JSON object with the following fields:
- id: an integer (use 123 as example)
- title: a string
- content: a string summary
- url: a string (extract or infer from context)
- source: a string
- trust_rating: a float between 0 and 1
- reasoning: a string explaining the trust rating
- sources: a list of strings (URLs)

Context: {request.context}

Return only the JSON object, no additional text.
"""

    try:
        client = openai.OpenAI(api_key=api_key)
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=500
        )
        result_text = response.choices[0].message.content.strip()
        import json
        result = json.loads(result_text)
        return NewsResponse(**result)
    except Exception as e:
        return NewsResponse(
            id=123,
            title="Error processing context",
            content=str(e),
            url="",
            source="",
            trust_rating=0.0,
            reasoning="Error occurred",
            sources=[]
        )
