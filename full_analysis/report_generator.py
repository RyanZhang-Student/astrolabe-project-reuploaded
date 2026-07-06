import os
import traceback
from flask import jsonify

def generate_full_report(user_email, data, results_dir):
    """
    Generates a premium HTML report page containing the user's chart image,
    birth date/time, and location, saved in the user's specific folder.
    """
    chart_img_data = data.get('chart_img')
    birth_date = data.get('birth_date', '')
    birth_time = data.get('birth_time', '')
    location = data.get('location', '')
    
    email_folder = os.path.join(results_dir, user_email)
    if not os.path.exists(email_folder):
        os.makedirs(email_folder)
        
    html_filename = f"full_report_{user_email}.html"
    html_filepath = os.path.join(email_folder, html_filename)
    
    html_template = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Full Astrological Analysis Report</title>
    <style>
        body {{
            background-color: #0d0b14;
            color: #e6c98b;
            font-family: 'Cormorant Garamond', 'Inter', sans-serif;
            margin: 0;
            padding: 0;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            min-height: 100vh;
            text-align: center;
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
            padding: 2rem;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
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
        }}
        .birth-info-sub {{
            font-size: 1.2rem;
            color: #a0aec0;
            letter-spacing: 1px;
        }}
    </style>
</head>
<body>
    <button class="back-btn" onclick="if(window.opener){{window.close();}}else{{window.history.back();}}" aria-label="返回">
        <svg viewBox="0 0 24 24">
            <path d="M15.41 7.41L14 6l-6 6 6 6 1.41-1.41L10.83 12z"/>
        </svg>
    </button>
    <div class="report-container">
        <img class="chart-img" src="{chart_img_data}" alt="Natal Chart">
        <div class="birth-info-title">{birth_date} {birth_time}</div>
        <div class="birth-info-sub">{location}</div>
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
