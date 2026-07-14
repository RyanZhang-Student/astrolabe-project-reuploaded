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
    user_name = data.get('name', 'guest').upper()
    
    user_folder = os.path.join(results_dir, user_email, user_name)
    if not os.path.exists(user_folder):
        os.makedirs(user_folder)
        
    html_filename = f"full_report_{user_email}.html"
    html_filepath = os.path.join(user_folder, html_filename)
    
    if os.path.exists(html_filepath):
        report_url = f"/results/{user_email}/{user_name}/{html_filename}"
        return jsonify({
            'status': 'success',
            'report_url': report_url
        })
        
    # Generate AI Content
    ai_html_content = ""
    try:
        from dotenv import load_dotenv
        load_dotenv(override=True)
        api_key = os.environ.get('GEMINI_API_KEY')
        if not api_key:
            ai_html_content = "<p style='color: red;'>Error: GEMINI_API_KEY not found in .env file.</p>"
        else:
            genai.configure(api_key=api_key)
            
            # Read base report HTML for context
            report_path = os.path.join(user_folder, f'report_{user_name}.html')
            base_html_content = ""
            if os.path.exists(report_path):
                with open(report_path, 'r', encoding='utf-8') as f:
                    base_html_content = f.read()
                    base_html_content = re.sub(r'<img[^>]+>', '', base_html_content)
            
            # Default to English prompt
            prompt = f"""
            You are an expert, premium astrologer interface.
            I will provide you with the HTML structure of a generated Astrolabe report for a user.
            Based on the specific data inside this HTML (including Classical Lord Evaluation, Modern Placements, Fixed Star Conjunctions, and Major Aspects), please provide a detailed, deeply insightful, and beautifully written astrological analysis.
            
            Do not say anything extra like "here is the report" or "this report suggests something". Just provide the analysis.
            Please cover the following EXACT 5 sections in your response, providing comprehensive details for each:
            1. Overall Life Strategy Blueprint: Analyze the distribution of elements, dominant planets, and major chart patterns from a macro perspective to set the core archetype.
            2. Core Talent Depth Analysis: Extract the core competitive advantages and talents.
            3. Career Path & Business Advice: Based on the talents above, directly provide specific career field recommendations and actionable business strategies.
            4. Core Fixed Star Depth Analysis: Select a few of the most influential fixed star conjunctions in the chart, and provide a deep interpretation of their trajectory and energy levels one by one.
            5. Core Advice for the Next Decade: Translate the macro analysis into a specific action guide, listing strategic focuses, action steps, and the underlying reasons for the next 10 years.

            Guidelines:
            - IMPORTANT: Write the ENTIRE analysis strictly in English. Do not use any other language. Make sure the headers correspond exactly to the requested sections in English.
            - Base your analysis purely on the provided HTML data. If the data is empty, invent a generic reading.
            - Format output in beautiful Markdown with clear headers (H2/H3) and bullet points.
            
            HTML DATA:
            ======================================
            {base_html_content}
            """

            if language == 'fr':
                prompt = f"""
                Vous êtes une interface d'astrologie experte et haut de gamme.
                Je vais vous fournir la structure HTML d'un rapport d'Astrolabe généré pour un utilisateur.
                Sur la base des données spécifiques à l'intérieur de ce HTML (y compris Classical Lord Evaluation, Modern Placements, Fixed Star Conjunctions, et Major Aspects), veuillez fournir une analyse astrologique détaillée, profondément perspicace et magnifiquement écrite.
                
                Ne dites rien de superflu comme « voici le rapport » ou « ce rapport suggère ». Fournissez uniquement l'analyse.
                Veuillez aborder EXACTEMENT les 5 sections suivantes dans votre réponse, en fournissant des détails complets pour chacune :
                1. Overall Life Strategy Blueprint : Analysez la répartition des éléments, les planètes dominantes et les configurations majeures du thème d'un point de vue macro pour définir l'archétype central.
                2. Core Talent Depth Analysis : Extrayez les avantages concurrentiels et les talents fondamentaux.
                3. Career Path & Business Advice : Sur la base des talents ci-dessus, proposez directement des recommandations de domaines de carrière spécifiques et des stratégies commerciales applicables.
                4. Core Fixed Star Depth Analysis : Sélectionnez quelques-unes des conjonctions d'étoiles fixes les plus influentes du thème, et fournissez une interprétation approfondie de leur trajectoire et de leurs niveaux d'énergie une par une.
                5. Core Advice for the Next Decade : Traduisez l'analyse macro en un guide d'action spécifique, énumérant les axes stratégiques, les étapes d'action et les raisons sous-jacentes pour les 10 prochaines années.

                Directives :
                - IMPORTANT : Rédigez l'intégralité de l'analyse strictement en français. N'utilisez aucune autre langue. Veillez à ce que les en-têtes correspondent exactement aux sections demandées en français.
                - Basez votre analyse uniquement sur les données HTML fournies. Si les données sont vides, inventez une lecture générique.
                - Formatez la sortie dans un format Markdown soigné avec des en-têtes clairs (H2/H3) et des listes à puces.
                
                DONNÉES HTML :
                ======================================
                {base_html_content}
                """

            if language == 'en':
                prompt = f"""
                You are an expert, premium astrologer interface.
                I will provide you with the HTML structure of a generated Astrolabe report for a user.
                Based on the specific data inside this HTML (including Classical Lord Evaluation, Modern Placements, Fixed Star Conjunctions, and Major Aspects), please provide a detailed, deeply insightful, and beautifully written astrological analysis.
                
                Do not say anything extra like "here is the report" or "this report suggests something". Just provide the analysis.
                Please cover the following EXACT 5 sections in your response, providing comprehensive details for each:
                1. Overall Life Strategy Blueprint: Analyze the distribution of elements, dominant planets, and major chart patterns from a macro perspective to set the core archetype.
                2. Core Talent Depth Analysis: Extract the core competitive advantages and talents.
                3. Career Path & Business Advice: Based on the talents above, directly provide specific career field recommendations and actionable business strategies.
                4. Core Fixed Star Depth Analysis: Select a few of the most influential fixed star conjunctions in the chart, and provide a deep interpretation of their trajectory and energy levels one by one.
                5. Core Advice for the Next Decade: Translate the macro analysis into a specific action guide, listing strategic focuses, action steps, and the underlying reasons for the next 10 years.

                Guidelines:
                - IMPORTANT: Write the ENTIRE analysis strictly in English. Do not use any other language. Make sure the headers correspond exactly to the requested sections in English.
                - Base your analysis purely on the provided HTML data. If the data is empty, invent a generic reading.
                - Format output in beautiful Markdown with clear headers (H2/H3) and bullet points.
                
                HTML DATA:
                ======================================
                {base_html_content}
                """
            
            model = genai.GenerativeModel(os.environ.get('AI_MODEL', 'gemini-2.5-flash'))
            response = model.generate_content(prompt)
            markdown_text = response.text
            
            # Convert Markdown to HTML
            ai_html_content = markdown.markdown(markdown_text, extensions=['extra', 'nl2br'])
            # Wrap overall analysis with target ID for TOC
            ai_html_content = f'<div id="section-overall">\n{ai_html_content}\n</div>'
            
            # --- First House Analysis ---
            try:
                import h1_analyzer
                first_house_md = h1_analyzer.analyze_first_house(user_email, user_name, language)
                first_house_html = markdown.markdown(first_house_md, extensions=['extra', 'nl2br'])
                # Append with a visual separator and target ID
                ai_html_content += f"\n<hr style='border:1px solid rgba(230, 201, 139, 0.2); margin: 3rem 0;'>\n<div id='section-house-1'>\n{first_house_html}\n</div>"
            except Exception as inner_e:
                ai_html_content += f"\n<p style='color: red;'>Error generating House 1 analysis: {str(inner_e)}</p>"

            # --- Second House Analysis ---
            try:
                import h2_analyzer
                second_house_md = h2_analyzer.analyze_second_house(user_email, user_name, language)
                second_house_html = markdown.markdown(second_house_md, extensions=['extra', 'nl2br'])
                # Append with a visual separator and target ID
                ai_html_content += f"\n<hr style='border:1px solid rgba(230, 201, 139, 0.2); margin: 3rem 0;'>\n<div id='section-house-2'>\n{second_house_html}\n</div>"
            except Exception as inner_e:
                ai_html_content += f"\n<p style='color: red;'>Error generating House 2 analysis: {str(inner_e)}</p>"

            # --- Third House Analysis ---
            try:
                import h3_analyzer
                third_house_md = h3_analyzer.analyze_third_house(user_email, user_name, language)
                third_house_html = markdown.markdown(third_house_md, extensions=['extra', 'nl2br'])
                # Append with a visual separator and target ID
                ai_html_content += f"\n<hr style='border:1px solid rgba(230, 201, 139, 0.2); margin: 3rem 0;'>\n<div id='section-house-3'>\n{third_house_html}\n</div>"
            except Exception as inner_e:
                ai_html_content += f"\n<p style='color: red;'>Error generating House 3 analysis: {str(inner_e)}</p>"

            # --- Fourth House Analysis ---
            try:
                import h4_analyzer
                fourth_house_md = h4_analyzer.analyze_fourth_house(user_email, user_name, language)
                fourth_house_html = markdown.markdown(fourth_house_md, extensions=['extra', 'nl2br'])
                # Append with a visual separator and target ID
                ai_html_content += f"\n<hr style='border:1px solid rgba(230, 201, 139, 0.2); margin: 3rem 0;'>\n<div id='section-house-4'>\n{fourth_house_html}\n</div>"
            except Exception as inner_e:
                ai_html_content += f"\n<p style='color: red;'>Error generating House 4 analysis: {str(inner_e)}</p>"

            # --- Fifth House Analysis ---
            try:
                import h5_analyzer
                fifth_house_md = h5_analyzer.analyze_fifth_house(user_email, user_name, language)
                fifth_house_html = markdown.markdown(fifth_house_md, extensions=['extra', 'nl2br'])
                # Append with a visual separator and target ID
                ai_html_content += f"\n<hr style='border:1px solid rgba(230, 201, 139, 0.2); margin: 3rem 0;'>\n<div id='section-house-5'>\n{fifth_house_html}\n</div>"
            except Exception as inner_e:
                ai_html_content += f"\n<p style='color: red;'>Error generating House 5 analysis: {str(inner_e)}</p>"

            # --- Sixth House Analysis ---
            try:
                import h6_analyzer
                sixth_house_md = h6_analyzer.analyze_sixth_house(user_email, user_name, language)
                sixth_house_html = markdown.markdown(sixth_house_md, extensions=['extra', 'nl2br'])
                # Append with a visual separator and target ID
                ai_html_content += f"\n<hr style='border:1px solid rgba(230, 201, 139, 0.2); margin: 3rem 0;'>\n<div id='section-house-6'>\n{sixth_house_html}\n</div>"
            except Exception as inner_e:
                ai_html_content += f"\n<p style='color: red;'>Error generating House 6 analysis: {str(inner_e)}</p>"
            
    except Exception as e:
        traceback.print_exc()
        ai_html_content = f"<p style='color: red;'>An error occurred during AI generation: {str(e)}</p>"

    # Generate Table of Contents
    try:
        import toc
        toc_html = toc.generate_toc_html(language)
    except Exception as e:
        toc_html = f"<!-- Error generating TOC: {str(e)} -->"

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
            position: fixed;
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
        
        {toc_html}
        
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
        
    report_url = f"/results/{user_email}/{user_name}/{html_filename}"
    return jsonify({
        'status': 'success',
        'report_url': report_url
    })
