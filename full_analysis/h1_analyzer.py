import os
import re
import google.generativeai as genai

def analyze_first_house(user_email: str, user_name: str, language: str = 'zh-CN') -> str:
    """
    Reads the 1st House HTML file for the user and generates an AI analysis.
    """
    api_key = os.environ.get('GEMINI_API_KEY')
    if not api_key:
        return "Error: GEMINI_API_KEY not found in environment."

    # Configure Gemini
    genai.configure(api_key=api_key)
    
    # In order to read the house 1 chart result html
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    report_path = os.path.join(base_dir, 'results', user_email, user_name, f'{user_name}_HOUSE 1.html')
    
    html_content = ""
    if os.path.exists(report_path):
        with open(report_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
            html_content = re.sub(r'<img[^>]+>', '', html_content)
    else:
        return f"Error: Could not find House 1 report for user {user_name}. Looked at: {report_path}"

    lang_instruction = f"IMPORTANT: Write the entire analysis strictly in the following language code: {language}."
    prompt = f"""
    You are an expert, premium astrologer interface.
    I will provide you with the HTML structure of a generated Astrolabe report for a user's 1st House.
    Based on the specific data inside this HTML (including Classical Lord Evaluation, Modern Placements, Fixed Star Conjunctions, and Major Aspects), please provide a detailed, deeply insightful, and beautifully written astrological analysis focusing specifically on **House 1 (The Ascendant/Self)**.

    Guidelines:
    - Draw connections using the specific planets occupying House 1, the sign on its cusp, its ruler, and any active aspects.
    - Mention any Fixed Stars conjuncted to points in this house if applicable.
    - {lang_instruction}
    - Format output in beautiful Markdown with clear headers (H3/H4) and bullet points. Do NOT include an H1 or H2 title at the very beginning, just start directly with the house analysis or use H3 for sections.
    
    HTML DATA:
    ======================================
    {html_content}
    """

    try:
        model = genai.GenerativeModel('gemini-2.5-flash')
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"An error occurred during Gemini API call for House 1: {str(e)}"
