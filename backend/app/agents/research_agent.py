import os
import json
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def generate_full_paper(content: str, template: str) -> dict:
    prompt = f"""
You are an expert academic research paper writer.
Based on the following raw research content, generate a complete research paper 
following {template} format. DO NOT add any additional information or semmantic changes.
Your job is to strictly Format the data accuratly 

Raw Content:
{content}

Generate all sections in this exact JSON format, return ONLY the JSON nothing else:
{{
    "Abstract": "...",
    "Introduction": "...",
    "Methodology": "...",
    "Results": "...",
    "Conclusion": "..."
}}

Rules:
- Be formal and academic in tone
- Follow {template} formatting standards
- Each section must be detailed and comprehensive
"""
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
    )

    text = response.choices[0].message.content.strip()
    text = text.replace("```json", "").replace("```", "").strip()
    return json.loads(text)