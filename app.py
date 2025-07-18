import os
import re
import shutil
import pytesseract
import nltk
from flask import Flask, render_template, request, redirect, url_for
from werkzeug.utils import secure_filename
from PyPDF2 import PdfReader
from fpdf import FPDF
from pdf2image import convert_from_path
from PIL import Image, ImageDraw

# NLTK setup
from nltk import word_tokenize, pos_tag
nltk.download('punkt')
nltk.download('averaged_perceptron_tagger')

# Flask app config
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['STATIC_UPLOAD_FOLDER'] = os.path.join('static', 'uploads')

# Ensure folders exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['STATIC_UPLOAD_FOLDER'], exist_ok=True)

# Regex patterns
regex_patterns = {
    "email": r"\b[\w.-]+?@\w+?\.\w+?\b",
    "phone": r"(\+?\d{1,3}[-.\s]?)?\(?\d{3,5}\)?[-.\s]?\d{3,5}[-.\s]?\d{4}",
    "ssn": r"\b\d{3}-\d{2}-\d{4}\b",
    "ip": r"\b(?:\d{1,3}\.){3}\d{1,3}\b",
    "aadhar": r"\b\d{4}[\s-]?\d{4}[\s-]?\d{4}\b",
    "pan": r"\b[A-Z]{5}[0-9]{4}[A-Z]\b",
    "voter": r"\b[A-Z]{3}[0-9]{7}\b",
    "credit_card": r"\b(?:\d[ -]*?){13,16}\b",
    "transaction_id": r"\b[a-zA-Z0-9]{10,}\b",
    "location": r"\b\d{1,3}\.\d{1,6},\s?\d{1,3}\.\d{1,6}\b"
}

# Detect names using NLTK
def detect_names_nltk(text):
    words = word_tokenize(text)
    tagged = pos_tag(words)
    names = [word for word, tag in tagged if tag == 'NNP']
    return names

# Redaction logic
def apply_redaction(text, redaction_type):
    redacted = text

    if redaction_type == "default":
        names = detect_names_nltk(text)
        for name in set(names):
            redacted = re.sub(rf'\b{name}\b', '[REDACTED]', redacted)

        for _, pattern in regex_patterns.items():
            redacted = re.sub(pattern, '[REDACTED]', redacted, flags=re.IGNORECASE)

    elif redaction_type in regex_patterns:
        redacted = re.sub(regex_patterns[redaction_type], '[REDACTED]', redacted, flags=re.IGNORECASE)

    elif redaction_type == "name":
        names = detect_names_nltk(text)
        for name in set(names):
            redacted = re.sub(rf'\b{name}\b', '[REDACTED]', redacted)

    elif redaction_type == "location":
        pass  # Placeholder for location redaction logic

    elif redaction_type == "govtid":
        for key in ['aadhar', 'pan', 'voter']:
            redacted = re.sub(regex_patterns[key], '[REDACTED]', redacted, flags=re.IGNORECASE)

    elif redaction_type == "financial":
        for key in ['credit_card', 'transaction_id']:
            redacted = re.sub(regex_patterns[key], '[REDACTED]', redacted, flags=re.IGNORECASE)

    return redacted

# Routes
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/uploads', methods=['POST'])
def handle_upload():
    file = request.files.get('file')
    redaction_type = request.form.get('dataType')

    if not file or not file.filename.endswith('.pdf'):
        return "Only PDF files allowed", 400

    filename = secure_filename(file.filename)
    path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(path)

    # Convert PDF pages to images
    images = convert_from_path(path)
    redacted_pdf = FPDF()

    for i, img in enumerate(images):
        text = pytesseract.image_to_string(img)
        redacted_text = apply_redaction(text, redaction_type)

        blank = Image.new('RGB', img.size, color='white')
        draw = ImageDraw.Draw(blank)
        draw.text((40, 40), redacted_text[:10000], fill='black')

        temp_image_path = f'redacted_page_{i}.jpg'
        blank.save(temp_image_path)

        redacted_pdf.add_page()
        redacted_pdf.image(temp_image_path, x=0, y=0, w=210)
        os.remove(temp_image_path)

    output_filename = f"redacted_{filename}"
    output_path = os.path.join(app.config['UPLOAD_FOLDER'], output_filename)
    redacted_pdf.output(output_path)

    # Copy to static folder to allow download
    final_static_path = os.path.join(app.config['STATIC_UPLOAD_FOLDER'], output_filename)
    shutil.copy(output_path, final_static_path)

    return redirect(url_for('downloads', filename=output_filename))

@app.route('/downloads')
def downloads():
    files = []
    uploads_folder = os.path.join(app.root_path, 'static', 'uploads')
    for filename in os.listdir(uploads_folder):
        if filename.endswith('.pdf') and filename.startswith('redacted_'):
            files.append(filename)
    return render_template('downloads.html', files=files)

# Run the app
if __name__ == "__main__":
    app.run(debug=True)