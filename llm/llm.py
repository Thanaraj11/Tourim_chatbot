import os
import google.generativeai as genai
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

class LLM:
    def __init__(self, provider="gemini"):
        self.provider = provider
        
        if provider == "gemini":
            gemini_api_key = os.getenv("GEMINI_API_KEY")
            if not gemini_api_key:
                raise ValueError("GEMINI_API_KEY is not set")
            genai.configure(api_key=gemini_api_key)
            model_name = os.getenv("GEMINI_MODEL", "models/gemini-2.5-flash")
            self.model = genai.GenerativeModel(model_name)
        elif provider == "openai":
            openai_api_key = os.getenv("OPENAI_API_KEY")
            if not openai_api_key:
                raise ValueError("OPENAI_API_KEY is not set")
            self.client = OpenAI(api_key=openai_api_key)
            self.model_name = "gpt-3.5-turbo"
    
    def generate(self, prompt: str) -> str:
        if self.provider == "gemini":
            response = self.model.generate_content(prompt)
            return response.text.strip()
        
        elif self.provider == "openai":
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3
            )
            return response.choices[0].message.content.strip()