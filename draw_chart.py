from utils import pol2cart
from constants import SIGNS, PLANET_COLORS, ASPECT_COLORS

def create_pro_svg(planets, aspects):
    cx, cy, r_out, r_in = 400, 400, 350, 280
    r_house_label = 385  
    asc_lon = planets.get('Asc', {'lon': 0})['lon']
    
    svg = [
        '<defs><marker id="arrowhead_brown" markerWidth="10" markerHeight="7" refX="10" refY="3.5" orient="auto"><polygon points="0 0, 10 3.5, 0 7" fill="#8B4513" /></marker></defs>',
        '<marker id="arrowhead_red" markerWidth="10" markerHeight="7" refX="10" refY="3.5" orient="auto"><polygon points="0 0, 10 3.5, 0 7" fill="#FF0000" /></marker>'
        f'<circle cx="{cx}" cy="{cy}" r="{r_out}" stroke="#333" stroke-width="2" fill="white"/>'
    ]
    
    for i in range(12):
        angle = i * 30
        draw_angle = (angle - asc_lon) % 360
        x1, y1 = pol2cart(cx, cy, r_in, draw_angle)
        x2, y2 = pol2cart(cx, cy, r_out, draw_angle)
        svg.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="#ccc" />')
        tx, ty = pol2cart(cx, cy, (r_out + r_in)/2, (draw_angle + 15) % 360)
        svg.append(f'<text x="{tx}" y="{ty}" font-size="14" font-weight="bold" text-anchor="middle" dominant-baseline="middle" fill="#555">{SIGNS[i][:3]}</text>')
    
    for h in range(1, 13):
        h_angle_start = (h - 1) * 30 
        hx1, hy1 = pol2cart(cx, cy, r_out, h_angle_start)
        hx2, hy2 = pol2cart(cx, cy, r_out + 12, h_angle_start)
        svg.append(f'<line x1="{hx1}" y1="{hy1}" x2="{hx2}" y2="{hy2}" stroke="red" stroke-width="2"/>')
        text_angle = h_angle_start + 15
        tx, ty = pol2cart(cx, cy, r_house_label, text_angle)
        svg.append(f'<text x="{tx}" y="{ty}" font-size="14" font-weight="bold" text-anchor="middle" dominant-baseline="middle" fill="red">H{h}</text>')

    svg.append(f'<circle cx="{cx}" cy="{cy}" r="{r_in}" stroke="#ccc" fill="none"/>')
    
    if 'Midheaven' in planets:
        mc_data = planets['Midheaven']
        mc_lon = mc_data['lon']
        mc_draw_angle = (mc_lon - asc_lon) % 360
        mi_color = PLANET_COLORS.get('Midheaven', '#8B4513')
        mix, miy = pol2cart(cx, cy, r_in - 15, mc_draw_angle) 
        milx, mily = pol2cart(cx, cy, r_in + 15, mc_draw_angle)
        svg.append(f'<circle cx="{mix}" cy="{miy}" r="4" fill="{mi_color}"/>')
        svg.append(f'<text x="{milx}" y="{mily}" font-size="11" font-weight="bold" text-anchor="middle" fill="{mi_color}">Mi</text>')

    if 'Midheaven' in planets:
        mc_lon = planets['Midheaven']['lon']
        mc_draw_angle = (mc_lon - asc_lon) % 360
        ic_draw_angle = (mc_draw_angle + 180) % 360
        x_ic, y_ic = pol2cart(cx, cy, r_out, ic_draw_angle)
        x_mc, y_mc = pol2cart(cx, cy, r_out + 15, mc_draw_angle)
        svg.append(f'<line x1="{x_ic}" y1="{y_ic}" x2="{x_mc}" y2="{y_mc}" stroke="#8B4513" stroke-width="1.5" stroke-dasharray="8,4" marker-end="url(#arrowhead_brown)" />')
        x_ic_txt, y_ic_txt = pol2cart(cx, cy, r_out + 25, ic_draw_angle)
        svg.append(f'<text x="{x_ic_txt}" y="{y_ic_txt}" font-size="14" font-weight="bold" text-anchor="middle" dominant-baseline="middle" fill="#8B4513">IC</text>')
        x_mc_txt, y_mc_txt = pol2cart(cx, cy, r_out + 35, mc_draw_angle)
        svg.append(f'<text x="{x_mc_txt}" y="{y_mc_txt}" font-size="14" font-weight="bold" text-anchor="middle" dominant-baseline="middle" fill="#8B4513">MC</text>')

    if 'Asc' in planets:
        asc_color = "#FF0000"
        x_des_line, y_des_line = pol2cart(cx, cy, r_out, 180)
        x_asc_line, y_asc_line = pol2cart(cx, cy, r_out + 15, 0)
        svg.append(f'<line x1="{x_des_line}" y1="{y_des_line}" x2="{x_asc_line}" y2="{y_asc_line}" stroke="{asc_color}" stroke-width="1.5" stroke-dasharray="8,4" marker-end="url(#arrowhead_red)" opacity="0.8"/>')
        asx, asy = pol2cart(cx, cy, r_in - 15, 0)
        aslx, asly = pol2cart(cx, cy, r_in + 15, 0)
        svg.append(f'<circle cx="{asx}" cy="{asy}" r="4" fill="{asc_color}"/>')
        svg.append(f'<text x="{aslx}" y="{asly}" font-size="11" font-weight="bold" text-anchor="middle" fill="{asc_color}">As</text>')
        x_asc_txt, y_asc_txt = pol2cart(cx, cy, r_out + 35, 0)
        svg.append(f'<text x="{x_asc_txt}" y="{y_asc_txt}" font-size="14" font-weight="bold" text-anchor="middle" dominant-baseline="middle" fill="{asc_color}">ASC</text>')
        x_des_txt, y_des_txt = pol2cart(cx, cy, r_out + 25, 180)
        svg.append(f'<text x="{x_des_txt}" y="{y_des_txt}" font-size="14" font-weight="bold" text-anchor="middle" dominant-baseline="middle" fill="{asc_color}">DES</text>')

    for asp in aspects:
        p1, p2 = asp['p1'], asp['p2']
        # Skip drawing aspects for house cusps and major angles to keep the chart clean
        if p1 in ['Asc', 'Midheaven', 'IC', 'Dsc'] or p1.startswith('House '):
            continue
        if p2 in ['Asc', 'Midheaven', 'IC', 'Dsc'] or p2.startswith('House '):
            continue

        lon1_draw = (planets[p1]['lon'] - asc_lon) % 360
        lon2_draw = (planets[p2]['lon'] - asc_lon) % 360
        x1, y1 = pol2cart(cx, cy, r_in - 10, lon1_draw)
        x2, y2 = pol2cart(cx, cy, r_in - 10, lon2_draw)
        color = ASPECT_COLORS.get(asp['type'], '#eee')
        svg.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}" stroke-width="1" opacity="0.6"/>')
    
    for name, data in planets.items():
        if name in ['Midheaven', 'IC', 'Asc', 'Dsc'] or name.startswith('House '): continue
        draw_lon = (data['lon'] - asc_lon) % 360
        color = PLANET_COLORS.get(name, 'black')
        px, py = pol2cart(cx, cy, r_in - 15, draw_lon)
        lx, ly = pol2cart(cx, cy, r_in + 15, draw_lon)
        svg.append(f'<circle cx="{px}" cy="{py}" r="4" fill="{color}"/>')
        svg.append(f'<text x="{lx}" y="{ly}" font-size="11" font-weight="bold" text-anchor="middle" fill="{color}">{name[:2]}</text>')
    
    return "".join(svg)
