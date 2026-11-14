# AI Project Studio

A simple web workspace where a user picks a task, types an input and receives AI-generated text, summaries or ideas.

## Features
- 5 task options: Summarizer, Idea Generator, Concept Explainer, Email Writer, Text Generator
- Reusable prompt templates stored in `prompts.json` (edit prompts without touching code)
- Tone and length controls
- "Show the prompt that was sent" panel for transparency
- Input validation, error messages, session history, copy button
- Demo mode when no API key is set

## Setup
1. Install Python 3.10+.
2. `pip install -r requirements.txt`
3. Get a free Gemini API key from Google AI Studio.
4. Copy `.env.example` to `.env` and paste your key after `GEMINI_API_KEY=` (never share or upload `.env`).
5. `python app.py` and open http://127.0.0.1:5000

Without a key the app still starts in demo mode (placeholder output only).

## Tests
`python test_app.py`

## Files
| File | Purpose |
|---|---|
| app.py | Flask backend, prompt building, Gemini API call |
| prompts.json | Task definitions and prompt templates |
| templates/index.html | Web interface |
| test_app.py | Automated tests |
| .env.example | Template for the API key (no real key) |
