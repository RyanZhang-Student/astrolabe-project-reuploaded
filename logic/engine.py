import ssl
import sys
import datetime
import math
from skyfield.api import load, wgs84
from geopy.geocoders import Nominatim
from timezonefinder import TimezoneFinder
import pytz
import geopy.adapters

# SSL Fix
try:
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    ssl._create_default_https_context = lambda: ctx
except Exception:
    pass

def lookup_local_city(query):
    """
    Search for a city in the local world_cities.json file.
    Matches against city name (case-insensitive).
    """
    try:
        import json
        import os
        data_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'world_cities.json')
        with open(data_path, 'r', encoding='utf-8') as f:
            cities = json.load(f)
        
        # Clean query: e.g., "BEIJING-CN" -> "BEIJING"
        clean_query = query.split('-')[0].strip().upper()
        
        for city in cities:
            if city['name'].upper() == clean_query:
                return city['lat'], city['lng'], f"{city['name']} ({city['country']}) [Local]"
    except Exception:
        pass
    return None

def get_astronomical_data(dob_input, location_input):
    try:
        p = dob_input.split('-')
        local_dt = datetime.datetime(int(p[0]), int(p[1][:2]), int(p[1][2:]), int(p[2][:2]), int(p[2][2:]))
    except Exception as e:
        return None, f"Time Format Error: {e}"

    # Try local lookup first
    local_res = lookup_local_city(location_input)
    if local_res:
        lat, lng, formatted_location = local_res
    else:
        # Fallback to online geocoder
        geolocator = Nominatim(user_agent="Astrolabe_Pro_V17", ssl_context=ctx, adapter_factory=geopy.adapters.URLLibAdapter)
        try:
            loc = geolocator.geocode(location_input, timeout=10)
            lat, lng, formatted_location = (loc.latitude, loc.longitude, loc.address) if loc else (39.9, 116.4, "Default (Beijing)")
        except:
            lat, lng, formatted_location = 39.9, 116.4, "Default (Beijing)"

    tf = TimezoneFinder()
    tz_str = tf.timezone_at(lng=lng, lat=lat) or 'UTC'
    local_tz = pytz.timezone(tz_str)
    localized_dt = local_tz.localize(local_dt)
    utc_dt = localized_dt.astimezone(pytz.utc)

    # Use BUILTIN=TRUE to avoid downloading deltat.tdb and leap_seconds.list
    ts = load.timescale(builtin=True)
    import os
    eph_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'de421.bsp')
    eph = load(eph_path)
    t = ts.from_datetime(utc_dt)
    observer = eph['earth'] + wgs84.latlon(lat, lng)
    
    bodies = {'Sun': eph['sun'], 'Moon': eph['moon'], 'Mercury': eph['mercury'], 'Venus': eph['venus'], 
              'Mars': eph['mars'], 'Jupiter': eph['jupiter barycenter'], 'Saturn': eph['saturn barycenter'], 
              'Uranus': eph['uranus barycenter'], 'Neptune': eph['neptune barycenter'], 'Pluto': eph['pluto barycenter']}
    
    planets = {}
    for n, b in bodies.items():
        astrometric = observer.at(t).observe(b)
        apparent = astrometric.apparent()
        lon = apparent.ecliptic_latlon()[1].degrees
        t_next = ts.from_datetime(utc_dt + datetime.timedelta(hours=1))
        lon_next = observer.at(t_next).observe(b).apparent().ecliptic_latlon()[1].degrees
        is_retro = (lon_next < lon) if abs(lon_next - lon) < 180 else (lon_next > lon)
        planets[n] = {'lon': lon, 'is_retro': is_retro}
    
    T = (t.tt - 2451545.0) / 36525.0
    node_lon = (125.04455501 - 1934.1361849 * T + 0.0020762 * T**2 + (T**3 / 467410.0) - (T**4 / 18999000.0)) % 360
    planets['Node'] = {'lon': node_lon, 'is_retro': True} 
    
    gast_hours = t.gast
    last_deg = (gast_hours + lng / 15.0) * 15.0 % 360
    RAMC = math.radians(last_deg)
    eps = math.radians(23.439)
    lat_rad = math.radians(lat)
    
    mc_lon = math.degrees(math.atan2(math.sin(RAMC), math.cos(RAMC) * math.cos(eps))) % 360
    planets['Midheaven'] = {'lon': mc_lon}
    
    asc_lon = math.degrees(math.atan2(math.cos(RAMC), -(math.sin(RAMC) * math.cos(eps) + math.tan(lat_rad) * math.sin(eps)))) % 360
    planets['Asc'] = {'lon': asc_lon}

    # UPDATE: Returning (ts, t) as a third tuple element
    return planets, (localized_dt, tz_str, formatted_location), (ts, t)