from dotenv import load_dotenv
load_dotenv()
import json
import os
import pandas as pd
from typing import Dict, Any

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from google import genai
from google.genai import types

app = FastAPI(title="Don't Collapse API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class AnalyzeRequest(BaseModel):
    scenario: str

DATA_PATH = os.path.join(os.path.dirname(__file__), "tampa-resilience", "output", "master_fragility_with_explanations.csv")

def get_base_data() -> str:
    try:
        df = pd.read_csv(DATA_PATH)
        return df.to_csv(index=False)
    except Exception as e:
        return f"Error loading data: {e}"

@app.post("/analyze")
async def analyze(request: AnalyzeRequest):
    try:
        scenario = request.scenario
        csv_data = get_base_data()
        
        system_instruction = """
        You are an expert infrastructure resilience analyst.
        You are given a base dataset (CSV) of localized fragility scores for zones in Tampa Bay.
        Based on the User's provided disaster scenario, calculate a comprehensive impact assessment for the frontend dashboard.
        
        The frontend dashboard requires a STRICT JSON output matching this schema exactly:
        {
          "summary": "2-3 sentences explaining the overarching threat and why certain areas are at risk.",
          "score": 0-100 (Overall system baseline score, lower means more secure, higher means critical danger),
          "affected": "Text describing the primary region or system affected",
          "actions": [
            { "id": "uuid", "title": "short title", "detail": "explanation", "urgency": "critical"|"warning"|"stable" }
          ],
          "logs": [ "short log string 1", "short log string 2" ],
          "rankedAreas": [
            { "name": "Zone Name", "score": 0-100, "reason": "short explanation" }
          ],
          "infrastructureScores": [
            { "id": "roads", "label": "Major Arteries", "score": 0-100 },
            { "id": "intersections", "label": "Key Intersections", "score": 0-100 },
            { "id": "drainage", "label": "Drainage Systems", "score": 0-100 },
            { "id": "power", "label": "Power Grid", "score": 0-100 },
            { "id": "access-routes", "label": "Shelter Access", "score": 0-100 }
          ],
          "actionPayload": {
            "action": "Some visual action text",
            "coordinates": []
          }
        }
        
        Generate the json using information from the CSV. Ensure exactly 3 items in `actions` and 5 items in `rankedAreas`. Add a small variance to the CSV scores dynamically based on the specific flavor or intensity of the provided scenario text.
        IMPORTANT: Return RAW JSON only, without any markdown formatting wrappers (no ```json).
        """
        
        prompt = f"Scenario: {scenario}\n\nBase Fragility Data:\n{csv_data}"

        client = genai.Client()
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=system_instruction,
                temperature=0.7,
                response_mime_type="application/json",
            ),
        )
        
        res_text = response.text.strip()
        if res_text.startswith("```json"):
            res_text = res_text[7:]
        if res_text.endswith("```"):
            res_text = res_text[:-3]
            
        data = json.loads(res_text)
        return data

    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
def health():
    return {"status": "ok"}
