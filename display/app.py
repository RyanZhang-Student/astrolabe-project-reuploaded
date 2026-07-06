import os
import sys
import json
import base64
import datetime
import shutil
from flask import Flask, render_template, request, jsonify, send_from_directory, session
from dotenv import load_dotenv

load_dotenv()

# Add project root to sys.path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOGIC_DIR = os.path.join(BASE_DIR, 'logic')
RESULTS_DIR = os.path.join(BASE_DIR, 'results')

if not os.path.exists(RESULTS_DIR):
    os.makedirs(RESULTS_DIR)

sys.path.append(BASE_DIR)
sys.path.append(LOGIC_DIR)
AI_ANALYSIS_DIR = os.path.join(BASE_DIR, 'ai_analysis')
sys.path.append(AI_ANALYSIS_DIR)
CHATBOT_DIR = os.path.join(BASE_DIR, 'chatbot')
sys.path.append(CHATBOT_DIR)
FULL_ANALYSIS_DIR = os.path.join(BASE_DIR, 'full_analysis')
sys.path.append(FULL_ANALYSIS_DIR)

from engine import get_astronomical_data
from utils import is_day_chart, get_zodiac_sign, determine_house, SIGNS, CLASSICAL_RULERS, EXALTATIONS, DETRIMENTS, FALLS, get_dignities_at_position, get_debilities_at_position, get_advanced_reception, calculate_mutual_reception_rejection, get_aspects
from planets import get_star_longitudes
from star_calc import calculate_star_conjunctions_and_stats
from scoring import calculate_essential_score, calculate_accidental_score, calculate_diplomacy, get_aspects_for_planet
from draw_chart import create_pro_svg
import main as astrolabe_main
import analyzer as ai_analyzer
import chatbot1
import chatbot2
import pdf_generator
from account.auth import auth_bp, init_oauth

app = Flask(__name__, static_folder='.', static_url_path='', template_folder='.')
app.secret_key = os.getenv('SECRET_KEY', 'default_secret')
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['SESSION_COOKIE_SECURE'] = False

init_oauth(app)
app.register_blueprint(auth_bp)

# Load cities once for autocomplete
CITIES_DATA = []
try:
    cities_file = os.path.join(LOGIC_DIR, 'world_cities.json')
    with open(cities_file, 'r', encoding='utf-8') as f:
        CITIES_DATA = json.load(f)
except Exception as e:
    print(f"Warning: Could not load world_cities.json: {e}")

from flask import make_response

@app.route('/')
def index():
    response = make_response(render_template('index.html', user=session.get('user')))
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

@app.route('/api/cities')
def api_cities():
    query = request.args.get('q', '').strip().upper()
    if not query:
        return jsonify([])
    
    matches = []
    # Find up to 3 matches
    for city in CITIES_DATA:
        if city['name'].upper().startswith(query):
            matches.append({'name': city['name'], 'country': city['country']})
            if len(matches) == 3:
                break
                
    # If less than 3, fallback to contains
    if len(matches) < 3:
        for city in CITIES_DATA:
            name_upper = city['name'].upper()
            if query in name_upper and not name_upper.startswith(query):
                matches.append({'name': city['name'], 'country': city['country']})
                if len(matches) == 3:
                    break
                    
    return jsonify(matches)

@app.route('/results/<path:filename>')
def serve_results(filename):
    return send_from_directory(RESULTS_DIR, filename)

@app.route('/calculate', methods=['POST'])
def calculate():
    data = request.json
    user_name = data.get('name', 'USER').upper()
    gender = data.get('gender') # Male, Female, Other
    dob_input = data.get('dob') # YYYY-MMDD-HHMM
    location_input = data.get('location') # CITY-COUNTRY
    
    # Use the same logic as logic/main.py
    data_tuple = get_astronomical_data(dob_input, location_input)
    if data_tuple[0] is None:
        return jsonify({'error': data_tuple[1]}), 400
        
    planets, meta, time_data = data_tuple
    localized_dt, tz_str, formatted_location = meta
    ts, t = time_data
    
    asc_lon, is_day = planets['Asc']['lon'], is_day_chart(planets)
    sun_lon, moon_lon = planets['Sun']['lon'], planets['Moon']['lon']
    planets['Fortune'] = {'lon': (asc_lon + (moon_lon - sun_lon if is_day else sun_lon - moon_lon)) % 360, 'is_retro': False}
    for h in range(1, 13):
        planets[f'House {h} cusp head'] = {'lon': (asc_lon + (h - 1) * 30) % 360, 'is_retro': False}
    for p in planets: planets[p]['house'] = determine_house(planets[p]['lon'], asc_lon)

    aspects = get_aspects(planets)
    star_raw_data = get_star_longitudes(ts, t)
    star_aspects, star_stats = calculate_star_conjunctions_and_stats(planets, star_raw_data, orb=1.0)
    
    if star_aspects:
        star_aspects.sort(key=lambda x: (
            1 if x.get('is_royal') else (2 if x.get('is_behenian') else (3 if x.get('is_practical') else 4)),
            x.get('orb', 999)
        ))

    # Helper functions for HTML generation (extracted from main.py)
    def get_orb_style(s):
        color = ""
        if s >= 90: color = "#B22222"
        elif s >= 60: color = "#FF8C00"
        elif s >= 30: color = "#B406BD"
        return f"style='font-weight:bold; color:{color}'" if color else "style='font-weight:bold'"

    p_rows = "".join([f"<tr><td>{p}</td><td>{get_zodiac_sign(d['lon'])[0]}</td><td>{int(get_zodiac_sign(d['lon'])[1])}°</td><td>{d.get('house', '-')}</td></tr>" for p, d in planets.items() if not p.startswith('House ')])
    a_rows = "".join([f"<tr><td>{a['p1']}</td><td>{a['p2']}</td><td style='color:{astrolabe_main.ASPECT_COLORS.get(a['type'], 'black')}; font-weight:bold'>{a['type']}</td><td {get_orb_style(a['strength'])}>{a['diff']}° ({a['strength']}%)</td></tr>" for a in aspects])
    
    # We need get_classical_row from main.py
    # Since it's not exported nicely, I'll use astrolabe_main.get_classical_row
    c_rows = "".join([astrolabe_main.get_classical_row(h, asc_lon, planets, is_day) for h in range(1, 13)])
    
    star_aspects_json = json.dumps(star_aspects) if star_aspects else "[]"
    
    def get_stat_span(count, label, category, title):
        if count > 0:
            return f'''<span class="clickable-stat" onclick="openStarModal('{category}', '{title}')">{label}: {count}</span>'''
        return f"<span>{label}: {count}</span>"

    stats_html = f"""
    <div class="stats-bar">
        {get_stat_span(star_stats['royal'], '👑 ROYAL STARS', 'is_royal', 'Royal Star Conjunctions')}
        {get_stat_span(star_stats['behenian'], '✨ BEHENIAN STARS', 'is_behenian', 'Behenian Star Conjunctions')}
        {get_stat_span(star_stats['practical'], '⚔️ PRACTICAL STARS', 'is_practical', 'Practical Star Conjunctions')}
        {get_stat_span(star_stats['robson'], '📚 ROBSON STARS', 'is_robson', 'Robson Star Conjunctions')}
    </div>
    """

    detailed_html = astrolabe_main.generate_detailed_html(planets, asc_lon, is_day)

    # Note: Use create_pro_svg from logic.draw_chart directly or through main
    svg_inner = create_pro_svg(planets, aspects)
    full_svg = f'<svg viewBox="0 0 800 800" xmlns="http://www.w3.org/2000/svg">{svg_inner}</svg>'
    svg_base64 = base64.b64encode(full_svg.encode('utf-8')).decode('utf-8')

    # Use the HTML template from main.py
    # (Copied here to avoid modifying main.py too much)
    html_template = f"""<!DOCTYPE html><html><head><meta charset="UTF-8">
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
        .stats-bar {{ display: flex; justify-content: space-around; background: #f8f9fa; padding: 10px; border-radius: 8px; margin-bottom: 10px; border: 1px solid #eee; font-weight: bold; flex-wrap: wrap; }}
        .stats-bar span {{ font-size: 14px; }}
        .clickable-stat {{ text-decoration: underline; cursor: pointer; color: #4B0082; }}
        .modal {{ display: none; position: fixed; z-index: 1000; left: 0; top: 0; width: 100%; height: 100%; overflow: auto; background-color: rgba(0,0,0,0.4); }}
        .modal-content {{ background-color: #fefefe; margin: 10% auto; padding: 20px; border: 1px solid #888; width: 80%; max-width: 600px; border-radius: 10px; box-shadow: 0 5px 15px rgba(0,0,0,0.3); }}
        .close-btn {{ color: #aaa; float: right; font-size: 28px; font-weight: bold; cursor: pointer; margin-top: -10px; }}
        .close-btn:hover, .close-btn:focus {{ color: black; text-decoration: none; cursor: pointer; }}
        #modalTitle {{ margin-top: 0; color: #4B0082; }}
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
            <p>{localized_dt.strftime('%Y-%m-%d %H:%M')} | {gender} | {formatted_location}</p>
        </div>
        <div class="section-title">Classical Lord Evaluation</div>
        <table>
            <thead><tr><th>House</th><th>Cusp</th><th>Ruler</th><th>Pos H</th><th>Pos Sign</th><th>Deg</th><th>State</th><th>Own Term</th><th>Own Face</th><th>Own Trip</th><th>Combust</th><th>Retro</th><th>Mut. Rec</th><th>Mut. Rej</th><th>Rej By</th><th>Rec By</th><th>Pattern</th></tr></thead>
            <tbody>{c_rows}</tbody>
        </table>
        <div class="flex">
            <div class="chart"><img src="data:image/svg+xml;base64,{svg_base64}" alt="Natal Chart Photo" style="width:100%; height:auto;" /></div>
            <div class="tables">
                <div class="section-title">Modern Placements</div>
                <table><thead><tr><th>Planet</th><th>Sign</th><th>Deg</th><th>House</th></tr></thead><tbody>{p_rows}</tbody></table>
            </div>
        </div>
        <div class="section-title">Fixed Star Conjunction</div>{stats_html}
        <div class="section-title">Major Aspects</div>
        <table><thead><tr><th>P1</th><th>P2</th><th>Type</th><th>Orb</th></tr></thead><tbody>{a_rows}</tbody></table>
        <div class="section-title">Detailed Calculation & House Analysis</div>{detailed_html}
    </div>
    <div id="starModal" class="modal"><div class="modal-content"><span class="close-btn" onclick="closeStarModal()">&times;</span><h3 id="modalTitle">Star Conjunctions</h3><table class="star-table"><thead><tr><th>Planet</th><th>Star</th><th>Orb</th><th>Meaning</th></tr></thead><tbody id="modalBody"></tbody></table></div></div>
    <script>
        window.starData = {star_aspects_json};
        function openStarModal(category, title) {{
            if (!window.starData || window.starData.length === 0) return;
            const tbody = document.getElementById('modalBody');
            tbody.innerHTML = '';
            const filtered = window.starData.filter(function(sa) {{ return sa[category]; }});
            if (filtered.length === 0) return;
            document.getElementById('modalTitle').innerText = title;
            filtered.forEach(function(sa) {{
                const tr = document.createElement('tr');
                tr.innerHTML = '<td>' + sa.planet + '</td><td>' + sa.star + '</td><td>' + sa.orb.toFixed(2) + '°</td><td>' + sa.meaning + '</td>';
                tbody.appendChild(tr);
            }});
            document.getElementById('starModal').style.display = 'block';
        }}
        function closeStarModal() {{ document.getElementById('starModal').style.display = 'none'; }}
        window.onclick = function(event) {{ let modal = document.getElementById('starModal'); if (event.target == modal) modal.style.display = "none"; }}
    </script>
    </body></html>"""
    
    user_info_dict = session.get('user')
    user_email = user_info_dict.get('email') if user_info_dict else 'guest'
    
    email_folder = os.path.join(RESULTS_DIR, user_email)
    if os.path.exists(email_folder):
        shutil.rmtree(email_folder)
    os.makedirs(email_folder)
    
    user_folder = os.path.join(email_folder, user_name)
    if not os.path.exists(user_folder):
        os.makedirs(user_folder)
        
    filename = f"report_{user_name}.html"
    filepath = os.path.join(user_folder, filename)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(html_template)
        
    import re
    house_blocks = re.findall(r'<details class="detailed-house">.*?</details>', detailed_html, re.DOTALL)
    
    base_css = """
    <style>
        body{font-family:sans-serif;background:#f4f7f6;padding:20px;color:#333}
        .detailed-house { border: 1px solid #ddd; padding: 15px; margin-top: 20px; border-radius: 8px; background: #fff; }
        .house-header { font-size: 18px; font-weight: bold; color: #4B0082; border-bottom: 2px solid #4B0082; padding-bottom: 5px; margin-bottom: 10px; }
        .cusp-info { font-size: 14px; font-weight: bold; background: #f0f0f0; padding: 5px 10px; border-radius: 4px; margin-bottom: 15px; }
        .planet-detail { border-left: 3px solid #666; padding-left: 15px; margin-bottom: 20px; font-size: 13px; line-height: 1.6; }
        .planet-title { font-size: 15px; font-weight: bold; color: #333; margin-top: 10px; }
        .score-line { color: #555; }
        .total-score { font-weight: bold; color: #d32f2f; font-size: 14px; margin-top: 3px; border-top: 1px dashed #ccc; padding-top: 3px; }
        .aspect-details { font-size: 12px; color: #777; margin-top: 5px; font-style: italic; }
    </style>
    """

    for i, block in enumerate(house_blocks, 1):
        block_open = block.replace('<details class="detailed-house">', '<details class="detailed-house" open>')
        house_html = f"<!DOCTYPE html>\n<html>\n<head>\n<meta charset='UTF-8'>\n{base_css}\n</head>\n<body>\n{block_open}\n</body>\n</html>"
        house_filename = f"{user_name}_HOUSE {i}.html"
        house_filepath = os.path.join(user_folder, house_filename)
        with open(house_filepath, "w", encoding="utf-8") as f:
            f.write(house_html)
    
    # Record user information and their Astrolabe input if they are logged in via Google
    user_info = session.get('user')
    if user_info:
        log_entry = {
            'timestamp': datetime.datetime.now().isoformat(),
            'google_account': user_info,
            'astrolabe_input': {
                'name': user_name,
                'gender': gender,
                'dob': dob_input,
                'location': location_input
            }
        }
        log_file_path = os.path.join(BASE_DIR, 'account', 'log.json')
        try:
            logs = []
            if os.path.exists(log_file_path):
                with open(log_file_path, 'r', encoding='utf-8') as log_f:
                    try:
                        logs = json.load(log_f)
                    except json.JSONDecodeError:
                        logs = []
            
            user_email = user_info.get('email')
            existing_index = -1
            if user_email:
                for i, log in enumerate(logs):
                    if log.get('google_account', {}).get('email') == user_email:
                        existing_index = i
                        break
            
            if existing_index >= 0:
                logs[existing_index] = log_entry
            else:
                logs.append(log_entry)

            with open(log_file_path, 'w', encoding='utf-8') as log_f:
                json.dump(logs, log_f, ensure_ascii=False, indent=4)
        except Exception as e:
            print(f"Error writing to log.json: {e}", flush=True)

    return jsonify({
        'status': 'success',
        'report_url': f'/results/{user_email}/{user_name}/{filename}',
        'star_aspects': star_aspects,
        'star_stats': star_stats,
        'chart_svg_base64': svg_base64,
        'user_name': user_name
    })

@app.route('/api/ai_analysis', methods=['POST'])
def api_ai_analysis():
    data = request.json
    user_name = data.get('user_name')
    house_number = data.get('house_number')
    lang = data.get('lang', 'en')
    
    if not user_name or not house_number:
        return jsonify({'error': 'Missing parameters'}), 400
        
    user_email = session.get('user', {}).get('email') if session.get('user') else 'guest'
    analysis_text = ai_analyzer.get_house_analysis(user_email, user_name, house_number, lang)
    return jsonify({
        'status': 'success',
        'analysis': analysis_text
    })

@app.route('/api/chatbot', methods=['POST'])
def api_chatbot():
    data = request.json
    user_name = data.get('user_name')
    message = data.get('message')
    history = data.get('history', [])
    persona = data.get('persona', 'bot1')
    lang = data.get('lang', 'en')
    
    if not user_name or not message:
        return jsonify({'error': 'Missing parameters'}), 400
        
    user_email = session.get('user', {}).get('email') if session.get('user') else 'guest'
    
    if persona == 'bot2':
        reply = chatbot2.get_chat_response(user_email, user_name, message, history, lang)
    else:
        reply = chatbot1.get_chat_response(user_email, user_name, message, history, lang)

    if reply == "__SERVICE_UNAVAILABLE__":
        return jsonify({'status': 'error', 'error': 'unavailable'}), 503
    elif reply == "__SERVICE_ERROR__":
        return jsonify({'status': 'error', 'error': 'internal'}), 500

    return jsonify({
        'status': 'success',
        'reply': reply
    })

@app.route('/generate_pdf', methods=['POST'])
def generate_pdf():
    data = request.json or {}
    user_info = session.get('user')
    user_email = user_info.get('email') if user_info else 'guest'
    
    return pdf_generator.generate_full_pdf(user_email, data, RESULTS_DIR)

if __name__ == '__main__':
    app.run(debug=True, port=5001)
