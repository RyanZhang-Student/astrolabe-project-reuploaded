from utils import pol2cart
from constants import SIGNS, PLANET_COLORS, ASPECT_COLORS

def create_pro_svg(planets, aspects):
    cx, cy, r_out, r_in = 400, 400, 350, 280
    r_house_label = 385  
    asc_lon = planets.get('Asc', {'lon': 0})['lon']
    
    svg = [
        '<defs>',
        '<marker id="arrowhead_brown" markerWidth="10" markerHeight="7" refX="10" refY="3.5" orient="auto"><polygon points="0 0, 10 3.5, 0 7" fill="rgba(230, 201, 139, 0.7)" /></marker>',
        '<marker id="arrowhead_red" markerWidth="10" markerHeight="7" refX="10" refY="3.5" orient="auto"><polygon points="0 0, 10 3.5, 0 7" fill="rgba(230, 201, 139, 0.9)" /></marker>',
        '<radialGradient id="sunGlow"><stop offset="0%" stop-color="rgba(230, 201, 139, 0.8)"/><stop offset="100%" stop-color="rgba(230, 201, 139, 0)"/></radialGradient>',
        '</defs>',
        f'<circle cx="{cx}" cy="{cy}" r="{r_out}" stroke="rgba(230, 201, 139, 0.4)" stroke-width="1.5" fill="#0d0b14"/>'
    ]
    
    for i in range(12):
        angle = i * 30
        draw_angle = (angle - asc_lon) % 360
        x1, y1 = pol2cart(cx, cy, r_in, draw_angle)
        x2, y2 = pol2cart(cx, cy, r_out, draw_angle)
        svg.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="rgba(230, 201, 139, 0.2)" stroke-width="1"/>')
        tx, ty = pol2cart(cx, cy, (r_out + r_in)/2, (draw_angle + 15) % 360)
        svg.append(f'<text data-sign="{SIGNS[i]}" x="{tx}" y="{ty}" font-family="\'Cormorant Garamond\', serif" font-size="20" font-style="italic" font-weight="400" text-anchor="middle" dominant-baseline="middle" fill="#e6c98b">{SIGNS[i][:3]}</text>')
    
    for h in range(1, 13):
        h_angle_start = (h - 1) * 30 
        hx1, hy1 = pol2cart(cx, cy, r_out, h_angle_start)
        hx2, hy2 = pol2cart(cx, cy, r_out + 12, h_angle_start)
        svg.append(f'<line x1="{hx1}" y1="{hy1}" x2="{hx2}" y2="{hy2}" stroke="rgba(230, 201, 139, 0.6)" stroke-width="1"/>')
        text_angle = h_angle_start + 15
        tx, ty = pol2cart(cx, cy, r_house_label, text_angle)
        svg.append(f'<text x="{tx}" y="{ty}" font-family="\'Inter\', sans-serif" font-size="12" font-weight="400" letter-spacing="2" text-anchor="middle" dominant-baseline="middle" fill="rgba(230, 201, 139, 0.6)">H{h}</text>')

    svg.append(f'<circle cx="{cx}" cy="{cy}" r="{r_in}" stroke="rgba(230, 201, 139, 0.3)" fill="none" stroke-width="1"/>')
    svg.append(f'<circle cx="{cx}" cy="{cy}" r="60" fill="url(#sunGlow)"/>')
    svg.append(f'<circle cx="{cx}" cy="{cy}" r="35" fill="#e6c98b" filter="drop-shadow(0 0 8px rgba(230,201,139,0.5))"/>')
    
    if 'Midheaven' in planets:
        mc_data = planets['Midheaven']
        mc_lon = mc_data['lon']
        mc_draw_angle = (mc_lon - asc_lon) % 360
        mi_color = "rgba(230, 201, 139, 0.8)"
        mix, miy = pol2cart(cx, cy, r_in - 15, mc_draw_angle) 
        milx, mily = pol2cart(cx, cy, r_in + 15, mc_draw_angle)
        svg.append(f'<circle cx="{mix}" cy="{miy}" r="3" fill="{mi_color}"/>')
        svg.append(f'<text data-point="Mi" x="{milx}" y="{mily}" font-family="\'Inter\', sans-serif" font-size="10" font-weight="600" text-anchor="middle" fill="{mi_color}">Mi</text>')

    if 'Midheaven' in planets:
        mc_lon = planets['Midheaven']['lon']
        mc_draw_angle = (mc_lon - asc_lon) % 360
        ic_draw_angle = (mc_draw_angle + 180) % 360
        x_ic, y_ic = pol2cart(cx, cy, r_out, ic_draw_angle)
        x_mc, y_mc = pol2cart(cx, cy, r_out + 15, mc_draw_angle)
        svg.append(f'<line x1="{x_ic}" y1="{y_ic}" x2="{x_mc}" y2="{y_mc}" stroke="rgba(230, 201, 139, 0.5)" stroke-width="1" stroke-dasharray="6,4" marker-end="url(#arrowhead_brown)" />')
        x_ic_txt, y_ic_txt = pol2cart(cx, cy, r_out + 25, ic_draw_angle)
        svg.append(f'<text data-point="IC" x="{x_ic_txt}" y="{y_ic_txt}" font-family="\'Inter\', sans-serif" font-size="12" font-weight="400" letter-spacing="1" text-anchor="middle" dominant-baseline="middle" fill="rgba(230, 201, 139, 0.7)">IC</text>')
        x_mc_txt, y_mc_txt = pol2cart(cx, cy, r_out + 35, mc_draw_angle)
        svg.append(f'<text data-point="MC" x="{x_mc_txt}" y="{y_mc_txt}" font-family="\'Inter\', sans-serif" font-size="12" font-weight="400" letter-spacing="1" text-anchor="middle" dominant-baseline="middle" fill="rgba(230, 201, 139, 0.7)">MC</text>')

    if 'Asc' in planets:
        asc_color = "rgba(230, 201, 139, 0.9)"
        x_des_line, y_des_line = pol2cart(cx, cy, r_out, 180)
        x_asc_line, y_asc_line = pol2cart(cx, cy, r_out + 15, 0)
        svg.append(f'<line x1="{x_des_line}" y1="{y_des_line}" x2="{x_asc_line}" y2="{y_asc_line}" stroke="{asc_color}" stroke-width="1" stroke-dasharray="6,4" marker-end="url(#arrowhead_red)" opacity="0.8"/>')
        asx, asy = pol2cart(cx, cy, r_in - 15, 0)
        aslx, asly = pol2cart(cx, cy, r_in + 15, 0)
        svg.append(f'<circle cx="{asx}" cy="{asy}" r="3" fill="{asc_color}"/>')
        svg.append(f'<text data-point="As" x="{aslx}" y="{asly}" font-family="\'Inter\', sans-serif" font-size="10" font-weight="600" text-anchor="middle" fill="{asc_color}">As</text>')
        x_asc_txt, y_asc_txt = pol2cart(cx, cy, r_out + 35, 0)
        svg.append(f'<text data-point="ASC" x="{x_asc_txt}" y="{y_asc_txt}" font-family="\'Inter\', sans-serif" font-size="12" font-weight="400" letter-spacing="1" text-anchor="middle" dominant-baseline="middle" fill="{asc_color}">ASC</text>')
        x_des_txt, y_des_txt = pol2cart(cx, cy, r_out + 25, 180)
        svg.append(f'<text data-point="DES" x="{x_des_txt}" y="{y_des_txt}" font-family="\'Inter\', sans-serif" font-size="12" font-weight="400" letter-spacing="1" text-anchor="middle" dominant-baseline="middle" fill="{asc_color}">DES</text>')

    for asp in aspects:
        p1, p2 = asp['p1'], asp['p2']
        if p1 in ['Asc', 'Midheaven', 'IC', 'Dsc'] or p1.startswith('House '):
            continue
        if p2 in ['Asc', 'Midheaven', 'IC', 'Dsc'] or p2.startswith('House '):
            continue

        lon1_draw = (planets[p1]['lon'] - asc_lon) % 360
        lon2_draw = (planets[p2]['lon'] - asc_lon) % 360
        x1, y1 = pol2cart(cx, cy, r_in - 10, lon1_draw)
        x2, y2 = pol2cart(cx, cy, r_in - 10, lon2_draw)
        
        # Subtle aspect line colors
        color = 'rgba(255, 255, 255, 0.1)'
        if asp['type'] == 'Trine' or asp['type'] == 'Sextile':
            color = 'rgba(100, 200, 255, 0.2)'
        elif asp['type'] == 'Square' or asp['type'] == 'Opposition':
            color = 'rgba(255, 100, 100, 0.2)'
        elif asp['type'] == 'Conjunction':
            color = 'rgba(230, 201, 139, 0.25)'
            
        svg.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}" stroke-width="1"/>')
    
    for name, data in planets.items():
        if name in ['Midheaven', 'IC', 'Asc', 'Dsc'] or name.startswith('House '): continue
        draw_lon = (data['lon'] - asc_lon) % 360
        color = PLANET_COLORS.get(name, 'white')
        px, py = pol2cart(cx, cy, r_in - 15, draw_lon)
        lx, ly = pol2cart(cx, cy, r_in + 15, draw_lon)
        svg.append(f'<circle cx="{px}" cy="{py}" r="3" fill="{color}"/>')
        svg.append(f'<text data-planet="{name}" x="{lx}" y="{ly}" font-family="\'Inter\', sans-serif" font-size="11" font-weight="600" text-anchor="middle" fill="{color}">{name[:2]}</text>')
    
    return "".join(svg)
