import io
from typing import Tuple
from PIL import Image
import easyocr
import pytesseract
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"


# Instantiate reader once for performance (supports English; add languages as needed)
reader = easyocr.Reader(["en"], gpu=False)  # set gpu=True if available

def image_to_text(image_bytes):
    try:
        # Convert bytes → PIL image
        image = Image.open(io.BytesIO(image_bytes))
        
        # Optional: convert to RGB (avoids mode errors)
        image = image.convert("RGB")

        # OCR extraction
        text = pytesseract.image_to_string(image)

        # Confidence: rough estimation (pytesseract doesn't give numeric confidence easily)
        conf = 0.9 if len(text.strip()) > 10 else 0.5
        
        return text, conf

    except Exception as e:
        raise ValueError(f"OCR failed: {e}")