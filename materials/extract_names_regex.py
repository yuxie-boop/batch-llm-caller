"""
Extract Chinese personal names from sentences using a baijiaxing surname list.

Deterministic: same input -> same output, every time.

Strategy:
- Read a list of single-character Chinese surnames (baijiaxing.txt).
- Build a regex: any surname character + 1 to 2 Chinese characters.
- Apply the regex to every sentence in sentences.txt.
- Write results to regex_output.csv.

Uses only the Python standard library. No `pip install` needed.
"""

import csv
import re
from pathlib import Path

HERE = Path(__file__).parent
SURNAMES_FILE = HERE / "baijiaxing.txt"
SENTENCES_FILE = HERE / "sentences.txt"
OUTPUT_FILE = HERE / "regex_output.csv"

# Load the surname dictionary
surnames = [s.strip() for s in SURNAMES_FILE.read_text(encoding="utf-8").splitlines() if s.strip()]

# Build the regex: [any surname char] + 1 to 2 Chinese characters
# 一-鿿 is the basic CJK Unified Ideographs Unicode block
surname_class = "[" + "".join(surnames) + "]"
name_pattern = re.compile(surname_class + r"[一-鿿]{1,2}")

# Load sentences
sentences = [s.strip() for s in SENTENCES_FILE.read_text(encoding="utf-8").splitlines() if s.strip()]

# Extract
rows = []
for i, sentence in enumerate(sentences, start=1):
    matches = name_pattern.findall(sentence)
    if not matches:
        rows.append((i, sentence, "", "regex"))
    else:
        for name in matches:
            rows.append((i, sentence, name, "regex"))

# Write CSV
with OUTPUT_FILE.open("w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["sentence_id", "sentence", "extracted_name", "method"])
    writer.writerows(rows)

print(f"Processed {len(sentences)} sentences.")
print(f"Wrote {len(rows)} rows to {OUTPUT_FILE.name}.")
