import google.generativeai as genai
from dotenv import load_dotenv  
import os

load_dotenv()  


genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
model = genai.GenerativeModel("gemini-2.5-flash")
response = model.generate_content("Éxplique em 3 frases o que é aprendizado de máquina.") 
print(response.text)




 llm = LLM(
            model ="ollama/gemma3:270m",
            base_url="http://localhost:11434",
            temperature=0.7,
        )
model = llm
response model.
