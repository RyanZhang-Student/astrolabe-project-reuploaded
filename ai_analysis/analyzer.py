import os
import json
from pathlib import Path
import google.generativeai as genai

# Try loading from pure python if python-dotenv isn't installed
def load_env():
    env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
    if os.path.exists(env_path):
        with open(env_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    key, val = line.split('=', 1)
                    os.environ[key.strip()] = val.strip().strip("'\"")

def get_house_analysis(user_name: str, house_number: int) -> str:
    load_env()
    api_key = os.environ.get('GEMINI_API_KEY')
    if not api_key:
        return "Error: GEMINI_API_KEY not found in .env file."

    # Configure Gemini
    genai.configure(api_key=api_key)
    
    # In order to read the chart result html
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    report_path = os.path.join(base_dir, 'results', f'report_{user_name.upper()}.html')
    
    html_content = ""
    if os.path.exists(report_path):
        with open(report_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
    else:
        return f"Error: Could not find report summary for user {user_name}."

    prompt = f"""
    You are an expert, premium astrologer interface.
    I will provide you with the HTML structure of a generated Astrolabe report for a user.
    Based on the specific data inside this HTML (including Classical Lord Evaluation, Modern Placements, Fixed Star Conjunctions, and Major Aspects), please provide a detailed, deeply insightful, and beautifully written astrological analysis focusing specifically on **House {house_number}**.

    Guidelines:
    - Draw connections using the specific planets occupying House {house_number}, the sign on its cusp, its ruler, and any active aspects.
    - Mention any Fixed Stars conjuncted to points in this house if applicable.
    - Write the analysis in the language of the user's interface (Chinese preferably, or English if preferred, given the "Analyze" button might be implied in Chinese based on instructions). Please output the response in Chinese as requested by user context ("一到十二的方块... 分析键").
    - Format output in beautiful Markdown with headers and bullet points.
    - respond in english
    HTML DATA:
    ======================================
    {html_content[:30000]} # Trim to fit in standard contexts just in case, though Gemini handles large contexts easily.
    """

    try:
        model = genai.GenerativeModel('gemini-2.5-flash')
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"An error occurred during Gemini API call: {str(e)}"
