import fitz  # PyMuPDF
import pytesseract
import cv2
import numpy as np
import re

# Regex patterns to redact
patterns = [
    r"\b\d{4}[\s-]?\d{4}[\s-]?\d{4}\b",        # Aadhaar
    r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", #email
    r"(?i)(fax[:\s]*)?(?:\+1\s?)?(?:\(?\d{3}\)?[\s.-]?)?\d{3}[\s.-]?\d{4}" #fax

    r"\b[A-Z]{5}[0-9]{4}[A-Z]\b",              # PAN
    r"\b[A-Z]{3}[0-9]{7}\b",                   # Voter ID
    r"\b[A-Z]{1,2}[0-9]{7}\b",                 # Passport
    r"\b\d{3}-\d{2}-\d{4}\b",                  # SSN
    r"\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}",

    r'(?:\+1\s?)?(?:\(?\d{3}\)?[\s.-]?)?\d{3}[\s.-]?\d{4}'          # Indian phone
]

# Load the scanned PDF
doc = fitz.open("pwmm.pdf")

for page_num, page in enumerate(doc):
    print(f"\n📄 OCR Text from Page {page_num + 1}:\n" + "-"*40)
    
    # Render page as image
    pix = page.get_pixmap(dpi=300)
    img = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width, pix.n)
    if pix.n == 4:
        img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)

    # 🔍 OCR Text Extraction (for printing)
    extracted_text = pytesseract.image_to_string(img)
    print(extracted_text)

    # 🔍 OCR with bounding boxes for redaction
    ocr_data = pytesseract.image_to_data(img, output_type=pytesseract.Output.DICT)

    for i, word in enumerate(ocr_data['text']):
        for pattern in patterns:
            if re.fullmatch(pattern, word.strip()):
                # Get bounding box
                x, y, w, h = (ocr_data['left'][i], ocr_data['top'][i],
                              ocr_data['width'][i], ocr_data['height'][i])

                # Map image coordinates to PDF coordinates
                pdf_rect = fitz.Rect(
                    x * page.rect.width / pix.width,
                    y * page.rect.height / pix.height,
                    (x + w) * page.rect.width / pix.width,
                    (y + h) * page.rect.height / pix.height,
                )
                page.add_redact_annot(pdf_rect, fill=(0, 0, 0))

    page.apply_redactions()

# Save the final redacted PDF
doc.save("redacted_scanned_output.pdf")
print("\n✅ Scanned PDF redacted and saved as 'redacted_scanned_output.pdf'")
