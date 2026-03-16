import os
import webbrowser
from constants import *
from utils import *
from engine import get_astronomical_data
# Import functionality from planets.py
from planets import get_star_longitudes, check_star_aspects
# 新增：引入星体计算工具
from star_calc import calculate_star_conjunctions_and_stats
# 新增：引入自研打分系统
from scoring import calculate_essential_score, calculate_accidental_score, calculate_diplomacy, get_aspects_for_planet
from draw_chart import create_pro_svg

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

def generate_detailed_html(planets, asc_lon, is_day):
    """
    生成详细的克重和宫位分析 HTML (涵盖所有12宫)
    """
    html_sections = []
    
    # 获取上升星座索引，用于计算宫头
    asc_sign_name, _ = get_zodiac_sign(asc_lon)
    asc_idx = SIGNS.index(asc_sign_name)
    
    # 按宫位分组星体 (仅限实际星体)
    house_planets = {i: [] for i in range(1, 13)}
    check_list = ['Sun', 'Moon', 'Mercury', 'Venus', 'Mars', 'Jupiter', 'Saturn', 'Uranus', 'Neptune', 'Pluto', 'Fortune', 'Node']
    for p_name in check_list:
        if p_name not in planets: continue
        p_data = planets[p_name]
        h = determine_house(p_data['lon'], asc_lon)
        house_planets[h].append(p_name)
        
    for h_num in range(1, 13):
        # 1. 宫头信息
        cusp_sign = SIGNS[(asc_idx + h_num - 1) % 12]
        ruler_name = CLASSICAL_RULERS[cusp_sign]
        
        # 宫主星飞宫
        if ruler_name in planets:
            ruler_lon = planets[ruler_name]['lon']
            ruler_flying_house = determine_house(ruler_lon, asc_lon)
            ruler_info_str = f"宫主星: {ruler_name} ({h_num}宫主) 飞入 {ruler_flying_house}宫"
        else:
            ruler_info_str = f"宫主星: {ruler_name} (数据缺失)"
        
        section = [f"""
        <details class="detailed-house">
            <summary class="house-header" style="cursor: pointer; outline: none;">
                第 {h_num} 宫 <span style="font-size:14px; color:#888; font-weight:normal; margin-left:10px;">▼ 点击展开/收缩</span>
            </summary>
            <div class="cusp-info">
                宫头: {cusp_sign} | {ruler_info_str}
            </div>
        """]
        
        # 2. 分析该宫位的守护星 (即使它不在该宫位)
        if ruler_name in planets:
            p_name = ruler_name
            p_data = planets[p_name]
            p_lon = p_data['lon']
            p_sign, p_deg = get_zodiac_sign(p_lon)
            
            essential = calculate_essential_score(p_name, p_sign, p_deg, is_day)
            accidental = calculate_accidental_score(p_name, p_data, planets, asc_lon)
            diplomacy = calculate_diplomacy(p_name, planets, is_day)
            total_score = essential['score'] + accidental['score'] + diplomacy['score']
            
            p_aspects = get_aspects_for_planet(p_name, planets)
            aspect_rows = "".join([f"<div>相位{i}: 对方星体: {asp['target']} | 对方宫位: {asp['target_house']} | 相位: {asp['type']} | 强度: {asp['orb']}° ({asp['intensity']}%)</div>" for i, asp in enumerate(p_aspects[:8], 1)])

            section.append(f"""
            <div class="planet-detail ruler-focus">
                <div class="planet-title">宫主星: {p_name} ({h_num}宫头守护)</div>
                <div>星体: {p_name}({h_num}宫头守护)</div>
                <div>落宫: {accidental['house']} | 星座: {p_sign} | 度数: {int(p_deg)}°{int((p_deg%1)*60)}'</div>
                <div class="score-line">先天分: 状态:{essential['status']} | 入界: {essential['in_term']} | 入面: {essential['in_face']} | 三分: {essential['in_trip']} | 先天分: {essential['score']:+g}</div>
                <div class="score-line">后天分: 落宫: {accidental['house_score']:+g} | 燃烧: {accidental['is_combust']} | 逆行: {accidental['is_retro']} | 燃烧径: {accidental['is_via_combusta']} | 后天分: {accidental['score']:+g}</div>
                <div class="score-line">外交: 互容: {diplomacy['mut_rec']} | 互拒: {diplomacy['mut_rej']} | 被拒: {diplomacy['rej_by']} | 被接纳: {diplomacy['accepted_by']} | 外交分: {diplomacy['score']:+g}</div>
                <div class="score-line total-score">先天后天总分: {total_score:+g} | 格局: 无(+0.0) | 重要性: {total_score:+g}</div>
                <div class="aspect-details">
                    {aspect_rows if aspect_rows else "无重大相位"}
                </div>
            </div>
            """)

        # 3. 分析该宫位内的其他星体
        for p_name in house_planets[h_num]:
            if p_name == ruler_name: continue # 避免重复分析
            
            p_data = planets[p_name]
            p_lon = p_data['lon']
            p_sign, p_deg = get_zodiac_sign(p_lon)
            
            essential = calculate_essential_score(p_name, p_sign, p_deg, is_day)
            accidental = calculate_accidental_score(p_name, p_data, planets, asc_lon)
            diplomacy = calculate_diplomacy(p_name, planets, is_day)
            total_score = essential['score'] + accidental['score'] + diplomacy['score']
            
            p_aspects = get_aspects_for_planet(p_name, planets)
            aspect_rows = "".join([f"<div>相位{i}: 对方星体: {asp['target']} | 对方宫位: {asp['target_house']} | 相位: {asp['type']} | 强度: {asp['orb']}° ({asp['intensity']}%)</div>" for i, asp in enumerate(p_aspects[:8], 1)])

            section.append(f"""
            <div class="planet-detail">
                <div class="planet-title">宫内星体: {p_name}</div>
                <div>星体: {p_name}</div>
                <div>落宫: {accidental['house']} | 星座: {p_sign} | 度数: {int(p_deg)}°{int((p_deg%1)*60)}'</div>
                <div class="score-line">先天分: 状态:{essential['status']} | 入界: {essential['in_term']} | 入面: {essential['in_face']} | 三分: {essential['in_trip']} | 先天分: {essential['score']:+g}</div>
                <div class="score-line">后天分: 落宫: {accidental['house_score']:+g} | 燃烧: {accidental['is_combust']} | 逆行: {accidental['is_retro']} | 燃烧径: {accidental['is_via_combusta']} | 后天分: {accidental['score']:+g}</div>
                <div class="score-line">外交: 互容: {diplomacy['mut_rec']} | 互拒: {diplomacy['mut_rej']} | 被拒: {diplomacy['rej_by']} | 被接纳: {diplomacy['accepted_by']} | 外交分: {diplomacy['score']:+g}</div>
                <div class="score-line total-score">先天后天总分: {total_score:+g} | 格局: 无(+0.0) | 重要性: {total_score:+g}</div>
                <div class="aspect-details">
                    {aspect_rows if aspect_rows else "无重大相位"}
                </div>
            </div>
            """)
            
        section.append("</details>")
        html_sections.append("".join(section))
        
    return "".join(html_sections)

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
    
    star_raw_data = get_star_longitudes(ts, t)
    star_aspects, star_stats = calculate_star_conjunctions_and_stats(planets, star_raw_data, orb=1.0)
    
    p_rows = "".join([f"<tr><td>{p}</td><td>{get_zodiac_sign(d['lon'])[0]}</td><td>{int(get_zodiac_sign(d['lon'])[1])}°</td><td>{d.get('house', '-')}</td></tr>" for p, d in planets.items()])
    a_rows = "".join([f"<tr><td>{a['p1']}</td><td>{a['p2']}</td><td style='color:{ASPECT_COLORS.get(a['type'], 'black')}; font-weight:bold'>{a['type']}</td><td>{a['diff']}°</td></tr>" for a in aspects])
    c_rows = "".join([get_classical_row(h, asc_lon, planets, is_day) for h in range(1, 13)])
    
    s_rows = ""
    if star_aspects:
        for sa in star_aspects:
            s_rows += f"<tr><td>{sa['planet']}</td><td>{sa['star']}</td><td>{sa['orb']:.2f}°</td><td>{sa['meaning']}</td></tr>"
    else:
        s_rows = "<tr><td colspan='4'>No major fixed star conjunctions found (<1°).</td></tr>"

    stats_html = f"""
    <div class="stats-bar">
        <span>👑 ROYAL STARS: {star_stats['royal']}</span>
        <span>✨ BEHENIAN STARS: {star_stats['behenian']}</span>
        <span>⚔️ PRACTICAL STARS: {star_stats['practical']}</span>
        <span>📚 ROBSON STARS: {star_stats['robson']}</span>
    </div>
    """

    detailed_html = generate_detailed_html(planets, asc_lon, is_day)

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
        .section-title{{font-size:16px;font-weight:bold;margin-top:30px;color:#444;border-left:5px solid #4B0082;padding-left:10px;background:#eee;padding:5px 10px}}
        
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
        .star-table th {{ background: #e9ecef; color: #333; }}

        .detailed-house {{ border: 1px solid #ddd; padding: 15px; margin-top: 20px; border-radius: 8px; background: #fff; }}
        .house-header {{ font-size: 18px; font-weight: bold; color: #4B0082; border-bottom: 2px solid #4B0082; padding-bottom: 5px; margin-bottom: 10px; }}
        .cusp-info {{ font-size: 14px; font-weight: bold; background: #f0f0f0; padding: 5px 10px; border-radius: 4px; margin-bottom: 15px; }}
        .planet-detail {{ border-left: 3px solid #666; padding-left: 15px; margin-bottom: 20px; font-size: 13px; line-height: 1.6; }}
        .planet-title {{ font-size: 15px; font-weight: bold; color: #333; margin-top: 10px; }}
        .score-line {{ color: #555; }}
        .total-score {{ font-weight: bold; color: #d32f2f; font-size: 14px; margin-top: 3px; border-top: 1px dashed #ccc; padding-top: 3px; }}
        .aspect-details {{ font-size: 12px; color: #777; margin-top: 5px; font-style: italic; }}
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
                <div class="section-title">Major Aspects</div>
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
                <div class="section-title">Fixed Star Conjunction</div>
                {stats_html}
                <table class="star-table">
                    <thead><tr><th>P1</th><th>P2</th><th>Orb</th><th>Meaning</th></tr></thead>
                    <tbody>{s_rows}</tbody>
                </table>
            </div>
        </div>

        <div class="section-title">Detailed Calculation & House Analysis</div>
        {detailed_html}
    </div>
    </body></html>"""
    
    filename = f"report_{user_name}.html"
    with open(filename, "w", encoding="utf-8") as f: 
        f.write(html)
    print(f"\nSuccess! File generated: {filename}")
    
    report_path = os.path.abspath(filename)
    webbrowser.open('file://' + report_path)

if __name__ == "__main__":
    generate_report()