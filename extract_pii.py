import os
import json
from dotenv import load_dotenv
import google.generativeai as genai

# Load .env where GOOGLE_API_KEY is stored
load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Gemini model setup
model = genai.GenerativeModel("gemini-2.0-flash")
chat = model.start_chat(history=[])

# Example PDF-extracted text
pdf_text = """
Hi, I'm Alice Johnson. You can contact me at alice.johnson@example.com or +1-555-1234.
I live at 123 Maple Street, Springfield. My colleague Bob Smith can also be reached at bob.smith@company.com.
"""

# Gemini prompt to extract structured PII
prompt = f"""
Extract all personally identifiable information (PII) from the following text. 
Return the result as a JSON object with these keys: name, email, phone_number, address, and others if applicable.

Each value should be a list of strings.

Text:
\"\"\"
{pdf_text}
\"\"\"
"""

# Get Gemini response
response = chat.send_message(prompt)
raw_output = response.text.strip()

# Attempt to parse as JSON (Gemini sometimes formats with triple backticks or code blocks)
try:
    if raw_output.startswith("```json"):
        raw_output = raw_output[7:-3].strip()
    pii_data = json.loads(raw_output)
except json.JSONDecodeError:
    print("⚠️ Could not parse Gemini output as JSON:")
    print(raw_output)
    exit(1)

# Save to file
with open("extracted_pii.json", "w") as f:
    json.dump(pii_data, f, indent=2)

print("✅ PII successfully saved to extracted_pii.json")
