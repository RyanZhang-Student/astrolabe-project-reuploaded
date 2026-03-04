# star_calculator.py
from planets import ROYAL_STARS, BEHENIAN_STARS, PRACTICAL_STARS

def calculate_star_conjunctions_and_stats(planets_data, stars_data, orb=1.0):
    """
    输入: 
        planets_data: 包含行星经度的字典 (来自 engine.py/planets.py)
        stars_data: 包含恒星经度和名字的列表 (来自 planets.py get_star_longitudes)
        orb: 容许度 (默认 1.0 度)
    
    输出:
        conjunctions: 合相列表
        stats: 统计数据 (Royal, Behenian, Practical, Robson)
    """
    
    conjunctions = []
    
    # 初始化统计计数器
    stats = {
        "royal": 0,
        "behenian": 0,
        "practical": 0,
        "robson": 0
    }

    # 遍历所有行星
    for p_name, p_info in planets_data.items():
        # 如果你不想算虚点（如 Asc, MC），可以在这里加 if p_name in [...]: continue
        # 这里默认计算所有传入的星体
        
        p_lon = p_info['lon']

        # 遍历所有恒星
        for star in stars_data:
            s_name = star['name']
            s_lon = star['longitude']
            
            # 计算距离 (处理 360/0 度交界问题)
            diff = abs(p_lon - s_lon)
            if diff > 180:
                diff = 360 - diff
            
            # 判断是否合相
            if diff <= orb:
                # 1. 记录合相数据
                conjunctions.append({
                    "planet": p_name,
                    "star": s_name,
                    "orb": diff,
                    "meaning": star['meaning']
                })
                
                # 2. 进行分类统计
                
                # Robson: 所有合相都算
                stats["robson"] += 1
                
                # 检查 Royal Stars (模糊匹配，防止 "Difda (Deneb)" 匹配不上 "Difda")
                if any(r_star in s_name for r_star in ROYAL_STARS):
                    stats["royal"] += 1
                    
                # 检查 Behenian Stars
                if any(b_star in s_name for b_star in BEHENIAN_STARS):
                    stats["behenian"] += 1
                    
                # 检查 Practical Stars
                if any(p_star in s_name for p_star in PRACTICAL_STARS):
                    stats["practical"] += 1

    return conjunctions, stats