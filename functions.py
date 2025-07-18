import re
import spacy

nlp = spacy.load("en_core_web_sm")

def common(text):
    doc = nlp(text)
    redacted_text = text

    # 1. Redact names and addresses using spaCy NER
    pii_labels = ["NAME", "GPE", "LOC"]
    for ent in doc.ents:
        if ent.label_ in pii_labels:
            redacted_text = redacted_text.replace(ent.text, f"[{ent.label_}]") 
    return redacted_text


# EMAIL REDACTION FUNCTION
def redact_email(text):
    pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b'
    return re.sub(pattern, '[REDACTED_EMAIL]', text)

# NAME REDACTION FUNCTION (simple title case match)
def redact_name(text):
    pattern = r'\b[A-Z][a-z]+(?: [A-Z][a-z]+){0,2}\b'
    return re.sub(pattern, '[REDACTED_NAME]', text)

# PHONE NUMBER REDACTION FUNCTION (Indian format)
def redact_phone(text):
    pattern = r'\b(?:\+91[-\s]?)?[789]\d{9}\b'
    return re.sub(pattern, '[REDACTED_PHONE]', text)

# AADHAAR REDACTION FUNCTION
def redact_aadhaar(text):
    pattern = r'\b\d{4}[\s-]?\d{4}[\s-]?\d{4}\b'
    return re.sub(pattern, '[REDACTED_AADHAAR]', text)

# PAN REDACTION FUNCTION
def redact_pan(text):
    pattern = r'\b[A-Z]{5}[0-9]{4}[A-Z]\b'
    return re.sub(pattern, '[REDACTED_PAN]', text)

# PASSPORT REDACTION FUNCTION
def redact_passport(text):
    pattern = r'\b[A-Z][0-9]{7}\b'
    return re.sub(pattern, '[REDACTED_PASSPORT]', text)

# VOTER ID REDACTION FUNCTION
def redact_voter_id(text):
    pattern = r'\b[A-Z]{3}[0-9]{7}\b'
    return re.sub(pattern, '[REDACTED_VOTERID]', text)

# BANK ACCOUNT REDACTION FUNCTION (Indian, 9 to 18 digits)
def redact_bank_account(text):
    pattern = r'\b\d{9,18}\b'
    return re.sub(pattern, '[REDACTED_BANK]', text)
