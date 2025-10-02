# extractor.py
import base64
import openai
import pdfplumber
from PIL import Image
import json
from io import BytesIO


class MedicalPDFExtractor:
    def __init__(self, api_key):
        self.client = openai.OpenAI(api_key=api_key)

    def pdf_to_images(self, pdf_path):
        pages = []
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                pil_image = page.to_image(resolution=200).original
                pages.append(pil_image)
        return pages

    def extract_medical_data(self, image: Image.Image):
        try:
            buffered = BytesIO()
            image.save(buffered, format="PNG")
            buffered.seek(0)
            base64_image = base64.b64encode(buffered.read()).decode('utf-8')

            prompt = (
                "Extract the following information from this medical report image "
                "and return only the JSON object, nothing else:\n"
                "{\n"
                "  'patient': {\n"
                "    'name': 'string or null',\n"
                "    'age': 'string or null',\n"
                "    'gender': 'string or null',\n"
                "    'date_of_report': 'string or null'\n"
                "  },\n"
                "  'tests': [\n"
                "    {\n"
                "      'test_name': 'string',\n"
                "      'value': 'string',\n"
                "      'unit': 'string or null'\n"
                "    }\n"
                "  ],\n"
                "  'diagnosis': 'string'\n"
                "}"
            )

            messages = [
                {"role": "system", "content": "You are an expert medical data analyst."},
                {"role": "user", "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{base64_image}"}}
                ]}
            ]

            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=messages,
                temperature=0.2,
                max_tokens=2048
            )

            content = response.choices[0].message.content.strip()

            if content.startswith("```json"):
                content = content[7:].strip()
            if content.endswith("```"):
                content = content[:-3].strip()

            parsed_data = json.loads(content)

            if not isinstance(parsed_data, dict) or "patient" not in parsed_data or "tests" not in parsed_data or "diagnosis" not in parsed_data:
                raise ValueError("Invalid JSON structure returned from OpenAI")
            return parsed_data

        except Exception as e:
            raise RuntimeError(f"Extraction failed: {e}")
