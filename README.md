# ♻️ SecondLife Engine — Give Discarded Things a New Job
Built for the Google AI Builder Cup.

## 🚀 Overview
SecondLife Engine uses multimodal AI to convert waste streams into structured upcycling blueprints. 

## 🛠️ Google Cloud Architecture
- **Gemini (`gemini-2.5-flash`):** Core multimodal engine for vision parsing, bounding-box generation, and multi-agent workflow orchestration.
- **Cloud Run:** Serverless backend hosting for our FastAPI service.
- **Firebase / Firestore:** Persistent storage for inventory metrics and saved creative project proposals.

## 🏁 How to Run Locally
1. Clone the repository and install `uv`.
2. Configure your API key: `$env:GEMINI_API_KEY="your-key"`
3. Run backend: `uv run python backend.py`
4. Run frontend: `uv run streamlit run frontend.py`