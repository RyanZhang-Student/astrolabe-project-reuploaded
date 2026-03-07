import math
from constants import *
from utils import get_zodiac_sign, get_dignities_at_position, get_debilities_at_position, check_aspect, determine_house

def calculate_essential_score(planet, sign, degree, is_day):
    """
    计算先天分数（Essential Dignities）:
    庙 (Domicile): +5
    旺 (Exaltation): +4
    三分 (Triplicity): +3
    界 (Term): +2
    面 (Face): +1
    失势 (Detriment): -5
    落陷 (Fall): -4
    游走 (Peregrine): -5 (如果没有以上任何正面得位)
    """
    dignities = get_dignities_at_position(sign, degree, is_day)
    debilities = get_debilities_at_position(sign)
    
    score = 0
    status = []
    
    is_domicile = dignities['domicile'] == planet
    is_exalted = dignities['exalt'] == planet
    is_trip = dignities['trip'] == planet
    is_term = dignities['term'] == planet
    is_face = dignities['face'] == planet
    
    if is_domicile:
        score += 5
        status.append("庙")
    if is_exalted:
        score += 4
        status.append("旺")
    if is_trip:
        score += 3
    if is_term:
        score += 2
    if is_face:
        score += 1
        
    is_detriment = DETRIMENTS.get(sign) == planet
    is_fall = FALLS.get(sign) == planet
    
    if is_detriment:
        score -= 5
        status.append("失")
    if is_fall:
        score -= 4
        status.append("落")
        
    # 游走判定：没有任何正面得位，且不在自己的陷弱位
    if not (is_domicile or is_exalted or is_trip or is_term or is_face) and not (is_detriment or is_fall):
        # 严格来说，古典黄金黎明或中世纪标准有些许差异，这里按常见扣分
        # score -= 5 
        status.append("平")

    return {
        "score": score,
        "status": status[0] if status else "平",
        "in_term": "是" if is_term else "否",
        "in_face": "是" if is_face else "否",
        "in_trip": "是" if is_trip else "否"
    }

def calculate_accidental_score(planet_name, p_data, all_planets, asc_lon):
    """
    计算后天分数（Accidental Dignities）:
    落宫 (House placement): 1,4,7,10 (+5); 2,5,8,11 (+3); 3,6,9,12 (+1) 
    (注意：不同流派对凶宫扣分不同，用户示例中 8宫是 -5)
    燃烧 (Combust): -5 (与太阳 8.5度内)
    逆行 (Retro): -5
    """
    lon = p_data['lon']
    house = determine_house(lon, asc_lon)
    is_retro = p_data.get('is_retro', False)
    
    score = 0
    
    # 落宫分数 (简单粗暴版，对应用户示例 8宫 -5)
    # 典型：1,4,7,10(+5), 2,5,11(+3), 3,9(+2), 6,8,12(-5)
    house_scores = {
        1: 5, 2: 3, 3: 2, 4: 5, 5: 3, 6: -5, 
        7: 5, 8: -5, 9: 2, 10: 5, 11: 3, 12: -5
    }
    house_score = house_scores.get(house, 0)
    score += house_score
    
    # 燃烧判定
    sun_lon = all_planets['Sun']['lon']
    dist_to_sun = abs(lon - sun_lon)
    if dist_to_sun > 180: dist_to_sun = 360 - dist_to_sun
    
    is_combust = False
    if planet_name != 'Sun' and dist_to_sun < 8.5:
        is_combust = True
        score -= 5
        
    # 逆行
    if is_retro:
        score -= 5
        
    # 燃烧径 (Via Combusta): 天秤15度 - 天蝎15度
    is_via_combusta = False
    if 195 <= lon <= 225:
        is_via_combusta = True
        score -= 5

    return {
        "score": score,
        "house": f"{house}宫",
        "house_score": house_score,
        "is_combust": "是" if is_combust else "否",
        "is_retro": "是" if is_retro else "否",
        "is_via_combusta": "是" if is_via_combusta else "否"
    }

def calculate_diplomacy(planet_name, all_planets, is_day):
    """
    外交分 (Diplomacy): 互容互拒等
    """
    p_data = all_planets[planet_name]
    my_lon = p_data['lon']
    my_sign, my_deg = get_zodiac_sign(my_lon)
    
    dignities_here = get_dignities_at_position(my_sign, my_deg, is_day)
    debilities_here = get_debilities_at_position(my_sign)
    
    mut_rec = [] # 互容
    mut_rej = [] # 互拒
    rej_by = []  # 被拒
    accepted_by = [] # 被接纳
    
    diplomacy_score = 0
    
    for other_name, other_data in all_planets.items():
        if other_name == planet_name or other_name not in CLASSICAL_RULERS.values():
            continue
            
        other_lon = other_data['lon']
        other_sign, other_deg = get_zodiac_sign(other_lon)
        other_dignities = get_dignities_at_position(other_sign, other_deg, is_day)
        other_debilities = get_debilities_at_position(other_sign)
        
        # 我在对方的庙/旺位置 -> 对方接纳我
        is_i_in_others_dignity = (other_dignities['domicile'] == planet_name or 
                                 other_dignities['exalt'] == planet_name)
        
        # 对方在我的庙/旺位置 -> 我接纳对方
        is_other_in_my_dignity = (dignities_here['domicile'] == other_name or 
                                 dignities_here['exalt'] == other_name)
        
        # 我在对方的陷/弱位置 -> 对方排斥我 (被拒)
        is_i_in_others_debility = planet_name in other_debilities
        
        # 对方在我的陷/弱位置 -> 我排斥对方 (互拒的一部分)
        is_other_in_my_debility = other_name in debilities_here
        
        if is_i_in_others_dignity and is_other_in_my_dignity:
            mut_rec.append(other_name)
            diplomacy_score += 4 # 互容加分
            
        if is_i_in_others_debility and is_other_in_my_debility:
            mut_rej.append(other_name)
            diplomacy_score -= 4 # 互拒扣分
            
        if is_i_in_others_debility and not is_other_in_my_debility:
            # 简化逻辑：被拒
            aspect = check_aspect(planet_name, other_name, all_planets)
            if aspect:
                rej_by.append(f"{other_name}({aspect[:1]})")
                diplomacy_score -= 0.4
                
        if is_i_in_others_dignity and not is_other_in_my_dignity:
            accepted_by.append(other_name)
            diplomacy_score += 0.4
            
    return {
        "score": round(diplomacy_score, 1),
        "mut_rec": ", ".join(mut_rec) if mut_rec else "无",
        "mut_rej": ", ".join(mut_rej) if mut_rej else "无",
        "rej_by": ", ".join(rej_by) if rej_by else "无",
        "accepted_by": ", ".join(accepted_by) if accepted_by else "无"
    }

def get_aspects_for_planet(planet_name, all_planets):
    """
    相位详情，包含强度计算
    强度 = (1 - orb/max_orb) * 100%
    """
    results = []
    p1_lon = all_planets[planet_name]['lon']
    
    # 常用许容度
    orb_map = {'Conjunction': (0, 10), 'Opposition': (180, 10), 'Trine': (120, 8), 'Square': (90, 8), 'Sextile': (60, 6)}
    # 映射中文
    name_map = {'Conjunction': '合相', 'Opposition': '对分', 'Trine': '三分', 'Square': '刑相位', 'Sextile': '六合相位'}
    
    for other_name, other_data in all_planets.items():
        if other_name == planet_name: continue
        
        p2_lon = other_data['lon']
        diff = abs(p1_lon - p2_lon)
        if diff > 180: diff = 360 - diff
        
        for asp_type, (angle, max_orb) in orb_map.items():
            orb = abs(diff - angle)
            if orb <= max_orb:
                intensity = (1 - orb/max_orb) * 100
                results.append({
                    "target": other_name,
                    "target_house": determine_house(p2_lon, all_planets['Asc']['lon']),
                    "type": f"{name_map[asp_type]}({angle}°)",
                    "orb": round(orb, 2),
                    "intensity": round(intensity, 1)
                })
                
    return results
