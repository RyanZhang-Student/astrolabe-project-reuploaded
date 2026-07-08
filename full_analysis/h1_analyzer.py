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

    Do not say anything extra like "here is the report" or "this yeah。report suggests something". Just provide the analysis.
    Do not give score numbers and orb degrees.

    Please cover the following EXACT 6 sections in your response, providing comprehensive details for each:
    - Concept Introduction: Explains the core definition and practical significance of this house in astrology or in the relevant area of life.
    - Foundation & Blueprint: Analyzes the zodiac sign ruling the cusp of this house, interpreting the innate traits, image, and potential challenges it brings to that area of life.
    - Core Drivers: Ruler Alignment: Identifies the zodiac sign, house, and retrograde status of the ruling planet (house ruler) for this house, and provides a detailed breakdown of the network of aspects formed between this ruling planet and the Sun, other core celestial bodies, and virtual points.
    - Energy Matrix: Planetary Distribution and Aspects (Energy Matrix): Analyzes the planets and asteroids directly located within the house, the energy at the cusp, and their interactive aspects with other celestial bodies.
    - Deep Insights: Hidden Influences: Explore conjunctions with fixed stars (fixed stars) within the house or near the ruling planet to reveal more hidden, deeper destinies or special empowerments.
    - Dynamic Analysis: Organically integrate all the above elements (zodiac signs, ruling planet, inner planets, fixed stars) to distill an overall energetic picture of this domain.
    - House Qualitative Summary: Provides a concise, final qualitative assessment of the house’s core energy, strengths, and risks.
    - Core Action Strategy Recommendations: Lists several (typically 8–10) highly targeted, well-organized, and actionable recommendations, fully translating the analysis into practical application.
    
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
