import os
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Dict, Any
from google import genai
from google.genai import types
from PIL import Image
import io

app = FastAPI(title="SecondLife Engine API", version="1.0")

# Initialize Gemini Client (picks up GEMINI_API_KEY from environment variables)
# Set your key via: export GEMINI_API_KEY="your-key"
client = genai.Client()

class AnalysisResponse(BaseModel):
    detected_materials: List[Dict[str, Any]]
    valuation_summary: Dict[str, Any]
    creative_proposals: List[Dict[str, Any]]

@app.post("/analyze", response_model=AnalysisResponse)
async def analyze_waste_image(file: UploadFile = File(...)):
    try:
        image_bytes = await file.read()
        image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        width, height = image.size

        # Multi-Agent Workflow orchestrated through specialized prompt contexts
        prompt = """
        You are the SecondLife Engine Multi-Agent AI Core. Analyze this image of discarded items and perform three consecutive agent tasks:
        
        1. [Agent 1: Vision & Bounding Box Detector] Identify distinct usable material components. Provide a detailed list, count/quantity, and bounding box coordinates [ymin, xmin, ymax, xmax] scaled strictly from 0 to 1000.
        2. [Agent 2: Safety & Valuation Auditor] Estimate the economic market value / replacement savings (in USD equivalent) for each identified material item, and list safety precautions.
        3. [Agent 3: Creative Upcycling Architect] Propose 3 high-impact, creative artistic or functional reuse plans utilizing these exact materials, complete with a Bill of Materials and step-by-step assembly guides.

        Return your output strictly as valid JSON matching this schema:
        {
          "detected_materials": [
            {
              "item_name": "string",
              "category": "string",
              "quantity": 0,
              "estimated_value_usd": 0.0,
              "safety_notes": "string",
              "box_2d": [ymin, xmin, ymax, xmax]
            }
          ],
          "valuation_summary": {
            "total_estimated_value_usd": 0.0,
            "estimated_waste_diverted_kg": 0.0
          },
          "creative_proposals": [
            {
              "project_name": "string",
              "artistic_theme": "string",
              "bill_of_materials": ["string"],
              "step_by_step_plan": ["string"]
            }
          ]
        }
        """

        # Call Gemini 2.5 Flash / Flash-Lite with structured JSON output configuration
        response = client.models.generate_content(
            model='gemini-3.8-flash',
            contents=[image, prompt],
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                temperature=0.2
            ),
        )

        import json
        result_data = json.loads(response.text)
        
        # Post-Processing: Crop the boxed sub-images locally for UI inspection
        processed_materials = []
        for mat in result_data.get("detected_materials", []):
            box = mat.get("box_2d", [0, 0, 1000, 1000])
            ymin, xmin, ymax, xmax = box
            
            # Convert normalized 0-1000 coordinates to absolute pixel values
            abs_ymin = int((ymin / 1000.0) * height)
            abs_xmin = int((xmin / 1000.0) * width)
            abs_ymax = int((ymax / 1000.0) * height)
            abs_xmax = int((xmax / 1000.0) * width)
            
            # Ensure boundaries are valid
            abs_ymin = max(0, min(abs_ymin, height))
            abs_xmin = max(0, min(abs_xmin, width))
            abs_ymax = max(abs_ymin + 5, min(abs_ymax, height))
            abs_xmax = max(abs_xmin + 5, min(abs_xmax, width))

            # Crop sub-image
            cropped_img = image.crop((abs_xmin, abs_ymin, abs_xmax, abs_ymax))
            buffered = io.BytesIO()
            cropped_img.save(buffered, format="JPEG")
            import base64
            img_str = base64.b64encode(buffered.getvalue()).decode()
            mat["cropped_image_base64"] = img_str
            processed_materials.append(mat)

        result_data["detected_materials"] = processed_materials
        return JSONResponse(content=result_data)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)