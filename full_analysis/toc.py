def generate_toc_html(language: str) -> str:
    """
    Generates a Table of Contents (TOC) HTML block based on the language.
    """
    if language == 'fr':
        items = [
            ("section-overall", "Rapport Astrolabe : Analyse Astrologique Profonde"),
            ("section-house-1", "Maison 1 Analyse Approfondie"),
            ("section-house-2", "Maison 2 Analyse Approfondie"),
            ("section-house-3", "Maison 3 Analyse Approfondie"),
            ("section-house-4", "Maison 4 Analyse Approfondie"),
            ("section-house-5", "Maison 5 Analyse Approfondie"),
            ("section-house-6", "Maison 6 Analyse Approfondie"),
            ("section-house-7", "Maison 7 Analyse Approfondie"),
            ("section-house-8", "Maison 8 Analyse Approfondie"),
            ("section-house-9", "Maison 9 Analyse Approfondie"),
            ("section-house-10", "Maison 10 Analyse Approfondie"),
            ("section-house-11", "Maison 11 Analyse Approfondie"),
            ("section-house-12", "Maison 12 Analyse Approfondie")
        ]
        toc_title = "Table des Matières"
    else:
        items = [
            ("section-overall", "Astrolabe Report: Deep Astrological Analysis"),
            ("section-house-1", "House 1 Deep Analysis"),
            ("section-house-2", "House 2 Deep Analysis"),
            ("section-house-3", "House 3 Deep Analysis"),
            ("section-house-4", "House 4 Deep Analysis"),
            ("section-house-5", "House 5 Deep Analysis"),
            ("section-house-6", "House 6 Deep Analysis"),
            ("section-house-7", "House 7 Deep Analysis"),
            ("section-house-8", "House 8 Deep Analysis"),
            ("section-house-9", "House 9 Deep Analysis"),
            ("section-house-10", "House 10 Deep Analysis"),
            ("section-house-11", "House 11 Deep Analysis"),
            ("section-house-12", "House 12 Deep Analysis")
        ]
        toc_title = "Table of Contents"

    # We use some elegant inline styles or classes for the TOC
    toc_items = "".join([
        f"<li style='margin-bottom: 0.8rem; border-bottom: 1px dotted rgba(230, 201, 139, 0.2); padding-bottom: 0.3rem;'>"
        f"<a href='#{item_id}' style='color: #e6c98b; text-decoration: none; transition: color 0.2s ease;' "
        f"onmouseover=\"this.style.color='#ffcc00'\" onmouseout=\"this.style.color='#e6c98b'\">{title}</a></li>"
        for item_id, title in items
    ])

    html = f"""
    <div class="toc-container" style="
        width: 100%; 
        max-width: 600px; 
        margin: 0 auto 3rem auto; 
        padding: 2rem; 
        background: rgba(20, 18, 25, 0.6); 
        border: 1px solid rgba(230, 201, 139, 0.2); 
        border-radius: 12px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.3);
    ">
        <h2 style="
            color: #ffcc00; 
            font-family: 'Cormorant Garamond', serif; 
            font-size: 1.8rem; 
            margin-top: 0; 
            margin-bottom: 1.5rem; 
            text-align: center; 
            letter-spacing: 2px;
            border-bottom: 2px solid rgba(255, 204, 0, 0.3);
            padding-bottom: 0.5rem;
        ">{toc_title}</h2>
        <ul style="
            list-style-type: none; 
            padding: 0; 
            margin: 0; 
            font-size: 1.2rem;
            font-family: 'Cormorant Garamond', serif;
        ">
            {toc_items}
        </ul>
    </div>
    """
    
    return html
