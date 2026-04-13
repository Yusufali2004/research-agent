import os
import json
import re
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def clean_paper_data(paper: dict) -> dict:
    """
    Refined correction logic to ensure strict IEEE compliance and clean UI output.
    """
    fixes = {
        "Introduction": [r"^1\.\s*INTRODUCTION", "I. INTRODUCTION"],
        "Methodology": [r"^2\.\s*METHODOLOGY", "II. METHODOLOGY"],
        "Results": [r"^3\.\s*RESULTS AND DISCUSSION", "III. RESULTS AND DISCUSSION"],
        "Conclusion": [r"^4\.\s*CONCLUSION", "IV. CONCLUSION"]
    }
    for key, (pattern, replacement) in fixes.items():
        if paper.get(key):
            paper[key] = re.sub(pattern, replacement, paper[key], flags=re.IGNORECASE)
            
    if paper.get("Abstract"):
        paper["Abstract"] = re.sub(r"^Abstract[-\s:]*", "Abstract—", paper["Abstract"], flags=re.IGNORECASE)
        
    if paper.get("Keywords"):
        val = paper["Keywords"]
        val = re.sub(r"^(Keywords|Index Terms|Keywords Index Terms)[-\s:]*", "", val, flags=re.IGNORECASE)
        if "Insufficient data" in val or not val:
            val = "Research, Analysis, System Design, Implementation"
        paper["Keywords"] = val
        
    if not paper.get("Authors") or "Insufficient data" in paper.get("Authors", ""):
        paper["Authors"] = "Team Algo Ninjas — ResearchMate AI, India"
        
    for key in paper:
        if isinstance(paper[key], str):
            # Remove any AI 'apologies' or meta-talk that escaped the JSON
            paper[key] = paper[key].replace("[Insufficient data in source content]", "").strip()
            
    return paper

def extract_json(text: str) -> dict:
    text = text.replace("```json", "").replace("```", "").strip()
    parsed_data = None
    try:
        parsed_data = json.loads(text)
    except:
        match = re.search(r'\{[\s\S]*\}', text)
        if match:
            try:
                parsed_data = json.loads(match.group())
            except:
                pass
                
    if not parsed_data:
        parsed_data = {
            "Title": "Research Paper Generation Failed",
            "Authors": "Error — System",
            "Abstract": "Abstract—Data could not be parsed.",
            "Keywords": "error, parsing",
            "Introduction": "I. INTRODUCTION\n\nFailed to parse response.",
            "Methodology": "II. METHODOLOGY\n\nCheck source content.",
            "Results": "III. RESULTS AND DISCUSSION\n\nCheck source content.",
            "Conclusion": "IV. CONCLUSION\n\nCheck source content.",
            "Acknowledgment": "ACKNOWLEDGMENT\n\nN/A",
            "References": "REFERENCES\n\n[1] Source content error."
        }
    return clean_paper_data(parsed_data)

def generate_full_paper(content: str, template: str) -> dict:
    # UPDATED PROMPT: Focused on depth, zero-hallucination, and exhaustive extraction
    prompt = f"""You are a Senior Technical Editor for IEEE Transactions. 

TASK: Convert the provided RAW RESEARCH CONTENT into a high-density, professional IEEE Conference Paper.

STRICT OPERATING RULES:
1. ZERO EXTERNAL KNOWLEDGE: Do not add information from the internet. Use ONLY the provided content.
2. EXHAUSTIVE EXTRACTION: If the user provides 10 details, use all 10. Do not summarize or shorten. 
3. EXPAND ON LOGIC: Explain the implications of the data provided. Use phrases like "This indicates...", "The implementation suggests...", "Consequently, the architecture..." to provide depth without adding new facts.
4. NO BULLET POINTS: Convert all lists into descriptive paragraphs.
5. FORMAL TONE: Use academic, passive voice where appropriate.
6. HEADINGS: Use Roman numerals (I. INTRODUCTION, II. METHODOLOGY, etc.).
7. FIGURES/TABLES: Preserve [IMAGE: filename.png] tags and Markdown tables exactly.

STRUCTURE:
- Abstract: Start with "Abstract—". A single, dense paragraph.
- Index Terms: 4-6 keywords.
- Methodology: Detailed technical steps found in content.
- Results: Focus on any metrics or observations provided.

RAW RESEARCH CONTENT:
{content}

RESPONSE FORMAT: Respond ONLY with a valid JSON object.
{{
    "Title": "Paper Title",
    "Authors": "Author — Affiliation, City, Country",
    "Abstract": "...",
    "Keywords": "...",
    "Introduction": "...",
    "Methodology": "...",
    "Results": "...",
    "Conclusion": "...",
    "Acknowledgment": "...",
    "References": "..."
}}"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "system",
                "content": "You are a specialized IEEE formatter. You only output pure JSON. You strictly adhere to provided source text without adding external data."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.1, # Lowered for higher precision/less hallucination
        max_tokens=4096,
    )

    text = response.choices[0].message.content.strip()
    return extract_json(text)