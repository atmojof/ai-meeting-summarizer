import os
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any, List

# Import engines
from utils.summarizer_engine import TranscriptParser, MetricsEngine, SummaryCompiler

app = FastAPI(
    title="AI Meeting Summarizer API",
    description="Backend services for parsing transcripts and summarizing minutes",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class SummarizeRequest(BaseModel):
    transcript_text: str

PRESET_TRANSCRIPTS = {
    "retro": (
        "Sarah: Welcome team, let's review the sprint retro.\n"
        "John: I will deploy the hotfix for the database API this afternoon. It was causing high CPU overhead.\n"
        "Emma: Great. I have finished coding the frontend user login component. Sarah, can you review the repository code?\n"
        "Sarah: Yes, I will check the git code logs today.\n"
        "Emma: Thanks. We decided to delay the beta release until next Tuesday to ensure thorough testing.\n"
        "John: Agreed. That gives us more time to clean up backend endpoints."
    ),
    "marketing": (
        "David: Let's discuss our growth acquisition budget for the summer campaign.\n"
        "Lisa: We decided to allocate 5000 dollars to social media ads. Our SEO clicks are converting nicely.\n"
        "Tom: I will prepare the marketing newsletter copy by tomorrow. We need to reach our newsletter list.\n"
        "David: Lisa, will you check the conversion target metrics?\n"
        "Lisa: Yes, I will verify the billing invoice targets and target ads spend today."
    ),
    "board": (
        "Alice: Let's start with our quarterly hiring status.\n"
        "Bob: We decided to hire two additional backend engineers to speed up deployment.\n"
        "Charlie: I will coordinate the developer interviews onboarding schedule.\n"
        "Alice: Excellent. Charlie, will you also write the job descriptions document update?\n"
        "Charlie: Yes, I will update the HR recruiting workflow by this Friday."
    )
}

@app.get("/api/presets")
def get_presets():
    """Returns the preseeded meeting transcripts for testing."""
    return PRESET_TRANSCRIPTS

@app.post("/api/summarize-transcript")
def summarize_transcript(request: SummarizeRequest):
    """Parses transcript text, computes speaker and topic metrics, and generates minutes recap."""
    text = request.transcript_text.strip()
    if not text:
        raise HTTPException(status_code=400, detail="Transcript text cannot be empty.")
        
    try:
        # 1. Parse speakers and word ratios
        parsed = TranscriptParser.parse(text)
        dialogues = parsed["dialogues"]
        speaker_shares = parsed["speaker_shares"]
        speaker_names = list(speaker_shares.keys())
        
        # 2. Compute timeline and topic weights
        timeline = MetricsEngine.analyze_sentiment_timeline(dialogues)
        topics = MetricsEngine.analyze_topic_weights(dialogues)
        
        # 3. Compile executive summaries & action items
        summary = SummaryCompiler.generate_summary(dialogues, speaker_names)
        
        return {
            "total_words": parsed["total_words"],
            "speaker_shares": speaker_shares,
            "timeline": timeline,
            "topics": topics,
            "summary": summary
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Mount static folder
static_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")
os.makedirs(static_path, exist_ok=True)
app.mount("/", StaticFiles(directory=static_path, html=True), name="static")
