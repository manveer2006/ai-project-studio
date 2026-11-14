"""
AI Project Studio - a small web workspace for AI-generated text.
Backend: Flask. Model: Google Gemini (REST API).
If no API key is configured the app runs in DEMO mode so it can still be shown.
"""
import json
import os
from pathlib import Path

import requests
from dotenv import load_dotenv
from flask import Flask, jsonify, render_template, request

load_dotenv()  # reads GEMINI_API_KEY from a local .env file (never hard-code keys)

BASE_DIR = Path(__file__).parent
app = Flask(__name__)

MAX_INPUT_CHARS = 6000
API_URL = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"


def load_config():
    with open(BASE_DIR / "prompts.json", encoding="utf-8") as f:
        return json.load(f)


CONFIG = load_config()
TASKS = {t["id"]: t for t in CONFIG["tasks"]}


def build_prompt(task, user_input, tone, points):
    """Fill the reusable prompt template of the chosen task."""
    return task["template"].format(input=user_input, tone=tone, points=points)


def demo_response(task, user_input):
    """Offline placeholder so the interface can be demonstrated without an API key."""
    snippet = user_input.strip().replace("\n", " ")[:80]
    return (
        f"[DEMO MODE - no API key found]\n"
        f"Task: {task['label']}\n"
        f"Your input began with: \"{snippet}...\"\n\n"
        f"Add GEMINI_API_KEY to your .env file to get real AI output."
    )


def call_gemini(system_text, prompt, temperature):
    key = os.getenv("GEMINI_API_KEY", "").strip()
    model = os.getenv("GEMINI_MODEL", "gemini-3.8-flash")
    body = {
        "system_instruction": {"parts": [{"text": system_text}]},
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"maxOutputTokens": 800},
    }
    resp = requests.post(
        API_URL.format(model=model),
        headers={"x-goog-api-key": key, "Content-Type": "application/json"},
        json=body,
        timeout=40,
    )
    if resp.status_code != 200:
        raise RuntimeError(f"API error {resp.status_code}: {resp.text[:200]}")
    data = resp.json()
    try:
        return data["candidates"][0]["content"]["parts"][0]["text"].strip()
    except (KeyError, IndexError):
        raise RuntimeError("The model returned no text (it may have been blocked).")


@app.route("/")
def index():
    return render_template("index.html", tasks=CONFIG["tasks"], tones=CONFIG["tones"])


@app.route("/api/generate", methods=["POST"])
def generate():
    payload = request.get_json(silent=True) or {}
    task_id = payload.get("task")
    user_input = (payload.get("input") or "").strip()
    tone = payload.get("tone") or "Neutral"
    try:
        points = int(payload.get("points", 5))
    except (TypeError, ValueError):
        points = 5

    # ---- input validation ----
    if task_id not in TASKS:
        return jsonify(error="Please choose a valid task."), 400
    if not user_input:
        return jsonify(error="Input is empty. Please type something first."), 400
    if len(user_input) > MAX_INPUT_CHARS:
        return jsonify(error=f"Input too long (max {MAX_INPUT_CHARS} characters)."), 400
    if tone not in CONFIG["tones"]:
        tone = "Neutral"
    points = max(1, min(points, 10))

    task = TASKS[task_id]
    prompt = build_prompt(task, user_input, tone, points)
    demo = not os.getenv("GEMINI_API_KEY", "").strip()

    try:
        output = demo_response(task, user_input) if demo else call_gemini(task["system"], prompt, 0.7)
    except (RuntimeError, requests.RequestException) as exc:
        return jsonify(error=str(exc), prompt=prompt), 502

    return jsonify(output=output, prompt=prompt, demo=demo)


if __name__ == "__main__":
    app.run(debug=True, port=5001)
