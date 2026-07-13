import os
import json
import re
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

def get_house_analysis(user_email: str, user_name: str, house_number: int, lang: str = 'en') -> str:
    load_env()
    api_key = os.environ.get('GEMINI_API_KEY')
    if not api_key:
        return "Error: GEMINI_API_KEY not found in .env file."

    # Configure Gemini
    genai.configure(api_key=api_key)
    
    # In order to read the chart result html
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    report_path = os.path.join(base_dir, 'results', user_email, user_name, f'report_{user_name.upper()}.html')
    
    html_content = ""
    if os.path.exists(report_path):
        with open(report_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
            # Remove base64 images to save tokens and prevent 429 errors
            html_content = re.sub(r'<img[^>]+>', '', html_content)
    else:
        return f"Error: Could not find report summary for user {user_name}."

    # Default to English prompt
    prompt = f"""
    You are an expert, premium astrologer interface.
    I will provide you with the HTML structure of a generated Astrolabe report for a user.
    Based on the specific data inside this HTML (including Classical Lord Evaluation, Modern Placements, Fixed Star Conjunctions, and Major Aspects), please provide a detailed, deeply insightful, and beautifully written astrological analysis focusing specifically on **House {house_number}**.

    Guidelines:
    - Draw connections using the specific planets occupying House {house_number}, the sign on its cusp, its ruler, and any active aspects.
    - Mention any Fixed Stars conjuncted to points in this house if applicable.
    - IMPORTANT: Write the entire analysis in English.
    - Format output in beautiful Markdown with headers and bullet points.
    HTML DATA:
    ======================================
    {html_content}
    """

    if lang == 'en':
        prompt = f"""
        You are an expert, premium astrologer interface.
        I will provide you with the HTML structure of a generated Astrolabe report for a user.
        Based on the specific data inside this HTML (including Classical Lord Evaluation, Modern Placements, Fixed Star Conjunctions, and Major Aspects), please provide a detailed, deeply insightful, and beautifully written astrological analysis focusing specifically on **House {house_number}**.

        Guidelines:
        - Draw connections using the specific planets occupying House {house_number}, the sign on its cusp, its ruler, and any active aspects.
        - Mention any Fixed Stars conjuncted to points in this house if applicable.
        - IMPORTANT: Write the entire analysis in English.
        - Format output in beautiful Markdown with headers and bullet points.
        HTML DATA:
        ======================================
        {html_content}
        """

    if lang == 'fr':
        prompt = f"""
        Vous êtes une interface d'astrologie experte et haut de gamme.
        Je vais vous fournir la structure HTML d'un rapport d'Astrolabe généré pour un utilisateur.
        Sur la base des données spécifiques à l'intérieur de ce HTML (y compris Classical Lord Evaluation, Modern Placements, Fixed Star Conjunctions, et Major Aspects), veuillez fournir une analyse astrologique détaillée, profondément perspicace et magnifiquement écrite, en vous concentrant spécifiquement sur la **Maison {house_number}**.

        Directives :
        - Établissez des liens en utilisant les planètes spécifiques occupant la Maison {house_number}, le signe sur sa cuspide, son maître et tous les aspects actifs.
        - Mentionnez toutes les étoiles fixes conjointes à des points de cette maison, le cas échéant.
        - IMPORTANT : Rédigez l'intégralité de l'analyse en français.
        - Formatez la sortie dans un format Markdown soigné avec des en-têtes et des listes à puces.
        DONNÉES HTML :
        ======================================
        {html_content}
        """

    try:
        model = genai.GenerativeModel(os.environ.get('AI_MODEL', 'gemini-2.5-flash'))
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"An error occurred during Gemini API call: {str(e)}"
