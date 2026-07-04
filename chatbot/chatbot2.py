import os
import json
import re
import google.generativeai as genai


def load_env():
    env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
    if os.path.exists(env_path):
        with open(env_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    key, val = line.split('=', 1)
                    os.environ[key.strip()] = val.strip().strip("'\"")


def get_chat_response(user_email: str, user_name: str, user_message: str, chat_history: list) -> str:
    """
    Send a chat message to Gemini with the user's astrological chart as context.
    chat_history is a list of dicts: [{'role': 'user'|'assistant', 'content': '...'}, ...]
    """
    load_env()
    api_key = os.environ.get('GEMINI_API_KEY')
    if not api_key:
        return "Error: GEMINI_API_KEY not found in .env file."

    genai.configure(api_key=api_key)

    # Load the user's chart report HTML for context
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    report_path = os.path.join(base_dir, 'results', user_email, user_name, f'report_{user_name.upper()}.html')

    html_content = ""
    if os.path.exists(report_path):
        with open(report_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
            # Remove base64 images to save tokens and prevent 429 errors
            html_content = re.sub(r'<img[^>]+>', '', html_content)
    else:
        return f"Error: Could not find report for user {user_name}. Please generate a chart first."

    # Build the system prompt with chart context
    system_prompt = f"""You are "Aurelius", a Top-tier oracle for 'Wealth and Career', expert in revealing financial potential and business landscapes based on astrological data.
You have access to the user's complete astrological chart data below.
Use this data to answer their questions with specific, personalized insights.

Guidelines:
- Core Logic & Flow: For any house or life topic analyzed, strictly follow this deductive chain: Identify the sign on the house cusp -> locate its ruling planet (Lord of the House) -> evaluate the house it occupies (flying house) -> analyze only major aspects (conjunction, opposition, square, trine, sextile) affecting it.
- Strict Brevity (Anti-Wall of Text): Do NOT generate long-winded essays or overwhelming explanations. Limit the entire response to exactly 2 concise, impactful paragraphs (similar to a standard professional consultation snippet). Keep sentences clear and direct.
- Zero Raw Numbers: Never expose internal calculation numbers to the user. Do NOT include geometric orbs (e.g., 0.44° orb), exact planetary degrees/minutes (e.g., 11°5'), or numerical strength scores (e.g., -9.2). Instead, translate these states into qualitative terms (e.g., use words like "very tight aspect," "debilitated/in fall," or "combust" to explain the condition).
- Format & Language: Use bolding for critical astrological variables (planets, houses, aspects) to make the text immediately scannable. Respond in the same language the user writes in (use standard Chinese terminology if they inquire in Chinese).
- Word counts:  keep it under 200 words, but do not make it less than 100 words unless you can not explain the user's question in. do not display the word count at the end of the response because the user would be thrown off by the extra text.
- If the user asks something unrelated to astrology, gently steer back to their chart.

USER'S CHART DATA:
======================================
{html_content}
======================================
"""

    # Build conversation for Gemini
    history = []
    for msg in chat_history:
        role = 'user' if msg['role'] == 'user' else 'model'
        history.append({'role': role, 'parts': [msg['content']]})

    try:
        model = genai.GenerativeModel(
            'gemini-2.5-flash',
            system_instruction=system_prompt
        )
        chat = model.start_chat(history=history)
        response = chat.send_message(user_message)
        return response.text
    except Exception as e:
        error_str = str(e)
        print(f"Chatbot API error: {error_str}", flush=True)
        if '429' in error_str or 'quota' in error_str.lower() or 'rate limit' in error_str.lower() or 'depleted' in error_str.lower():
            return "__SERVICE_UNAVAILABLE__"
        return "__SERVICE_ERROR__"
