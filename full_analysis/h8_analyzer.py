import os
import re
import google.generativeai as genai

def analyze_eighth_house(user_email: str, user_name: str, language: str = 'zh-CN') -> str:
    """
    Reads the 8th House HTML file for the user and generates an AI analysis.
    """
    from dotenv import load_dotenv
    load_dotenv(override=True)
    api_key = os.environ.get('GEMINI_API_KEY')
    if not api_key:
        return "Error: GEMINI_API_KEY not found in environment."

    # Configure Gemini
    genai.configure(api_key=api_key)
    
    # In order to read the house 8 chart result html
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    report_path = os.path.join(base_dir, 'results', user_email, user_name, f'{user_name}_HOUSE 8.html')
    
    html_content = ""
    if os.path.exists(report_path):
        with open(report_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
            html_content = re.sub(r'<img[^>]+>', '', html_content)
    else:
        return f"Error: Could not find House 8 report for user {user_name}. Looked at: {report_path}"

    # Default to English prompt
    prompt = f"""
    You are an expert, premium astrologer interface.
    I will provide you with the HTML structure of a generated Astrolabe report for a user's 8th House.
    Based on the specific data inside this HTML (including Classical Lord Evaluation, Modern Placements, Fixed Star Conjunctions, and Major Aspects), please provide a detailed, deeply insightful, and beautifully written astrological analysis focusing specifically on **House 8 (Transformation, Shared Resources, and Rebirth)**.

    Do not say anything extra like "here is the report" or "this report suggests something". Just provide the analysis.
    Do not give score numbers and orb degrees.

    Please start your response with a main title:
    ## House 8 Deep Analysis

    Please cover the following EXACT sections in your response, providing comprehensive details for each:
    - Concept Introduction: Explains the core definition and practical significance of this house in astrology or in the relevant area of life.
    - Foundation & Blueprint: Analyzes the zodiac sign ruling the cusp of this house, interpreting the innate traits, image, and potential challenges it brings to that area of life.
    - Core Drivers: Ruler Alignment: Identifies the zodiac sign, house, and retrograde status of the ruling planet (house ruler) for this house, and provides a detailed breakdown of the network of aspects formed between this ruling planet and the Sun, other core celestial bodies, and virtual points.
    - Energy Matrix: Planetary Distribution and Aspects: Analyzes the planets and asteroids directly located within the house, the energy at the cusp, and their interactive aspects with other celestial bodies.
    - Deep Insights: Hidden Influences: Explore conjunctions with fixed stars within the house or near the ruling planet to reveal more hidden, deeper destinies or special empowerments.
    - Dynamic Analysis: Organically integrate all the above elements (zodiac signs, ruling planet, inner planets, fixed stars) to distill an overall energetic picture of this domain.
    - House Qualitative Summary: Provides a concise, final qualitative assessment of the house’s core energy, strengths, and risks.
    - Core Action Strategy Recommendations: Lists several (typically 8–10) highly targeted, well-organized, and actionable recommendations, fully translating the analysis into practical application.

    Guidelines:
    - IMPORTANT: Write the entire analysis strictly in English. Do not use any other language.
    - Format output in beautiful Markdown with headers and bullet points.

    HTML DATA:
    ======================================
    {html_content}
    """

    if language == 'fr':
        prompt = f"""
        Vous êtes une interface d'astrologie experte et haut de gamme.
        Je vais vous fournir la structure HTML d'un rapport d'Astrolabe généré pour la 8ème Maison d'un utilisateur.
        Sur la base des données spécifiques à l'intérieur de ce HTML (y compris Classical Lord Evaluation, Modern Placements, Fixed Star Conjunctions, et Major Aspects), veuillez fournir une analyse astrologique détaillée, profondément perspicace et magnifiquement écrite, en vous concentrant spécifiquement sur la **Maison 8 (Transformation, Ressources Partagées, et Renaissance)**.

        Ne dites rien de superflu comme « voici le rapport » ou « ce rapport suggère ». Fournissez uniquement l'analyse.
        Ne donnez pas de scores numériques ni de degrés d'orbe.

        Veuillez commencer votre réponse par un titre principal :
        ## Maison 8 Analyse Approfondie

        Veuillez aborder EXACTEMENT les sections suivantes dans votre réponse, en fournissant des détails complets pour chacune :
        - Présentation du concept: Explique la définition fondamentale et la signification pratique de cette maison en astrologie ou dans le domaine de vie correspondant.
        - Fondements et plan directeur: Analyse le signe du zodiaque régissant la cuspide de cette maison, en interprétant les traits innés, l'image et les défis potentiels qu'il apporte à ce domaine de vie.
        - principaux facteurs : Identifie le signe du zodiaque, la maison et l'état de rétrogradation de la planète maîtresse (régent de la maison) pour cette maison, et fournit une analyse détaillée du réseau d'aspects formés entre cette planète maîtresse et le Soleil, d'autres corps célestes essentiels et les points virtuels.
        - Matrice énergétique : Analyse les planètes et astéroïdes directement situés dans la maison, l'énergie à la cuspide et leurs aspects interactifs avec d'autres corps célestes.
        - analyses approfondies : Explore les conjonctions avec les étoiles fixes dans la maison ou à proximité de la planète maîtresse pour révéler des destins plus cachés et profonds ou des habilitations spéciales.
        - analyse dynamique : Intègre de manière organique tous les éléments ci-dessus (signes du zodiaque, planète maîtresse, planètes intérieures, étoiles fixes) pour distiller une image énergétique globale de ce domaine.
        - Résumé qualitatif de la maison: Fournit une évaluation qualitative concise et finale de l'énergie fondamentale de la maison, de ses forces et de ses risques.
        - Recommandations relatives à la stratégie d'action principale: Liste plusieurs (généralement 8 à 10) recommandations très ciblées, bien organisées et applicables, traduisant pleinement l'analyse en applications pratiques.

        Directives :
        - IMPORTANT : Rédigez l'intégralité de l'analyse strictement en français. N'utilisez aucune autre langue.
        - Formatez la sortie dans un format Markdown soigné avec des en-têtes et  des listes à puces.

        DONNÉES HTML :
        ======================================
        {html_content}
        """

    if language == 'zh':
        prompt = f"""
        你是一个专家级的高端占星分析引擎。
        我将为你提供一个用户 Astrolabe 星盘报告的 HTML 结构，专门针对第 8 宫。
        基于这个 HTML 内部的具体数据（包括古典占星守护星评估、现代落位、恒星合相和主要相位），请提供一份详细、见解深刻且文笔优美的占星分析，专门针对 **第 8 宫**。

        不要说任何多余的话，如“这是您的报告”或“该报告表明”。直接开始你的分析。
        不要提供数字分数或容许度度数。

        请在你的回复开头加上主标题：
        ## 第 8 宫深度分析

        请在你的回复中准确涵盖以下部分，并为每个部分提供详尽的细节：
        - 概念介绍：解释该宫位在占星学或对应生活领域中的基本定义和实际意义。
        - 基础与蓝图：分析该宫位宫头所在的星座，解读其为该生活领域带来的天生特质、形象和潜在挑战。
        - 核心驱动力：找出该宫位主星（宫主星）的星座、落宫和逆行状态，并详细分析该主星与太阳、其他核心天体及虚点形成的相位网络。
        - 能量矩阵：分析直接落入该宫位的行星和四神星，宫头的能量，以及它们与其他天体的互动相位。
        - 深度解析：探索该宫位内或主星附近的恒星合相，以揭示更隐秘深远的宿命或特殊赋能。
        - 动态综合分析：有机地整合上述所有元素（星座、主星、内行星、恒星），提炼出该领域的整体能量图景。
        - 宫位定性总结：提供一个简洁而最终的定性评估，总结该宫位的核心能量、优势和风险。
        - 核心行动战略建议：列出几条（通常为8-10条）极具针对性、条理清晰且可操作的建议，将分析完全转化为实际应用。

        指南：
        - 重要：严格使用纯正、地道的中文进行完整的分析。不要使用其他语言。
        - 将输出格式化为优美的 Markdown，使用清晰的标题和无序列表。

        HTML 数据：
        ======================================
        {html_content}
        """

    if language == 'en':
        prompt = f"""
        You are an expert, premium astrologer interface.
        I will provide you with the HTML structure of a generated Astrolabe report for a user's 8th House.
        Based on the specific data inside this HTML (including Classical Lord Evaluation, Modern Placements, Fixed Star Conjunctions, and Major Aspects), please provide a detailed, deeply insightful, and beautifully written astrological analysis focusing specifically on **House 8 (Transformation, Shared Resources, and Rebirth)**.

        Do not say anything extra like "here is the report" or "this report suggests something". Just provide the analysis.
        Do not give score numbers and orb degrees.

        Please start your response with a main title:
        ## House 8 Deep Analysis

        Please cover the following EXACT sections in your response, providing comprehensive details for each:
        - Concept Introduction: Explains the core definition and practical significance of this house in astrology or in the relevant area of life.
        - Foundation & Blueprint: Analyzes the zodiac sign ruling the cusp of this house, interpreting the innate traits, image, and potential challenges it brings to that area of life.
        - Core Drivers: Ruler Alignment: Identifies the zodiac sign, house, and retrograde status of the ruling planet (house ruler) for this house, and provides a detailed breakdown of the network of aspects formed between this ruling planet and the Sun, other core celestial bodies, and virtual points.
        - Energy Matrix: Planetary Distribution and Aspects: Analyzes the planets and asteroids directly located within the house, the energy at the cusp, and their interactive aspects with other celestial bodies.
        - Deep Insights: Hidden Influences: Explore conjunctions with fixed stars within the house or near the ruling planet to reveal more hidden, deeper destinies or special empowerments.
        - Dynamic Analysis: Organically integrate all the above elements (zodiac signs, ruling planet, inner planets, fixed stars) to distill an overall energetic picture of this domain.
        - House Qualitative Summary: Provides a concise, final qualitative assessment of the house’s core energy, strengths, and risks.
        - Core Action Strategy Recommendations: Lists several (typically 8–10) highly targeted, well-organized, and actionable recommendations, fully translating the analysis into practical application.

        Guidelines:
        - IMPORTANT: Write the entire analysis strictly in English. Do not use any other language.
        - Format output in beautiful Markdown with headers and bullet points.

        HTML DATA:
        ======================================
        {html_content}
        """



    try:
        model = genai.GenerativeModel(os.environ.get('AI_MODEL', 'gemini-2.5-flash'))
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"An error occurred during Gemini API call for House 8: {str(e)}"
