# ConveneAI Minutes — AI Meeting Summarizer & Analytics Board

**ConveneAI Minutes** is a glassmorphic meeting intelligence workstation designed to parse transcripts, analyze conversational stats, and compile premium summaries. It features an interactive action item deliverables checklist, speaker word share counters, topic weight bars, and dialogue sentiment flow charts.

---

## Key Features

1. **Dialogue Transcript Parser**:
   - Parses turn lines beginning with speaker names (e.g. `Sarah: Welcome team`).
   - Calculates word tallies to audit speaker participation percentages.
2. **Dialogue Sentiment & Topic Analyzers**:
   - Tracks timeline sentiment flow across 5 chronological segments using simple valence counts.
   - Plots topic keyword weights (Tech, Marketing, Operations, Finance) from dialogues.
3. **Structured Minutes Recap Compiler**:
   - Generates an executive overview and a list of key decisions.
   - Parses tasks and constructs an interactive **Action Items Checklist** with owners, priority tags, and timeline tracking.
4. **Markdown Recaps Exporter**:
   - One-click copy or file download to save minutes in standard markdown format.
5. **Interactive Visualization Boards**:
   - Fully interactive graphs using **Chart.js** detailing speaker share donuts, sentiment timelines, and topic weights.

---

## Installation & Setup

### Prerequisites
- Python 3.9+

### Local Run
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Start the FastAPI server:
   ```bash
   uvicorn main:app --reload
   ```

3. Open your browser and navigate to:
   ```
   http://127.0.0.1:8000
   ```

---

## Running Verification Tests

We have included a programmatic test suite `verify_summarizer.py` to audit our transcript parser, sentiment calculations, and action items extraction rules.

Run the test suite using:
```bash
python verify_summarizer.py
```

All 9 assertions will run, confirming that speaker turns compile correctly, word counts are precise, and action items capture the correct owners.

---

## Docker Deployment

To build and run the playground container:

1. Build the Docker image:
   ```bash
   docker build -t ai-meeting-summarizer .
   ```

2. Run the container:
   ```bash
   docker run -p 8000:8000 ai-meeting-summarizer
   ```

3. Access the dashboard at `http://localhost:8000`.
