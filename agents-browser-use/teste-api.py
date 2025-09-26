import google.generativeai as genai
from dotenv import load_dotenv  
load_dotenv()  
import os

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
model = genai.GenerativeModel("gemini-2.5-flash")
response = model.generate_content("Éxplique em 3 frases o que é aprendizado de máquina.") 
print(response.text)