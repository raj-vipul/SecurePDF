import re
import fitz  # PyMuPDF
import os

# General redaction patterns
patterns = [
    r"\b[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,6}\b",               # Email
    r"\b(?:\+91[\-\s]?)?[6-9]\d{9}\b",                                    # Indian phone
    r"\b[A-Z]{4}0[A-Z0-9]{6}\b",                                          # IFSC
    r"\b(?:\d[ -]?){13,19}\b",                                            # Card number
    r"\b[a-zA-Z0-9._-]{2,256}@[a-zA-Z]{2,64}\b",                          # UPI ID
    r"\b\d{4}[\s-]?\d{4}[\s-]?\d{4}\b",                                   # Aadhaar
    r"\b[A-Z]{5}[0-9]{4}[A-Z]\b",                                         # PAN
    r"\b\d{3}-\d{2}-\d{4}\b",                                             # SSN
    r"\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b",                                 # Date
    r"\b\d{6}\b",                                                         # PIN code
    r"\b\d{9,18}\b",                                                      # Bank account
    r"\b[A-Z0-9]{12,}\b"                                                  # Transaction ID
]


def redact_pii(input_pdf_path):
    # Load the PDF
    doc = fitz.open(input_pdf_path)

    # Redact patterns page by page
    for page in doc:
        text = page.get_text()
        for pattern in patterns:
            for match in re.finditer(pattern, text):
                for rect in page.search_for(match.group()):
                    page.add_redact_annot(rect, fill=(0, 0, 0))  # Black out
        page.apply_redactions()

    # Save redacted file
    filename = os.path.basename(input_pdf_path)
    redacted_name = f"redacted_{filename}"
    redacted_path = os.path.join(os.path.dirname(input_pdf_path), redacted_name)
    doc.save(redacted_path)
    doc.close()

    return redacted_path

