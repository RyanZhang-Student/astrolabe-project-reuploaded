import os
import re
import traceback
import markdown
import google.generativeai as genai
from flask import jsonify

def generate_full_report(user_email, data, results_dir):
    """
    Generates a premium HTML report page containing the user's chart image,
    birth date/time, location, and an AI-generated astrological analysis.
    """
    chart_img_data = data.get('chart_img')
    birth_date = data.get('birth_date', '')
    birth_time = data.get('birth_time', '')
    location = data.get('location', '')
    language = data.get('language', 'zh-CN')
    user_name = data.get('name', 'guest')
    
    email_folder = os.path.join(results_dir, user_email)
    if not os.path.exists(email_folder):
        os.makedirs(email_folder)
        
    html_filename = f"full_report_{user_email}.html"
    html_filepath = os.path.join(email_folder, html_filename)
    
    if os.path.exists(html_filepath):
        report_url = f"/results/{user_email}/{html_filename}"
        return jsonify({
            'status': 'success',
            'report_url': report_url
        })
        
    # Generate AI Content
    ai_html_content = ""
    try:
        api_key = os.environ.get('GEMINI_API_KEY')
        if not api_key:
            ai_html_content = "<p style='color: red;'>Error: GEMINI_API_KEY not found in .env file.</p>"
        else:
            genai.configure(api_key=api_key)
            
            # Read base report HTML for context
            report_path = os.path.join(email_folder, user_name, f'report_{user_name.upper()}.html')
            base_html_content = ""
            if os.path.exists(report_path):
                with open(report_path, 'r', encoding='utf-8') as f:
                    base_html_content = f.read()
                    base_html_content = re.sub(r'<img[^>]+>', '', base_html_content)
            
            lang_instruction = f"IMPORTANT: Write the ENTIRE analysis strictly in the following language code: {language}. Do not use any other language. Make sure the headers correspond exactly to the requested sections in {language}."
            
            prompt = f"""
            You are an expert, premium astrologer interface.
            I will provide you with the HTML structure of a generated Astrolabe report for a user.
            Based on the specific data inside this HTML (including Classical Lord Evaluation, Modern Placements, Fixed Star Conjunctions, and Major Aspects), please provide a detailed, deeply insightful, and beautifully written astrological analysis.
            
            Please cover the following EXACT 5 sections in your response, providing comprehensive details for each:
            1. 人生总体战略蓝图 (Overall Life Strategy Blueprint): Analyze the distribution of elements, dominant planets, and major chart patterns from a macro perspective to set the core archetype.
            2. 核心天赋深度解析 (Core Talent Depth Analysis): Extract the core competitive advantages and talents.
            3. 事业赛道与商业建议 (Career Path & Business Advice): Based on the talents above, directly provide specific career field recommendations and actionable business strategies.
            4. 核心恒星深度解析 (Core Fixed Star Depth Analysis): Select a few of the most influential fixed star conjunctions in the chart, and provide a deep interpretation of their trajectory and energy levels one by one.
            5. 未来十年核心建议 (Core Advice for the Next Decade): Translate the macro analysis into a specific action guide, listing strategic focuses, action steps, and the underlying reasons for the next 10 years.

            Guidelines:
            - {lang_instruction}
            - Base your analysis purely on the provided HTML data. If the data is empty, invent a generic reading.
            - Format output in beautiful Markdown with clear headers (H2/H3) and bullet points.
            
            HTML DATA:
            ======================================
            {base_html_content}
            """
            
            model = genai.GenerativeModel('gemini-2.5-flash')
            response = model.generate_content(prompt)
            markdown_text = response.text
            
            # Convert Markdown to HTML
            ai_html_content = markdown.markdown(markdown_text, extensions=['extra', 'nl2br'])
            
    except Exception as e:
        traceback.print_exc()
        ai_html_content = f"<p style='color: red;'>An error occurred during AI generation: {str(e)}</p>"

    # HTML Template
    html_template = f"""<!DOCTYPE html>
<html lang="{language}">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Full Astrological Analysis Report</title>
    <style>
        body {{
            background-color: #0d0b14;
            color: #e6c98b;
            font-family: 'Inter', 'Cormorant Garamond', sans-serif;
            margin: 0;
            padding: 0;
            display: flex;
            flex-direction: column;
            align-items: center;
            min-height: 100vh;
            box-sizing: border-box;
            position: relative;
        }}
        .back-btn {{
            position: absolute;
            top: 2rem;
            left: 2rem;
            width: 3.2rem;
            height: 3.2rem;
            border-radius: 50%;
            background-color: #0d0b14;
            border: 1px solid rgba(230, 201, 139, 0.4);
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.4);
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
            transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
            z-index: 100;
            outline: none;
        }}
        .back-btn:hover {{
            transform: scale(1.1);
            border-color: rgba(255, 204, 0, 0.8);
            box-shadow: 0 6px 20px rgba(255, 204, 0, 0.3);
        }}
        .back-btn svg {{
            width: 1.5rem;
            height: 1.5rem;
            fill: #ffcc00;
        }}
        .report-container {{
            max-width: 800px;
            width: 100%;
            padding: 4rem 2rem;
            display: flex;
            flex-direction: column;
            align-items: center;
        }}
        .chart-img {{
            max-width: 600px;
            width: 100%;
            height: auto;
            border-radius: 50%;
            box-shadow: 0 0 30px rgba(230, 201, 139, 0.2);
            margin-bottom: 2.5rem;
            transition: transform 0.5s ease;
        }}
        .chart-img:hover {{
            transform: scale(1.02);
        }}
        .birth-info-title {{
            font-size: 1.8rem;
            font-weight: bold;
            margin-bottom: 0.5rem;
            letter-spacing: 2px;
            color: #e6c98b;
            font-family: 'Cormorant Garamond', serif;
            text-align: center;
        }}
        .birth-info-sub {{
            font-size: 1.2rem;
            color: #a0aec0;
            letter-spacing: 1px;
            margin-bottom: 4rem;
            text-align: center;
        }}
        
        /* AI Content Styles */
        .ai-content {{
            width: 100%;
            text-align: left;
            line-height: 1.8;
            font-size: 1.1rem;
            color: #fdfbf7;
        }}
        .ai-content h2 {{
            color: #e6c98b;
            font-family: 'Cormorant Garamond', serif;
            font-size: 2rem;
            margin-top: 3rem;
            margin-bottom: 1.5rem;
            border-bottom: 1px solid rgba(230, 201, 139, 0.2);
            padding-bottom: 0.5rem;
        }}
        .ai-content h3 {{
            color: #b39b6b;
            font-size: 1.4rem;
            margin-top: 2rem;
            margin-bottom: 1rem;
        }}
        .ai-content p {{
            margin-bottom: 1.5rem;
        }}
        .ai-content ul {{
            margin-bottom: 1.5rem;
            padding-left: 2rem;
        }}
        .ai-content li {{
            margin-bottom: 0.5rem;
        }}
        .ai-content strong {{
            color: #e6c98b;
        }}
    </style>
</head>
<body>
    <button class="back-btn" onclick="if(window.opener){{window.close();}}else{{window.history.back();}}" aria-label="Back">
        <svg viewBox="0 0 24 24">
            <path d="M15.41 7.41L14 6l-6 6 6 6 1.41-1.41L10.83 12z"/>
        </svg>
    </button>
    <div class="report-container">
        <img class="chart-img" src="{chart_img_data}" alt="Natal Chart">
        <div class="birth-info-title">{birth_date} {birth_time}</div>
        <div class="birth-info-sub">{location}</div>
        
        <div class="ai-content">
            {ai_html_content}
        </div>
    </div>
</body>
</html>"""

    try:
        with open(html_filepath, 'w', encoding='utf-8') as f:
            f.write(html_template)
    except Exception as e:
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500
        
    report_url = f"/results/{user_email}/{html_filename}"
    return jsonify({
        'status': 'success',
        'report_url': report_url
    })
