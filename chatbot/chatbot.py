import os
import json
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
    else:
        return f"Error: Could not find report for user {user_name}. Please generate a chart first."

    # Build the system prompt with chart context
    system_prompt = f"""You are "Astrolabe Advisor", a deeply knowledgeable and warm astrology consultant.
You have access to the user's complete astrological chart data below.
Use this data to answer their questions with specific, personalized insights.

Guidelines:
- Be warm, insightful and specific — reference actual placements from their chart.
- When discussing houses, planets, aspects, or fixed stars, cite the exact data.
- Keep responses conversational but substantive (2-4 paragraphs typically).
- You may respond in the same language the user writes in.
- Format important terms in **bold** for emphasis.
- If the user asks something unrelated to astrology, gently steer back to their chart.

USER'S CHART DATA:
======================================
{html_content[:25000]}
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
        return f"An error occurred: {str(e)}"
