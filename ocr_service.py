import pytesseract
import re
import pymupdf
from PIL import Image
import io
import os
import cv2
import numpy as np
from google import genai
import json
from dotenv import load_dotenv

load_dotenv()

# Ensure Tesseract executable is found (adjust path if necessary)
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def preprocess_image(image_path):
    """Preprocess image for better OCR results."""
    img = cv2.imread(image_path)
    if img is None:
        return None
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # Increase contrast, remove noise
    thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
    return thresh

def extract_text_from_image(image_path):
    """Extract text from an image using Tesseract OCR with preprocessing."""
    processed = preprocess_image(image_path)
    if processed is not None:
        # --psm 6 treats the image as a single uniform block of text
        return pytesseract.image_to_string(processed, config="--psm 6")
    else:
        # Fallback if cv2 fails to read
        return pytesseract.image_to_string(Image.open(image_path), config="--psm 6")

def extract_text_from_pdf(pdf_path):
    """Convert PDF pages to images and extract text."""
    text = ""
    doc = pymupdf.open(pdf_path)
    for page in doc:
        pix = page.get_pixmap(dpi=300)
        img = Image.open(io.BytesIO(pix.tobytes()))
        # Save temporarily for cv2 processing
        temp_img_path = pdf_path + "_temp.png"
        img.save(temp_img_path)
        text += extract_text_from_image(temp_img_path) + "\n"
        if os.path.exists(temp_img_path):
            os.remove(temp_img_path)
    return text

def extract_text_from_file(file_path):
    """Determine file type and extract text accordingly."""
    if file_path.lower().endswith('.pdf'):
        return extract_text_from_pdf(file_path)
    else:
        return extract_text_from_image(file_path)

def parse_invoice_text(raw_text):
    """Extract specific fields from raw OCR text using Gemini."""
    client = genai.Client()
    
    prompt = f"""
Extract invoice information from the text below.

Return ONLY valid JSON with these exact fields:
invoice_number,
buyer_name,
invoice_date,
due_date,
invoice_amount,
amount_paid,
currency,
missing_fields,
confidence_notes

Rules:
- Do not invent missing values.
- Use null when a value is unavailable.
- Preserve the exact invoice number.
- Return dates in YYYY-MM-DD format.
- Return amounts as numbers only.

Text:
{raw_text}
"""
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )
        
        raw_output = response.text.strip()
        raw_output = raw_output.replace("```json", "").replace("```", "").strip()
        
        return json.loads(raw_output)
    except Exception as e:
        print(f"Gemini extraction failed: {e}")
        return {}

