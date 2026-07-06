import os
import io
import base64
import traceback
from flask import jsonify

def generate_full_pdf(user_email, data, results_dir):
    """
    Generates a PDF containing the user's chart image, birth date/time, and location.
    Saves it in the user's specific results folder.
    """
    chart_img_data = data.get('chart_img')
    birth_date = data.get('birth_date', '')
    birth_time = data.get('birth_time', '')
    location = data.get('location', '')
    
    email_folder = os.path.join(results_dir, user_email)
    if not os.path.exists(email_folder):
        os.makedirs(email_folder)
        
    pdf_filename = f"full_report_{user_email}.pdf"
    pdf_filepath = os.path.join(email_folder, pdf_filename)
    
    try:
        from PIL import Image as PILImage
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import letter
        from reportlab.lib.utils import ImageReader
        from reportlab.lib.colors import HexColor
        
        c = canvas.Canvas(pdf_filepath, pagesize=letter)
        width, height = letter # 612 x 792
        
        # Fill background with #0d0b14 to match the astrolabe dark background
        c.setFillColor(HexColor('#0d0b14'))
        c.rect(0, 0, width, height, fill=True, stroke=False)
        
        # Position the square chart to take up a large portion of the page
        img_size = 500
        img_x = (width - img_size) / 2
        img_y = (height - img_size) / 2 + 35
        
        # Decode and draw chart image if available
        if chart_img_data and ',' in chart_img_data:
            header, base64_str = chart_img_data.split(',', 1)
            image_bytes = base64.b64decode(base64_str)
            img_buffer = io.BytesIO(image_bytes)
            pil_img = PILImage.open(img_buffer)
            img_reader = ImageReader(pil_img)
            c.drawImage(img_reader, img_x, img_y, width=img_size, height=img_size)
            
        # Draw user's birth time and location below the chart
        c.setFillColor(HexColor('#e6c98b')) # Golden color matching the theme
        c.setFont("Helvetica-Bold", 18)
        datetime_str = f"{birth_date} {birth_time}"
        c.drawCentredString(width / 2, img_y - 45, datetime_str)
        
        c.setFont("Helvetica", 14)
        c.setFillColor(HexColor('#a0aec0')) # Elegant slate gray/silver
        c.drawCentredString(width / 2, img_y - 75, location)
        
        c.showPage()
        c.save()
    except Exception as e:
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500
        
    pdf_url = f"/results/{user_email}/{pdf_filename}"
    return jsonify({
        'status': 'success',
        'pdf_url': pdf_url
    })
