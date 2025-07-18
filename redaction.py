import fitz  # PyMuPDF
import pytesseract
from PIL import Image, ImageDraw
from presidio_analyzer import AnalyzerEngine, PatternRecognizer, Pattern
import spacy
import re
from pathlib import Path

# Set Tesseract path (Windows only)
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# === Load spaCy model ===
nlp = spacy.load("en_core_web_md")

# === Initialize Presidio ===
analyzer = AnalyzerEngine()



def redact_person_names(text):
   
    doc = nlp(text)
    redacted_text = text

    for ent in doc.ents:
        if ent.label_ == "PERSON":
            person_name = ent.text
            redacted_text = redacted_text.replace(person_name, "[REDACTED_PERSON]")

    return redacted_text


def redact_phone_numbers(text):
   
    # Using Presidio to detect phone numbers
    presidio_results = analyzer.analyze(text=text, language='en')
    redacted_text = text

    for result in presidio_results:
        if result.entity_type == "PHONE_NUMBER":
            phone_number = text[result.start:result.end]
            redacted_text = redacted_text.replace(phone_number, "[REDACTED_PHONE]")

    # in case presuido is unable to recognize , Use regex as a fallback
    pattern = r"\+?\d{1,3}[-.\s]?\(?\d{1,4}\)?[-.\s]?\d{1,4}[-.\s]?\d{1,9}"
    redacted_text = re.sub(pattern, "[REDACTED_PHONE]", redacted_text)

    return redacted_text

def redact_email_addresses(text):
    #Using Presidio
    presidio_results = analyzer.analyze(text=text, language='en')
    redacted_text = text

    for result in presidio_results:
        if result.entity_type == "EMAIL_ADDRESS":
            email_address = text[result.start:result.end]
            redacted_text = redacted_text.replace(email_address, "[REDACTED_EMAIL]")

    # Using regex as a fallback
    pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b'
    redacted_text = re.sub(pattern, "[REDACTED_EMAIL]", redacted_text)

    return redacted_text


def redact_aadhaar(text):
    # Regex  for Aadhaar numbers
    aadhaar_pattern = r'\b\d{4}[\s-]?\d{4}[\s-]?\d{4}\b'

    # Contextual keywords to validate Aadhaar numbers
    aadhaar_keywords = ["aadhaar", "uid", "govt id", "identity card"]

    # Split text into sentences for contextual validation
    sentences = text.split(".")
    redacted_text = text

    for sentence in sentences:
        # Check if the sentence contains any Aadhaar-related keywords
        if any(keyword.lower() in sentence.lower() for keyword in aadhaar_keywords):
            # Find Aadhaar numbers in the sentence
            matches = re.findall(aadhaar_pattern, sentence)
            for match in matches:
                # Replace Aadhaar number with redacted text
                redacted_text = redacted_text.replace(match, "[REDACTED_AADHAAR]")

    return redacted_text
def redact_addresses(text):
    # Using Presidio to detect addresses
    presidio_results = analyzer.analyze(text=text, language='en')
    redacted_text = text

    for result in presidio_results:
        if result.entity_type == "ADDRESS":
            address = text[result.start:result.end]
            redacted_text = redacted_text.replace(address, "[REDACTED_ADDRESS]")
    
    #using spacy for GPE
    doc = nlp(text)
    for ent in doc.ents:
        if ent.label_ == "GPE":
            gpe = ent.text
            redacted_text = redacted_text.replace(gpe, "[REDACTED_GPE]")

    # regex as a fallback
    # Regex pattern for common address formats
    pattern = r'\d{1,5}\s[\w\s.,-]+(?:Street|St|Avenue|Ave|Road|Rd|Lane|Ln|Boulevard|Blvd|Drive|Dr|Court|Ct|Square|Sq|Building|Bldg|Block|Blk|Floor|Fl|Apartment|Suite|Ste|Unit|#)?[\w\s.,-]*'
    redacted_text = re.sub(pattern, "[REDACTED_ADDRESS]", redacted_text, flags=re.IGNORECASE)

    return redacted_text

def redact_pan(text):
    presidio_results = analyzer.analyze(text=text, language='en')
    redacted_text = text

    for result in presidio_results:
        if result.entity_type == "PAN":
            pan_number = text[result.start:result.end]
            redacted_text = redacted_text.replace(pan_number, "[REDACTED_PAN]")
    
    pattern = r'\b[A-Z]{5}[0-9]{4}[A-Z]\b'
    redacted_text = re.sub(pattern, "[REDACTED_PAN]", redacted_text)
    return redacted_text


#  Redaction Function
def redact_pii_on_image(pil_image):
    
    data = pytesseract.image_to_data(pil_image, output_type=pytesseract.Output.DICT)
    full_text = " ".join(data["text"])

    # Apply redaction functions
    redacted_text = redact_person_names(full_text)
    redacted_text = redact_phone_numbers(redacted_text)
    redacted_text = redact_email_addresses(redacted_text)
    redacted_text = redact_addresses(redacted_text)
    redacted_text = redact_aadhaar(redacted_text)
    redacted_text = redact_pan(redacted_text)



    # Draw redactions on the image
    draw = ImageDraw.Draw(pil_image)
    for i, word in enumerate(data["text"]):
        word_clean = word.strip()
        if word_clean != "" and word_clean in full_text and word_clean not in redacted_text:
            x, y, w, h = data["left"][i], data["top"][i], data["width"][i], data["height"][i]
            draw.rectangle([x, y, x + w, y + h], fill="black")

    return pil_image

# === PDF Redaction Function ===
def redact_pdf_with_pymupdf(input_pdf_path):

    pdf_path = Path(input_pdf_path)
    output_pdf_path = pdf_path.with_name(pdf_path.stem + "_redacted.pdf")

    doc = fitz.open(str(pdf_path))
    redacted_images = []

    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        pix = page.get_pixmap(dpi=200)
        image = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

        print(f"[INFO] Processing Page {page_num + 1}/{len(doc)}...")
        redacted_image = redact_pii_on_image(image)
        redacted_images.append(redacted_image.convert("RGB"))

    # Save the redacted pages to a new PDF
    redacted_images[0].save(output_pdf_path, save_all=True, append_images=redacted_images[1:])
    print(f"[SUCCESS] Redacted PDF saved as: {output_pdf_path}")


if __name__ == "__main__":
    redact_pdf_with_pymupdf("indian_pii_document.pdf")