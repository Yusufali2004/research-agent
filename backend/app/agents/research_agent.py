import os
import json
import re
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

IEEE_TEMPLATE = """
PAPER TITLE (Title Case, centered, bold, 24pt Times New Roman)

Author Name — dept. name of organization, name of organization, City, Country, email@domain.com

Abstract — Single paragraph, 150-250 words. Start with "Abstract—". No symbols, special characters, footnotes or math. Summarize: problem, method, key results, conclusion. Do NOT use bullet points.

Keywords — 4-6 lowercase keywords separated by commas.

I. INTRODUCTION (Heading 1, uppercase, bold)
Body text in Times New Roman 10pt, two-column layout, justified alignment.
Paragraph 1: Problem statement and motivation.
Paragraph 2: Existing approaches and limitations.
Paragraph 3: Proposed approach and contributions.
Paragraph 4: Paper organization ("Section II describes...")

II. METHODOLOGY (Heading 1)
A. Subsection Heading (Title Case, italic if needed)
Detailed technical approach. Passive voice. Formal academic tone.

III. RESULTS AND DISCUSSION (Heading 1)
Present findings and metrics from the content only.
Do NOT invent numbers. Discuss implications.

IV. CONCLUSION (Heading 1)
Paragraph 1: Summary of work and achievements.
Paragraph 2: Limitations.
Paragraph 3: Future work directions.

ACKNOWLEDGMENT (unnumbered heading)

REFERENCES (unnumbered heading)
[1] A. Author, "Title of paper," Journal Name, vol. X, no. X, pp. XX-XX, Year.
"""

def extract_json(text: str) -> dict:
    # Remove markdown code blocks
    text = text.replace("```json", "").replace("```", "").strip()
    
    # Try direct parse first
    try:
        return json.loads(text)
    except:
        pass
    
    # Find JSON object using regex
    match = re.search(r'\{[\s\S]*\}', text)
    if match:
        try:
            return json.loads(match.group())
        except:
            pass
    
    # Last resort — return error structure
    return {
        "Title": "Parse Error",
        "Authors": "",
        "Abstract": "Failed to parse AI response. Please try again.",
        "Keywords": "",
        "Introduction": text[:500],
        "Methodology": "",
        "Results": "",
        "Conclusion": "",
        "Acknowledgment": "",
        "References": ""
    }

def generate_full_paper(content: str, template: str) -> dict:
    prompt = f"""You are a strict IEEE conference paper formatter.

YOUR ONLY JOB: Take the raw research content below and restructure it into a properly formatted IEEE conference paper.

STRICT RULES:
1. Use ONLY information from the provided content. Do NOT add external knowledge or invented data.
2. Do NOT change meaning, results, or claims from the original content.
3. If information for a section is missing, write: "[Insufficient data in source content]"
4. Do NOT use bullet points anywhere.
5. Formal academic English. Third person. Passive voice preferred.
6. Abstract must start with "Abstract—" and be 150-250 words.
7. Section headings use Roman numerals: I. INTRODUCTION, II. METHODOLOGY, etc.
8. References follow IEEE format: [1] A. Author, "Title," Journal, vol., pp., Year.
9. Do NOT include any commentary or explanation outside the JSON.

IEEE STRUCTURE:
{IEEE_TEMPLATE}

RAW RESEARCH CONTENT (use ONLY this):
{content}

YOU MUST return ONLY a valid JSON object. No text before or after. No markdown. No explanation.
Exact format:
{{
    "Title": "...",
    "Authors": "Author Name, Department, Institution, City, Country, email@domain.com",
    "Abstract": "Abstract— ...",
    "Keywords": "keyword1, keyword2, keyword3",
    "Introduction": "I. INTRODUCTION\\n\\n...",
    "Methodology": "II. METHODOLOGY\\n\\n...",
    "Results": "III. RESULTS AND DISCUSSION\\n\\n...",
    "Conclusion": "IV. CONCLUSION\\n\\n...",
    "Acknowledgment": "ACKNOWLEDGMENT\\n\\n...",
    "References": "REFERENCES\\n\\n[1] ..."
}}"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "system",
                "content": "You are an IEEE paper formatter. You respond ONLY with valid JSON. Never add text outside the JSON object."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.2,
    )

    text = response.choices[0].message.content.strip()
    return extract_json(text)