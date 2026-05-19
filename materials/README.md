# Session 04 — Materials

This folder holds the materials for the deterministic-vs-non-deterministic name-extraction demo.

## Files

| File | Purpose |
|---|---|
| `baijiaxing.txt` | The most common Chinese single-character surnames, from the canonical 百家姓. One per line. Used by the regex script. |
| `sentences.txt` | The corpus of modern-Chinese newspaper sentences we run extraction on. One sentence per line. |
| `system_prompt.txt` | The Chinese NER instruction sent to the LLM as a system prompt. |
| `extract_names_regex.py` | Approach 1 — deterministic regex extraction. Reads `baijiaxing.txt` + `sentences.txt`, writes `regex_output.csv`. |
| `extract_names_api.py` | Approach 2 — non-deterministic LM Studio API extraction. Reads `system_prompt.txt` + `sentences.txt`, writes `api_output.csv`. |
| `regex_output.csv` | Created when the regex script runs. |
| `api_output.csv` | Created when the API script runs. |

## In session

You do not type any of this code yourself today. **Codex orchestrates**: it reads the scripts, runs them, explains them when you ask, and writes the output. The point is the *contrast between the two outputs*, not the code.

After the session you can re-read the scripts and modify them. Both are intentionally short and use only Python's standard library — no `pip install` needed.

## How to run them yourself (outside the session)

Open a terminal inside Codex Desktop (⌘J on macOS, or the terminal icon at the top right), then:

```bash
cd ~/genai-workshop/session-04/materials
python3 extract_names_regex.py     # Approach 1 — deterministic
python3 extract_names_api.py       # Approach 2 — non-deterministic (LM Studio server must be running)
```
