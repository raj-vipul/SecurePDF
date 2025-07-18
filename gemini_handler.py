# gemini_handler.py
import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()  # Load your .env file
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

model = genai.GenerativeModel("gemini-2.0-flash")
chat = model.start_chat(history=[])

def get_gemini_response(prompt):
    try:
        response = chat.send_message(prompt, stream=False)
        return response.text
    except Exception as e:
        return f"Error: {str(e)}"
