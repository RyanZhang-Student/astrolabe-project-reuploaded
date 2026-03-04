import os
import webbrowser
from constants import *
from utils import *
from engine import get_astronomical_data
# Import functionality from planets.py
from planets import get_star_longitudes, check_star_aspects
# 新增：引入星体计算工具
from star_calc import calculate_star_conjunctions_and_stats

# bruh reuploading the repository
'''
try:
    from ai_analysis_1 import generate_and_append_analysis_1
    from ai_analysis_2 import generate_and_append_analysis_2
    from ai_analysis_3 import generate_and_append_analysis_3
    from ai_analysis_4 import generate_and_append_analysis_4
    from ai_analysis_5 import generate_and_append_analysis_5
    from ai_analysis_6 import generate_and_append_analysis_6
    from ai_analysis_7 import generate_and_append_analysis_7

    HAS_AI = True
except ImportError as e:
    print(f"⚠️ AI 模块加载失败，原因: {e}")
    print("💡 请运行: pip install google-genai")
    HAS_AI = False
  '''  


def get_classical_row(house_num, asc_lon, planets, is_day):
    asc_sign_name, _ = get_zodiac_sign(asc_lon)
    asc_idx = SIGNS.index(asc_sign_name)
    cusp_sign = SIGNS[(asc_idx + house_num - 1) % 12]
    ruler_name = CLASSICAL_RULERS[cusp_sign]
    
    if ruler_name not in planets:
        return f"<tr><td>{house_num}</td><td>{cusp_sign}</td><td>{ruler_name}</td><td colspan='14'>Data Unavailable</td></tr>"
    
    ruler_data = planets[ruler_name]
    ruler_lon = ruler_data['lon']
    ruler_sign, ruler_deg = get_zodiac_sign(ruler_lon)
    ruler_house = determine_house(ruler_lon, asc_lon)
    
    state = "Peregrine"
    if CLASSICAL_RULERS[ruler_sign] == ruler_name: state = "Domicile"
    elif EXALTATIONS.get(ruler_sign) == ruler_name: state = "Exalted"
    elif DETRIMENTS.get(ruler_sign) == ruler_name: state = "Detriment"
    elif FALLS.get(ruler_sign) == ruler_name: state = "Fall"
    
    dignities_here = get_dignities_at_position(ruler_sign, ruler_deg, is_day)
    in_term = "Yes" if dignities_here['term'] == ruler_name else "-"
    in_face = "Yes" if dignities_here['face'] == ruler_name else "-"
    in_trip = "Yes" if dignities_here['trip'] == ruler_name else "-"
    
    sun_lon = planets['Sun']['lon']
    diff_sun = abs(ruler_lon - sun_lon)
    if diff_sun > 180: diff_sun = 360 - diff_sun
    combustion = "Yes" if diff_sun < 8.5 and ruler_name != 'Sun' else "-"
    retro = "Rx" if ruler_data.get('is_retro') else "-"
    
    receptions = get_advanced_reception(ruler_name, planets, is_day)
    rel_str_list = []
    for r in receptions:
        # 根据等级添加视觉标签
        level_tag = "⭐" * r['level']
        status = " (有效)" if r['has_aspect'] else " (暗中)"
        reject = " [❗互拒]" if r['is_rejected'] else ""
        rel_info = f"{r['from']}{level_tag}{status}{reject}"
        rel_str_list.append(rel_info)
    rel_final_str = "<br>".join(rel_str_list) if rel_str_list else "-"

    mut_rec, mut_rej = calculate_mutual_reception_rejection(ruler_name, ruler_data, planets, is_day)
    debilities_here = get_debilities_at_position(ruler_sign)
    rej_by_str = ", ".join([p for p in debilities_here if p in planets]) or "-"

    receivers = []
    for k, label in [('domicile', 'Dom'), ('exalt', 'Exalt'), ('term', 'Term')]:
        if dignities_here[k] and dignities_here[k] != ruler_name:
            receivers.append(dignities_here[k])
    rec_by_str = ", ".join(list(dict.fromkeys(receivers))) or "-"

    deg_str = f"{int(ruler_deg)}°{int((ruler_deg % 1)*60)}'"
    return f"<tr><td>{house_num}</td><td>{cusp_sign}</td><td>{ruler_name}</td><td>{ruler_house}</td><td>{ruler_sign}</td><td>{deg_str}</td><td>{state}</td><td>{in_term}</td><td>{in_face}</td><td>{in_trip}</td><td>{combustion}</td><td>{retro}</td><td>{rel_final_str}</td><td>{mut_rej}</td><td>{rej_by_str}</td><td>{rec_by_str}</td><td>-</td></tr>"



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
        lon1_draw = (planets[asp['p1']]['lon'] - asc_lon) % 360
        lon2_draw = (planets[asp['p2']]['lon'] - asc_lon) % 360
        x1, y1 = pol2cart(cx, cy, r_in - 10, lon1_draw)
        x2, y2 = pol2cart(cx, cy, r_in - 10, lon2_draw)
        color = ASPECT_COLORS.get(asp['type'], '#eee')
        svg.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}" stroke-width="1" opacity="0.6"/>')
    
    for name, data in planets.items():
        if name in ['Midheaven', 'IC', 'Asc', 'Dsc']: continue
        draw_lon = (data['lon'] - asc_lon) % 360
        color = PLANET_COLORS.get(name, 'black')
        px, py = pol2cart(cx, cy, r_in - 15, draw_lon)
        lx, ly = pol2cart(cx, cy, r_in + 15, draw_lon)
        svg.append(f'<circle cx="{px}" cy="{py}" r="4" fill="{color}"/>')
        svg.append(f'<text x="{lx}" y="{ly}" font-size="11" font-weight="bold" text-anchor="middle" fill="{color}">{name[:2]}</text>')
    
    return "".join(svg)

def generate_report():
    print("\n" + "="*45 + "\n   ASTROLABE DRAWING AND ANALYZING - MODULAR V17\n" + "="*45)
    user_name = input("Enter Name: ").strip().upper()
    dob_input = input("Date (YYYY-MMDD-HHMM): ").strip()
    location_input = input("City-Country (e.g., BEIJING-CN): ").strip()

    data_tuple = get_astronomical_data(dob_input, location_input)
    if data_tuple[0] is None: 
        print(data_tuple[1])
        return
        
    planets, meta, time_data = data_tuple
    localized_dt, tz_str, formatted_location = meta
    ts, t = time_data
    
    asc_lon, is_day = planets['Asc']['lon'], is_day_chart(planets)
    sun_lon, moon_lon = planets['Sun']['lon'], planets['Moon']['lon']
    planets['Fortune'] = {'lon': (asc_lon + (moon_lon - sun_lon if is_day else sun_lon - moon_lon)) % 360, 'is_retro': False}
    for p in planets: planets[p]['house'] = determine_house(planets[p]['lon'], asc_lon)

    aspects = get_aspects(planets)
    
    # --- 修改部分：调用 star_calc 进行恒星计算 ---
    star_raw_data = get_star_longitudes(ts, t)
    star_aspects, star_stats = calculate_star_conjunctions_and_stats(planets, star_raw_data, orb=1.0)
    
    p_rows = "".join([f"<tr><td>{p}</td><td>{get_zodiac_sign(d['lon'])[0]}</td><td>{int(get_zodiac_sign(d['lon'])[1])}°</td><td>{d.get('house', '-')}</td></tr>" for p, d in planets.items()])
    a_rows = "".join([f"<tr><td>{a['p1']}</td><td>{a['p2']}</td><td style='color:{ASPECT_COLORS.get(a['type'], 'black')}; font-weight:bold'>{a['type']}</td><td>{a['diff']}°</td></tr>" for a in aspects])
    c_rows = "".join([get_classical_row(h, asc_lon, planets, is_day) for h in range(1, 13)])
    
    # 构建恒星表格行
    s_rows = ""
    if star_aspects:
        for sa in star_aspects:
            s_rows += f"<tr><td>{sa['planet']}</td><td>{sa['star']}</td><td>{sa['orb']:.2f}°</td><td>{sa['meaning']}</td></tr>"
    else:
        s_rows = "<tr><td colspan='4'>No major fixed star conjunctions found (<1°).</td></tr>"

    # 构建统计栏 HTML (根据截图样式)
    stats_html = f"""
    <div class="stats-bar">
        <span>👑 ROYAL STARS: {star_stats['royal']}</span>
        <span>✨ BEHENIAN STARS: {star_stats['behenian']}</span>
        <span>⚔️ PRACTICAL STARS: {star_stats['practical']}</span>
        <span>📚 ROBSON STARS: {star_stats['robson']}</span>
    </div>
    """

    html = f"""<!DOCTYPE html><html><head><meta charset="UTF-8">
    <style>
        body{{font-family:sans-serif;background:#f4f7f6;padding:20px;color:#333}}
        .card{{background:white;max-width:1400px;margin:auto;padding:30px;border-radius:15px;box-shadow:0 4px 15px rgba(0,0,0,0.1)}}
        .header{{border-bottom:2px solid #333;margin-bottom:20px}}
        .flex{{display:flex;gap:30px;flex-wrap:wrap}}
        .chart{{flex:1;min-width:400px}}
        svg{{width:100%;height:auto;overflow:visible}}
        .tables{{flex:2;min-width:500px}}
        table{{width:100%;border-collapse:collapse;margin-top:10px;font-size:11px}}
        th,td{{border:1px solid #ddd;padding:6px 4px;text-align:center}}
        th{{background:#f8f8f8; color:#666}}
        .section-title{{font-size:14px;font-weight:bold;margin-top:20px;color:#444;border-left:4px solid #4B0082;padding-left:8px}}
        
        /* 统计栏样式 */
        .stats-bar {{
            display: flex;
            justify-content: space-around;
            background: #f8f9fa;
            padding: 10px;
            border-radius: 8px;
            margin-bottom: 10px;
            border: 1px solid #eee;
            font-weight: bold;
            flex-wrap: wrap;
        }}
        .stats-bar span {{ font-size: 14px; }}
        
        /* 恒星表格表头特殊颜色 */
        .star-table th {{ background: #e9ecef; color: #333; }}
    </style></head>
    <body>
    <div class="card">
        <div class="header">
            <h2>{user_name} - Classical Analysis</h2>
            <p>{localized_dt.strftime('%Y-%m-%d %H:%M')} ({tz_str}) | {formatted_location}</p>
        </div>
        
        <div class="section-title">Classical Lord Evaluation</div>
        <table>
            <thead><tr><th>House</th><th>Cusp</th><th>Ruler</th><th>Pos H</th><th>Pos Sign</th><th>Deg</th><th>State</th><th>Own Term</th><th>Own Face</th><th>Own Trip</th><th>Combust</th><th>Retro</th><th>Mut. Rec</th><th>Mut. Rej</th><th>Rej By</th><th>Rec By</th><th>Pattern</th></tr></thead>
            <tbody>{c_rows}</tbody>
        </table>

        <div class="flex">
            <div class="chart">
                <svg viewBox="0 0 800 800">{create_pro_svg(planets, aspects)}</svg>
                <div class="section-title" style="margin-top: 20px;">Major Aspects</div>
                <table>
                    <thead><tr><th>P1</th><th>P2</th><th>Type</th><th>Orb</th></tr></thead>
                    <tbody>{a_rows}</tbody>
                </table>
            </div>
            <div class="tables">
                <div class="section-title">Modern Placements</div>
                <table>
                    <thead><tr><th>Planet</th><th>Sign</th><th>Deg</th><th>House</th></tr></thead>
                    <tbody>{p_rows}</tbody>
                </table>
                <div class="section-title" style="margin-top: 20px;">Fixed Star Conjunction</div>
                {stats_html}
                <table class="star-table">
                    <thead><tr><th>P1</th><th>P2</th><th>Orb</th><th>Meaning</th></tr></thead>
                    <tbody>{s_rows}</tbody>
                </table>
            </div>
        </div>
    </div>
    </body></html>"""
    
    filename = f"report_{user_name}.html"
    with open(filename, "w", encoding="utf-8") as f: 
        f.write(html)
    print(f"\nSuccess! File generated: {filename}")
    
    # 获取绝对路径，避免路径问题
    report_path = os.path.abspath(filename)

    # === 修复后的 AI 分析调用段 ===
    '''
    if HAS_AI:
        try:
            # 只有当 ai_analysis 模块导入成功且函数存在时才执行
            print("💡 正在深度解读第1宫...")
            generate_and_append_analysis_1(report_path)
            print("💡 正在深度解读第2宫...")
            generate_and_append_analysis_2(report_path)
            print("💡 正在深度解读第3宫...")
            generate_and_append_analysis_3(report_path)
            print("💡 正在深度解读第4宫...")
            generate_and_append_analysis_4(report_path)
            print("💡 正在深度解读第5宫...")
            generate_and_append_analysis_5(report_path)
            print("💡 正在深度解读第6宫...")
            generate_and_append_analysis_6(report_path)
            print("💡 正在深度解读第7宫...")
            generate_and_append_analysis_7(report_path)
        except Exception as e:
            print(f"⚠️ AI 分析未能完成（但不影响报告生成）: {e}")
    # ====================================
    '''

    # 确保无论 AI 是否成功，都会打开报告文件
    webbrowser.open('file://' + report_path)

if __name__ == "__main__":
    generate_report()