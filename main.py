# main.py
import os
import tempfile
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
from extractor import MedicalPDFExtractor
from utils import initialize_record, merge_records
from save_to_csv import save_to_csv
from PIL import Image

load_dotenv()
API_KEY = os.getenv("OPENAI_API_KEY")
if not API_KEY:
    raise RuntimeError("OpenAI API key not found in environment variables")

DATA_DIR = "data"
os.makedirs(DATA_DIR, exist_ok=True)

app = FastAPI(title="Medical Report Extractor API")

extractor = MedicalPDFExtractor(API_KEY)

@app.post("/lab")
async def extract_lab_reports(files: list[UploadFile] = File(...)):
    all_results = {}
    for uploaded_file in files:
        merged_data = initialize_record()
        try:
            # Save temporarily
            with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(uploaded_file.filename)[1]) as tmp:
                tmp.write(await uploaded_file.read())
                temp_path = tmp.name

            ext = uploaded_file.filename.lower().split(".")[-1]
            pages = []

            if ext == "pdf":
                pages = extractor.pdf_to_images(temp_path)
            else:
                image = Image.open(temp_path).convert("RGB")
                pages = [image]

            for page in pages:
                page_data = extractor.extract_medical_data(page)
                if page_data:
                    merged_data = merge_records(merged_data, page_data)

            # Optional: save to CSV
            save_to_csv(merged_data, uploaded_file.filename, os.path.join(DATA_DIR, "extracted_reports.csv"))

            all_results[uploaded_file.filename] = merged_data

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error processing {uploaded_file.filename}: {e}")
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)

    return JSONResponse(content=all_results)

