import math
from constants import *

def get_face_ruler(sign, degree):
    sign_idx = SIGNS.index(sign)
    decan = int(degree // 10)
    if decan > 2: decan = 2
    start_idx = (sign_idx * 3) % 7
    face_idx = (start_idx + decan) % 7
    return CHALDEAN_ORDER[face_idx]

def get_term_ruler(sign, degree):
    for planet, limit in EGYPTIAN_TERMS[sign]:
        if degree < limit:
            return planet
    return None

def determine_house(lon, asc_lon):
    diff = (lon - asc_lon) % 360
    return int(diff // 30) + 1

def pol2cart(cx, cy, radius, angle_deg):
    angle_rad = math.radians(180 - angle_deg)
    return cx + radius * math.cos(angle_rad), cy + radius * math.sin(angle_rad)

def get_zodiac_sign(lon):
    idx = int((lon % 360) // 30)
    deg = lon % 30
    return SIGNS[idx], deg

def is_day_chart(planets):
    sun_lon = planets['Sun']['lon']
    asc_lon = planets['Asc']['lon']
    h = determine_house(sun_lon, asc_lon)
    return h >= 7

def get_aspects(planets):
    aspects = []
    p_names = list(planets.keys())
    check_list = ['Sun', 'Moon', 'Mercury', 'Venus', 'Mars', 'Jupiter', 'Saturn', 'Uranus', 'Neptune', 'Pluto', 'Asc', 'Node', 'Fortune']
    check_list.extend([f'House {i}' for i in range(1, 13)])
    orb_map = {'Conjunction': (0, 8), 'Opposition': (180, 8), 'Trine': (120, 8), 'Square': (90, 8), 'Sextile': (60, 6)}
    
    for i in range(len(p_names)):
        for j in range(i + 1, len(p_names)):
            p1, p2 = p_names[i], p_names[j]
            if p1 not in check_list or p2 not in check_list: continue
            if p1.startswith('House ') and p2.startswith('House '): continue
            lon1, lon2 = planets[p1]['lon'], planets[p2]['lon']
            diff = abs(lon1 - lon2)
            if diff > 180: diff = 360 - diff
            for name, (angle, orb) in orb_map.items():
                if abs(diff - angle) <= orb:
                    aspects.append({'p1': p1, 'p2': p2, 'type': name, 'diff': round(abs(diff-angle), 2)})
    return aspects

def check_aspect(p1_name, p2_name, planets, orb=8):
    """
    检查两颗星之间是否存在古典相位 (0, 60, 90, 120, 180)
    用于判定接纳是否“有效”
    """
    p1_lon = planets[p1_name]['lon']
    p2_lon = planets[p2_name]['lon']
    
    diff = abs(p1_lon - p2_lon)
    if diff > 180:
        diff = 360 - diff
        
    # 古典五大相位
    aspects = {
        'Conjunction': 0,
        'Sextile': 60,
        'Square': 90,
        'Trine': 120,
        'Opposition': 180
    }
    
    for name, angle in aspects.items():
        if abs(diff - angle) <= orb:
            return name
    return None

def get_dignities_at_position(sign, degree, is_day):
    domicile = CLASSICAL_RULERS[sign]
    exalt = EXALTATIONS.get(sign)
    element = SIGN_ELEMENTS[sign]
    triplicity = TRIPLICITIES[element]['Day' if is_day else 'Night']
    term = get_term_ruler(sign, degree)
    face = get_face_ruler(sign, degree)
    return {'domicile': domicile, 'exalt': exalt, 'trip': triplicity, 'term': term, 'face': face}

def get_debilities_at_position(sign):
    detriment = DETRIMENTS.get(sign)
    fall = FALLS.get(sign)
    debilities = []
    if detriment and detriment != '-': debilities.append(detriment)
    if fall and fall != '-': debilities.append(fall)
    return debilities

def calculate_mutual_reception_rejection(p_name, p_data, all_planets, is_day):
    if p_name not in ['Sun', 'Moon', 'Mercury', 'Venus', 'Mars', 'Jupiter', 'Saturn']:
        return "-", "-"
    my_lon = p_data['lon']
    my_sign, my_deg = get_zodiac_sign(my_lon)
    host_dignities = get_dignities_at_position(my_sign, my_deg, is_day)
    host_debilities = get_debilities_at_position(my_sign)
    mut_rec_list, mut_rej_list = [], []

    for other_p, other_data in all_planets.items():
        if other_p == p_name or other_p not in ['Sun', 'Moon', 'Mercury', 'Venus', 'Mars', 'Jupiter', 'Saturn']:
            continue
        other_lon = other_data['lon']
        other_sign, other_deg = get_zodiac_sign(other_lon)
        other_has_dignity_here = False
        if host_dignities['domicile'] == other_p: other_has_dignity_here = True
        elif host_dignities['exalt'] == other_p: other_has_dignity_here = True
        elif host_dignities['trip'] == other_p: other_has_dignity_here = True
        elif host_dignities['term'] == other_p: other_has_dignity_here = True

        if other_has_dignity_here:
            other_sign_dignities = get_dignities_at_position(other_sign, other_deg, is_day)
            if any(other_sign_dignities[k] == p_name for k in ['domicile', 'exalt', 'trip', 'term']):
                mut_rec_list.append(other_p)

        if other_p in host_debilities:
            other_sign_debilities = get_debilities_at_position(other_sign)
            if p_name in other_sign_debilities:
                mut_rej_list.append(other_p)

    return (", ".join(mut_rec_list) if mut_rec_list else "-", ", ".join(mut_rej_list) if mut_rej_list else "-")

def get_advanced_reception(p_name, all_planets, is_day):
    """
    更专业的接纳/互溶判定，增加了相位检查和等级评分
    """
    p_data = all_planets[p_name]
    my_lon = p_data['lon']
    my_sign, my_deg = get_zodiac_sign(my_lon)
    
    # 获取我所在位置的各级主人
    dignities_at_my_pos = get_dignities_at_position(my_sign, my_deg, is_day)
    debilities_at_my_pos = get_debilities_at_position(my_sign)
    
    reception_results = []

    for other_p, other_data in all_planets.items():
        if other_p == p_name or other_p not in ['Sun', 'Moon', 'Mercury', 'Venus', 'Mars', 'Jupiter', 'Saturn']:
            continue
            
        # 1. 检查是否有相位 (必须具备相位，接纳才真正有力)
        # 假设你已经有一个函数 check_aspect(p1, p2) 返回相位类型或 None
        aspect = check_aspect(p_name, other_p, all_planets) 
        
        # 2. 检查接纳等级
        level = 0
        reception_type = None
        
        if dignities_at_my_pos['domicile'] == other_p:
            level = 3 # 庙接纳：最高等级
            reception_type = "Domicile Reception"
        elif dignities_at_my_pos['exalt'] == other_p:
            level = 2 # 旺接纳：极高等级
            reception_type = "Exaltation Reception"
        elif dignities_at_my_pos['trip'] == other_p:
            level = 1 # 三分接纳：中等等级
            reception_type = "Triplicity Reception"
            
        # 3. 检查互拒 (Detriment/Fall)
        is_rejected = False
        if other_p in debilities_at_my_pos:
            is_rejected = True

        if reception_type:
            # 记录结果，区分“有效接纳”和“暗中支持”
            res = {
                "from": other_p,
                "type": reception_type,
                "level": level,
                "has_aspect": aspect is not None,
                "aspect_name": aspect,
                "is_rejected": is_rejected
            }
            reception_results.append(res)
            
    return reception_results