import os
import logging
import tempfile
import pytesseract
import pdfplumber
import pandas as pd
from pdf2image import convert_from_path
from docx import Document
from PIL import Image

def extract_from_docx(file_path):
    doc = Document(file_path)
    return "\n".join([p.text for p in doc.paragraphs if p.text.strip()])

def extract_from_csv(file_path):
    df = pd.read_csv(file_path)
    return df.to_string(index=False)

def extract_from_xlsx(file_path):
    try:
        df = pd.read_excel(file_path)
        return df.to_string(index=False)
    except Exception as e:
        logging.error(f"Failed to extract from xlsx: {e}")
        return ""

def extract_from_image(file_path):
    return pytesseract.image_to_string(Image.open(file_path), config='--psm 6 -l eng+nld')

async def ocr_with_tesseract(pdf_path):
    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            images = convert_from_path(pdf_path, dpi=150, output_folder=temp_dir)
            full_text = ""
            for image in images:
                full_text += pytesseract.image_to_string(image, config='--psm 6 -l eng+nld') + "\n"
            return full_text.strip()
    except Exception as e:
        logging.error(f"Tesseract OCR failed: {e}")
        return ""

def extract_with_pdfplumber(file_path):
    try:
        text = ""
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                text += page.extract_text() or ""
        return text.strip()
    except Exception as e:
        logging.warning(f"pdfplumber failed: {e}")
        return ""

async def extract_text(file_path: str, extension: str) -> str:
    try:
        if extension == ".pdf":
            text = extract_with_pdfplumber(file_path)
            if not text:
                logging.warning("pdfplumber found no text, using Tesseract fallback.")
                return await ocr_with_tesseract(file_path)
            return text
        elif extension == ".docx":
            return extract_from_docx(file_path)
        elif extension == ".csv":
            return extract_from_csv(file_path)
        elif extension == ".xlsx":
            return extract_from_xlsx(file_path)
        elif extension in [".png", ".jpg", ".jpeg"]:
            return extract_from_image(file_path)
        else:
            raise ValueError("Unsupported file format")
    except Exception as e:
        logging.error(f"Text extraction failed: {e}")
        return ""
