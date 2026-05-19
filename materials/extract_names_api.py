"""
Extract Chinese personal names by calling LM Studio's local API.

Non-deterministic: same input may give different output across runs.

Before running:
  1. Open LM Studio.
  2. Click the "Developer" tab on the left (older versions: "Local Server").
  3. Click "Start Server". The endpoint appears, usually http://localhost:1234.
  4. Make sure Qwen3.5 0.8B is loaded in the chat side.

Uses only the Python standard library. No `pip install` needed.
"""

import csv
import json
import urllib.request
from pathlib import Path

# --- Configuration ---
API_URL = "http://localhost:1234/v1/chat/completions"
# The model ID shown in LM Studio -> Developer -> "API Model Identifier".
# If your loaded model is different, change this string accordingly.
MODEL = "qwen3.5-0.8b"
TEMPERATURE = 0.7

# --- Paths ---
HERE = Path(__file__).parent
SYSTEM_PROMPT_FILE = HERE / "system_prompt.txt"
SENTENCES_FILE = HERE / "sentences.txt"
OUTPUT_FILE = HERE / "api_output.csv"

# --- Load the system prompt and sentences ---
system_prompt = SYSTEM_PROMPT_FILE.read_text(encoding="utf-8").strip()
sentences = [s.strip() for s in SENTENCES_FILE.read_text(encoding="utf-8").splitlines() if s.strip()]

# --- Call the API for each sentence ---
rows = []
for i, sentence in enumerate(sentences, start=1):
    payload = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": sentence},
        ],
        "temperature": TEMPERATURE,
    }
    req = urllib.request.Request(
        API_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req) as resp:
        response = json.load(resp)

    raw = response["choices"][0]["message"]["content"].strip()

    # The model was asked to return a JSON array. If it didn't, log the raw text.
    try:
        names = json.loads(raw)
        if not isinstance(names, list):
            names = [f"(non-list response: {raw})"]
    except json.JSONDecodeError:
        names = [f"(unparseable: {raw})"]

    if not names:
        rows.append((i, sentence, "", "api"))
    else:
        for name in names:
            rows.append((i, sentence, str(name), "api"))

    print(f"[{i}/{len(sentences)}] {sentence} -> {names}")

# --- Write CSV ---
with OUTPUT_FILE.open("w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["sentence_id", "sentence", "extracted_name", "method"])
    writer.writerows(rows)

print(f"\nProcessed {len(sentences)} sentences.")
print(f"Wrote {len(rows)} rows to {OUTPUT_FILE.name}.")
