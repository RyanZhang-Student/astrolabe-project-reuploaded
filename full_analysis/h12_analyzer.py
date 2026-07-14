import os
import re
import google.generativeai as genai

def analyze_twelfth_house(user_email: str, user_name: str, language: str = 'zh-CN') -> str:
    """
    Reads the 12th House HTML file for the user and generates an AI analysis.
    """
    from dotenv import load_dotenv
    load_dotenv(override=True)
    api_key = os.environ.get('GEMINI_API_KEY')
    if not api_key:
        return "Error: GEMINI_API_KEY not found in environment."

    # Configure Gemini
    genai.configure(api_key=api_key)
    
    # In order to read the house 12 chart result html
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    report_path = os.path.join(base_dir, 'results', user_email, user_name, f'{user_name}_HOUSE 12.html')
    
    html_content = ""
    if os.path.exists(report_path):
        with open(report_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
            html_content = re.sub(r'<img[^>]+>', '', html_content)
    else:
        return f"Error: Could not find House 12 report for user {user_name}. Looked at: {report_path}"

    # Default to English prompt
    prompt = f"""
    You are an expert, premium astrologer interface.
    I will provide you with the HTML structure of a generated Astrolabe report for a user's 12th House.
    Based on the specific data inside this HTML (including Classical Lord Evaluation, Modern Placements, Fixed Star Conjunctions, and Major Aspects), please provide a detailed, deeply insightful, and beautifully written astrological analysis focusing specifically on **House 12 (Subconscious, Secrets, and Karma)**.

    Do not say anything extra like "here is the report" or "this report suggests something". Just provide the analysis.
    Do not give score numbers and orb degrees.

    Please start your response with a main title:
    ## House 12 Deep Analysis

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
        Je vais vous fournir la structure HTML d'un rapport d'Astrolabe généré pour la 12ème Maison d'un utilisateur.
        Sur la base des données spécifiques à l'intérieur de ce HTML (y compris Classical Lord Evaluation, Modern Placements, Fixed Star Conjunctions, et Major Aspects), veuillez fournir une analyse astrologique détaillée, profondément perspicace et magnifiquement écrite, en vous concentrant spécifiquement sur la **Maison 12 (Subconscient, Secrets, et Karma)**.

        Ne dites rien de superflu comme « voici le rapport » ou « ce rapport suggère ». Fournissez uniquement l'analyse.
        Ne donnez pas de scores numériques ni de degrés d'orbe.

        Veuillez commencer votre réponse par un titre principal :
        ## Maison 12 Analyse Approfondie

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

    if language == 'en':
        prompt = f"""
        You are an expert, premium astrologer interface.
        I will provide you with the HTML structure of a generated Astrolabe report for a user's 12th House.
        Based on the specific data inside this HTML (including Classical Lord Evaluation, Modern Placements, Fixed Star Conjunctions, and Major Aspects), please provide a detailed, deeply insightful, and beautifully written astrological analysis focusing specifically on **House 12 (Subconscious, Secrets, and Karma)**.

        Do not say anything extra like "here is the report" or "this report suggests something". Just provide the analysis.
        Do not give score numbers and orb degrees.

        Please start your response with a main title:
        ## House 12 Deep Analysis

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
        return f"An error occurred during Gemini API call for House 12: {str(e)}"
