SIGNS = ['Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo', 
         'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces']

PLANET_COLORS = {
    'Sun': '#FFD700', 'Moon': '#708090', 'Mercury': '#2E8B57', 'Venus': '#FF69B4',
    'Mars': '#FF4500', 'Jupiter': '#DAA520', 'Saturn': '#4B0082', 'Uranus': '#40E0D0',
    'Neptune': '#0000FF', 'Pluto': '#800000', 'Asc': '#FF0000', 'Dsc': '#FF4500',
    'Node': '#555', 'SNode': '#999', 'Midheaven': '#8B4513', 'IC': '#A52A2A', 'Fortune': '#FF8C00'
}

ASPECT_COLORS = {
    'Conjunction': '#333', 'Opposition': '#00008B', 'Trine': '#006400', 
    'Square': '#FF0000', 'Sextile': '#00BFFF'
}

CLASSICAL_RULERS = {
    'Aries': 'Mars', 'Taurus': 'Venus', 'Gemini': 'Mercury', 'Cancer': 'Moon',
    'Leo': 'Sun', 'Virgo': 'Mercury', 'Libra': 'Venus', 'Scorpio': 'Mars',
    'Sagittarius': 'Jupiter', 'Capricorn': 'Saturn', 'Aquarius': 'Saturn', 'Pisces': 'Jupiter'
}

EXALTATIONS = {
    'Aries': 'Sun', 'Taurus': 'Moon', 'Cancer': 'Jupiter', 'Virgo': 'Mercury',
    'Libra': 'Saturn', 'Capricorn': 'Mars', 'Pisces': 'Venus'
}

DETRIMENTS = {
    'Aries': 'Venus', 'Taurus': 'Mars', 'Gemini': 'Jupiter', 'Cancer': 'Saturn',
    'Leo': 'Saturn', 'Virgo': 'Jupiter', 'Libra': 'Mars', 'Scorpio': 'Venus',
    'Sagittarius': 'Mercury', 'Capricorn': 'Moon', 'Aquarius': 'Sun', 'Pisces': 'Mercury'
}

FALLS = {
    'Aries': 'Saturn', 'Taurus': '-', 'Gemini': '-', 'Cancer': 'Mars',
    'Leo': '-', 'Virgo': 'Venus', 'Libra': 'Sun', 'Scorpio': 'Moon',
    'Sagittarius': '-', 'Capricorn': 'Jupiter', 'Aquarius': '-', 'Pisces': 'Mercury'
}

EGYPTIAN_TERMS = {
    'Aries': [('Jupiter', 6), ('Venus', 12), ('Mercury', 20), ('Mars', 25), ('Saturn', 30)],
    'Taurus': [('Venus', 8), ('Mercury', 14), ('Jupiter', 22), ('Saturn', 27), ('Mars', 30)],
    'Gemini': [('Mercury', 6), ('Jupiter', 12), ('Venus', 17), ('Mars', 24), ('Saturn', 30)],
    'Cancer': [('Mars', 7), ('Venus', 13), ('Mercury', 19), ('Jupiter', 26), ('Saturn', 30)],
    'Leo': [('Jupiter', 6), ('Venus', 11), ('Saturn', 18), ('Mercury', 24), ('Mars', 30)],
    'Virgo': [('Mercury', 7), ('Venus', 17), ('Jupiter', 21), ('Mars', 28), ('Saturn', 30)],
    'Libra': [('Saturn', 6), ('Venus', 14), ('Jupiter', 21), ('Mercury', 28), ('Mars', 30)],
    'Scorpio': [('Mars', 7), ('Venus', 11), ('Mercury', 19), ('Jupiter', 24), ('Saturn', 30)],
    'Sagittarius': [('Jupiter', 12), ('Venus', 17), ('Mercury', 21), ('Saturn', 26), ('Mars', 30)],
    'Capricorn': [('Venus', 7), ('Mercury', 14), ('Jupiter', 22), ('Mars', 26), ('Saturn', 30)],
    'Aquarius': [('Saturn', 7), ('Mercury', 13), ('Venus', 20), ('Jupiter', 25), ('Mars', 30)],
    'Pisces': [('Venus', 12), ('Jupiter', 16), ('Mercury', 19), ('Mars', 28), ('Saturn', 30)]
}

TRIPLICITIES = {
    'Fire': {'Day': 'Sun', 'Night': 'Jupiter'},      
    'Earth': {'Day': 'Venus', 'Night': 'Moon'},      
    'Air': {'Day': 'Saturn', 'Night': 'Mercury'},    
    'Water': {'Day': 'Venus', 'Night': 'Mars'}       
}

SIGN_ELEMENTS = {
    'Aries': 'Fire', 'Leo': 'Fire', 'Sagittarius': 'Fire',
    'Taurus': 'Earth', 'Virgo': 'Earth', 'Capricorn': 'Earth',
    'Gemini': 'Air', 'Libra': 'Air', 'Aquarius': 'Air',
    'Cancer': 'Water', 'Scorpio': 'Water', 'Pisces': 'Water'
}

CHALDEAN_ORDER = ['Mars', 'Sun', 'Venus', 'Mercury', 'Moon', 'Saturn', 'Jupiter']