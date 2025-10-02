# 🩺 Medical Report Extractor — FastAPI Quickstart

A minimal, step-by-step README to get the **FastAPI `/lab`** endpoint running locally. This repo uses your existing extractor logic (OpenAI + `gpt-4o`) and saves extracted JSON/CSV in `data/`.
(You said you’re **not** pushing the Streamlit app — this README covers *only* the FastAPI flow.)

---

## What this does (quick)

* Accepts one or more PDF/image files via `POST /lab`.
* Uses your `MedicalPDFExtractor` (OpenAI) to extract JSON per report.
* Merges multi-page results and returns JSON for each file.
* Optionally appends results to `data/extracted_reports.csv`.

---

## Files (important)

* `main.py` — FastAPI app with `/lab` endpoint
* `extractor.py` — extraction logic (prompt kept as-is)
* `utils.py` — `initialize_record()` and `merge_records()`
* `save_to_csv.py` — appends results to CSV
* `requirements.txt` — Python deps
* `.env` — store `OPENAI_API_KEY` (not checked into git)
* `data/` — output CSV/JSON files (created automatically)

---

## Prerequisites

* Python 3.10+
* Git (optional)
* OpenAI API key with access to the model you use

---

## 1) Clone repo

```bash
git clone https://github.com/yourusername/medical-report-extractor.git
cd medical-report-extractor
```

---

## 2) Create & activate virtualenv

```bash
python -m venv venv
# mac/linux
source venv/bin/activate
# windows (PowerShell)
venv\Scripts\Activate.ps1
```

---

## 3) Install dependencies

Create or update `requirements.txt` with (example):

```
fastapi
uvicorn[standard]
python-dotenv
openai
pillow
pdfplumber
pandas
```

Then install:

```bash
pip install -r requirements.txt
```

---

## 4) Add OpenAI key

Create a `.env` file in project root:

```
OPENAI_API_KEY=sk-xxxxxx...
```

> The extractor uses this env var to initialize the OpenAI client. Don’t commit `.env`.

---

## 5) Run the FastAPI server

Start the app:

```bash
uvicorn main:app --reload
```

* Default local address: `http://127.0.0.1:8000`
* Auto-reload for development is enabled with `--reload`.

---

## 6) Use the `/lab` endpoint

### curl (single file)

```bash
curl -X POST "http://127.0.0.1:8000/lab" \
  -F "files=@/path/to/report1.pdf"
```

### curl (multiple files)

```bash
curl -X POST "http://127.0.0.1:8000/lab" \
  -F "files=@/path/to/report1.pdf" \
  -F "files=@/path/to/report2.jpg"
```

### Python `requests` example

```python
import requests

url = "http://127.0.0.1:8000/lab"
files = [("files", open("report1.pdf","rb")), ("files", open("report2.jpg","rb"))]
resp = requests.post(url, files=files)
print(resp.status_code)
print(resp.json())   # dictionary: { "report1.pdf": {...extracted json...}, ... }
```

---

## 7) Response format (example)

The API returns a JSON object mapping filenames → extracted record:

```json
{
  "report1.pdf": {
    "patient": {
      "name": "John Doe",
      "age": "45",
      "gender": "Male",
      "date_of_report": "2025-09-01"
    },
    "tests": [
      {"test_name": "Hemoglobin", "value": "13.2", "unit": "g/dL"},
      {"test_name": "Glucose (Fasting)", "value": "135", "unit": "mg/dL"}
    ],
    "diagnosis": "Not Mentioned"
  }
}
```

CSV output (if enabled) is written to `data/extracted_reports.csv` (appends rows per file).

---

## 8) Notes & tips

* **Prompt unchanged:** The prompt in `extractor.py` is intentionally left as you wrote it. I did not modify it.
* **Temporary files:** The server uses temporary files; they are cleaned up after processing.
* **Large files:** If processing fails, check server logs. Consider increasing timeouts or splitting very large PDFs into smaller pages.
* **Unit canonicalization & validation:** Not included by default — recommended next step before production.
* **Concurrency:** `uvicorn` + FastAPI handle concurrent requests; if you expect high volume, run with multiple workers or behind a production ASGI server.

---

## 9) Troubleshooting

* `400/500` errors — check terminal logs for exception details.
* `OPENAI_API_KEY missing` — ensure `.env` exists and app restarted after changes.
* `pdfplumber` errors on unusual PDFs — try converting the PDF to images first (tooling/scripts can be added).

---

## 10) Next steps (recommended)

* Add unit standardization (mmol/L → mg/dL etc.).
* Add canonical test-name mapping (Hb → Hemoglobin) before saving results.
* Add validation of model output (Pydantic models).
* Add optional RAG/Pinecone retrieval if you want context-guided extraction.
* Add authentication (API key or bearer token) for production.

---

If you want, I can now:

* Create a **minimal `main.py`** example (exact code used by your FastAPI endpoint) for the repo, or
* Add **Pydantic response models** to validate the extractor output before returning.

Which would you like next?
