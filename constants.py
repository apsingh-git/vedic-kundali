"""
Vedic Astrology Constants — Signs, Nakshatras, Planets, Lordships, Dignities, Aspects
"""

# ── Zodiac Signs ──────────────────────────────────────────────
SIGNS = [
    'Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo',
    'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces'
]
SIGN_ABBR = ['Ar', 'Ta', 'Ge', 'Cn', 'Le', 'Vi', 'Li', 'Sc', 'Sg', 'Cp', 'Aq', 'Pi']
SIGN_ELEMENTS = ['Fire', 'Earth', 'Air', 'Water'] * 3
SIGN_MODALITY = ['Cardinal', 'Fixed', 'Mutable'] * 4

# ── Planets ───────────────────────────────────────────────────
PLANETS = ['Sun', 'Moon', 'Mars', 'Mercury', 'Jupiter', 'Venus', 'Saturn', 'Rahu', 'Ketu']
PLANET_ABBR = {'Sun': 'Su', 'Moon': 'Mo', 'Mars': 'Ma', 'Mercury': 'Me',
               'Jupiter': 'Ju', 'Venus': 'Ve', 'Saturn': 'Sa', 'Rahu': 'Ra', 'Ketu': 'Ke'}

# Swiss Ephemeris planet IDs
import swisseph as swe
SWE_PLANETS = {
    'Sun': swe.SUN, 'Moon': swe.MOON, 'Mars': swe.MARS,
    'Mercury': swe.MERCURY, 'Jupiter': swe.JUPITER, 'Venus': swe.VENUS,
    'Saturn': swe.SATURN, 'Rahu': swe.MEAN_NODE  # Ketu = Rahu + 180
}

# ── Nakshatras (27) ──────────────────────────────────────────
NAKSHATRAS = [
    'Ashwini', 'Bharani', 'Krittika', 'Rohini', 'Mrigashira', 'Ardra',
    'Punarvasu', 'Pushya', 'Ashlesha', 'Magha', 'Purva Phalguni', 'Uttara Phalguni',
    'Hasta', 'Chitra', 'Swati', 'Vishakha', 'Anuradha', 'Jyeshtha',
    'Mula', 'Purva Ashadha', 'Uttara Ashadha', 'Shravana', 'Dhanishtha', 'Shatabhisha',
    'Purva Bhadrapada', 'Uttara Bhadrapada', 'Revati'
]
NAKSHATRA_SPAN = 13 + 20/60  # 13°20' each

# Nakshatra lords (Vimshottari order, repeats 3x for 27 nakshatras)
NAKSHATRA_LORDS = ['Ketu', 'Venus', 'Sun', 'Moon', 'Mars', 'Rahu', 'Jupiter', 'Saturn', 'Mercury'] * 3

# ── Vimshottari Dasha Periods (years) ────────────────────────
DASHA_YEARS = {
    'Ketu': 7, 'Venus': 20, 'Sun': 6, 'Moon': 10, 'Mars': 7,
    'Rahu': 18, 'Jupiter': 16, 'Saturn': 19, 'Mercury': 17
}
DASHA_ORDER = ['Ketu', 'Venus', 'Sun', 'Moon', 'Mars', 'Rahu', 'Jupiter', 'Saturn', 'Mercury']
TOTAL_DASHA_YEARS = 120

# ── Sign Lordships ────────────────────────────────────────────
SIGN_LORDS = {
    'Aries': 'Mars', 'Taurus': 'Venus', 'Gemini': 'Mercury', 'Cancer': 'Moon',
    'Leo': 'Sun', 'Virgo': 'Mercury', 'Libra': 'Venus', 'Scorpio': 'Mars',
    'Sagittarius': 'Jupiter', 'Capricorn': 'Saturn', 'Aquarius': 'Saturn', 'Pisces': 'Jupiter'
}
# Reverse: planet -> signs owned
PLANET_OWNS = {}
for sign, lord in SIGN_LORDS.items():
    PLANET_OWNS.setdefault(lord, []).append(sign)

# ── Exaltation & Debilitation ─────────────────────────────────
EXALTATION = {
    'Sun': ('Aries', 10), 'Moon': ('Taurus', 3), 'Mars': ('Capricorn', 28),
    'Mercury': ('Virgo', 15), 'Jupiter': ('Cancer', 5), 'Venus': ('Pisces', 27),
    'Saturn': ('Libra', 20), 'Rahu': ('Taurus', 20), 'Ketu': ('Scorpio', 20)
}
DEBILITATION = {
    'Sun': ('Libra', 10), 'Moon': ('Scorpio', 3), 'Mars': ('Cancer', 28),
    'Mercury': ('Pisces', 15), 'Jupiter': ('Capricorn', 5), 'Venus': ('Virgo', 27),
    'Saturn': ('Aries', 20), 'Rahu': ('Scorpio', 20), 'Ketu': ('Taurus', 20)
}

# Moolatrikona signs and degree ranges
MOOLATRIKONA = {
    'Sun': ('Leo', 0, 20), 'Moon': ('Taurus', 3, 30), 'Mars': ('Aries', 0, 12),
    'Mercury': ('Virgo', 15, 20), 'Jupiter': ('Sagittarius', 0, 10),
    'Venus': ('Libra', 0, 15), 'Saturn': ('Aquarius', 0, 20)
}

# ── Natural Friendships (Parashari) ──────────────────────────
NATURAL_FRIENDS = {
    'Sun':     ['Moon', 'Mars', 'Jupiter'],
    'Moon':    ['Sun', 'Mercury'],
    'Mars':    ['Sun', 'Moon', 'Jupiter'],
    'Mercury': ['Sun', 'Venus'],
    'Jupiter': ['Sun', 'Moon', 'Mars'],
    'Venus':   ['Mercury', 'Saturn'],
    'Saturn':  ['Mercury', 'Venus'],
    'Rahu':    ['Mercury', 'Venus', 'Saturn'],
    'Ketu':    ['Mars', 'Jupiter'],
}
NATURAL_ENEMIES = {
    'Sun':     ['Venus', 'Saturn'],
    'Moon':    [],
    'Mars':    ['Mercury'],
    'Mercury': ['Moon'],
    'Jupiter': ['Mercury', 'Venus'],
    'Venus':   ['Sun', 'Moon'],
    'Saturn':  ['Sun', 'Moon', 'Mars'],
    'Rahu':    ['Sun', 'Moon', 'Mars'],
    'Ketu':    ['Moon', 'Venus'],
}

# ── Special Aspects ───────────────────────────────────────────
# All planets aspect 7th. These are ADDITIONAL aspects.
SPECIAL_ASPECTS = {
    'Mars': [4, 8],       # 4th and 8th from self
    'Jupiter': [5, 9],    # 5th and 9th from self
    'Saturn': [3, 10],    # 3rd and 10th from self
    'Rahu': [5, 9],       # Same as Jupiter
    'Ketu': [5, 9],       # Same as Jupiter
}

# ── Karakas (Significators) ──────────────────────────────────
KARAKAS = {
    'Sun': 'Soul, father, authority, government, health',
    'Moon': 'Mind, mother, emotions, public, nurturing',
    'Mars': 'Energy, courage, siblings, property, surgery',
    'Mercury': 'Intelligence, speech, commerce, friends, writing',
    'Jupiter': 'Wisdom, children, wealth, guru, dharma, husband',
    'Venus': 'Love, marriage, luxury, art, vehicles, wife',
    'Saturn': 'Discipline, longevity, sorrow, service, karma',
    'Rahu': 'Foreign, obsession, technology, unconventional',
    'Ketu': 'Spirituality, liberation, past life, mysticism',
}

# ── House Significations ─────────────────────────────────────
HOUSE_SIGNIFICATIONS = {
    1: 'Self, body, personality, health, appearance',
    2: 'Wealth, family, speech, food, right eye',
    3: 'Siblings, courage, communication, short travel, hands',
    4: 'Mother, home, happiness, vehicles, education, chest',
    5: 'Children, intelligence, creativity, past merit, romance',
    6: 'Enemies, disease, debt, service, competition, obstacles',
    7: 'Marriage, partnership, business, public dealings',
    8: 'Longevity, transformation, occult, inheritance, sudden events',
    9: 'Fortune, father, dharma, higher learning, long travel, guru',
    10: 'Career, status, karma, authority, government, fame',
    11: 'Gains, income, elder siblings, fulfillment of desires',
    12: 'Losses, foreign lands, moksha, expenses, bed pleasures, isolation',
}

# ── Benefic / Malefic ────────────────────────────────────────
NATURAL_BENEFICS = ['Jupiter', 'Venus', 'Moon', 'Mercury']  # Mercury when unafflicted
NATURAL_MALEFICS = ['Sun', 'Mars', 'Saturn', 'Rahu', 'Ketu']

# ── Dig Bala (Directional Strength) ──────────────────────────
# House where planet gets directional strength
DIG_BALA = {
    'Sun': 10, 'Mars': 10,
    'Jupiter': 1, 'Mercury': 1,
    'Moon': 4, 'Venus': 4,
    'Saturn': 7,
}

# ── Combustion Degrees (proximity to Sun) ─────────────────────
COMBUSTION_DEGREES = {
    'Moon': 12, 'Mars': 17, 'Mercury': 14,  # 12 when retrograde
    'Jupiter': 11, 'Venus': 10, 'Saturn': 15
}

# ── Major Indian Cities Database ──────────────────────────────
CITY_DB = {
    'delhi': (28.6139, 77.2090), 'new delhi': (28.6139, 77.2090),
    'mumbai': (19.0760, 72.8777), 'bombay': (19.0760, 72.8777),
    'bangalore': (12.9716, 77.5946), 'bengaluru': (12.9716, 77.5946),
    'chennai': (13.0827, 80.2707), 'madras': (13.0827, 80.2707),
    'kolkata': (22.5726, 88.3639), 'calcutta': (22.5726, 88.3639),
    'hyderabad': (17.3850, 78.4867),
    'pune': (18.5204, 73.8567), 'poona': (18.5204, 73.8567),
    'ahmedabad': (23.0225, 72.5714),
    'jaipur': (26.9124, 75.7873),
    'lucknow': (26.8467, 80.9462),
    'chandigarh': (30.7333, 76.7794),
    'bhopal': (23.2599, 77.4126),
    'patna': (25.6093, 85.1376),
    'indore': (22.7196, 75.8577),
    'nagpur': (21.1458, 79.0882),
    'coimbatore': (11.0168, 76.9558),
    'kochi': (9.9312, 76.2673), 'cochin': (9.9312, 76.2673),
    'thiruvananthapuram': (8.5241, 76.9366), 'trivandrum': (8.5241, 76.9366),
    'guwahati': (26.1445, 91.7362),
    'varanasi': (25.3176, 83.0068), 'banaras': (25.3176, 83.0068),
    'amritsar': (31.6340, 74.8723),
    'surat': (21.1702, 72.8311),
    'visakhapatnam': (17.6868, 83.2185), 'vizag': (17.6868, 83.2185),
    'mysore': (12.2958, 76.6394), 'mysuru': (12.2958, 76.6394),
    'udaipur': (24.5854, 73.7125),
    'jodhpur': (26.2389, 73.0243),
    'dehradun': (30.3165, 78.0322),
    'shimla': (31.1048, 77.1734),
    'srinagar': (34.0837, 74.7973),
    'ranchi': (23.3441, 85.3096),
    'bhubaneswar': (20.2961, 85.8245),
    'raipur': (21.2514, 81.6296),
    'goa': (15.2993, 74.1240), 'panaji': (15.4909, 73.8278),
    'pondicherry': (11.9416, 79.8083), 'puducherry': (11.9416, 79.8083),
    'noida': (28.5355, 77.3910),
    'gurgaon': (28.4595, 77.0266), 'gurugram': (28.4595, 77.0266),
    'faridabad': (28.4089, 77.3178),
    'agra': (27.1767, 78.0081),
    'kanpur': (26.4499, 80.3319),
    'ludhiana': (30.9010, 75.8573),
    'jalandhar': (31.3260, 75.5762),
    'patiala': (30.3398, 76.3869),
    'meerut': (28.9845, 77.7064),
    'allahabad': (25.4358, 81.8463), 'prayagraj': (25.4358, 81.8463),
    'nashik': (19.9975, 73.7898),
    'aurangabad': (19.8762, 75.3433),
    'rajkot': (22.3039, 70.8022),
    'vadodara': (22.3072, 73.1812), 'baroda': (22.3072, 73.1812),
    'thane': (19.2183, 72.9781),
    'madurai': (9.9252, 78.1198),
    'salem': (11.6643, 78.1460),
    'tiruchirappalli': (10.7905, 78.7047), 'trichy': (10.7905, 78.7047),
    'mangalore': (12.9141, 74.8560), 'mangaluru': (12.9141, 74.8560),
    'hubli': (15.3647, 75.1240),
    'belgaum': (15.8497, 74.4977), 'belagavi': (15.8497, 74.4977),
    'jammu': (32.7266, 74.8570),
    'jabalpur': (23.1815, 79.9864),
    'gwalior': (26.2183, 78.1828),
    'bareilly': (28.3670, 79.4304),
    'moradabad': (28.8386, 78.7733),
    'aligarh': (27.8974, 78.0880),
    'gorakhpur': (26.7606, 83.3732),
    'bikaner': (28.0229, 73.3119),
    'kota': (25.2138, 75.8648),
    'ajmer': (26.4499, 74.6399),
    'dhanbad': (23.7957, 86.4304),
    'jamshedpur': (22.8046, 86.2029),
    'cuttack': (20.4625, 85.8830),
    'warangal': (17.9689, 79.5941),
    'guntur': (16.3067, 80.4365),
    'nellore': (14.4426, 79.9865),
    'tirupati': (13.6288, 79.4192),
    'ambernath': (19.1864, 73.1853), 'ambarnath': (19.1864, 73.1853),
    'kalyan': (19.2437, 73.1355), 'dombivli': (19.2183, 73.0868),
    'badlapur': (19.1555, 73.2281), 'ulhasnagar': (19.2215, 73.1645),
    'bhiwandi': (19.2967, 73.0631), 'panvel': (18.9894, 73.1175),
    'navi mumbai': (19.0330, 73.0297), 'vashi': (19.0771, 72.9987),
    'kharghar': (19.0474, 73.0680), 'sangli': (16.8524, 74.5815),
    'kolhapur': (16.7050, 74.2433), 'solapur': (17.6599, 75.9064),
    'latur': (18.4088, 76.5604), 'nanded': (19.1383, 77.3210),
    'akola': (20.7002, 77.0082), 'amravati': (20.9374, 77.7796),
    'chandrapur': (19.9615, 79.2961), 'parbhani': (19.2608, 76.7748),
    'jalgaon': (21.0077, 75.5626), 'satara': (17.6805, 74.0183),
    'ratnagiri': (16.9902, 73.3120), 'sindhudurg': (16.3489, 73.6520),
    'alibaug': (18.6414, 72.8724), 'lonavala': (18.7481, 73.4072),
    'mahabaleshwar': (17.9307, 73.6477), 'shirdi': (19.7668, 74.4773),
    'palghar': (19.6968, 72.7651), 'vasai': (19.3607, 72.8397),
    'virar': (19.4559, 72.8111), 'mira road': (19.2812, 72.8683),
    'bhayandar': (19.3012, 72.8515), 'borivali': (19.2308, 72.8567),
    'andheri': (19.1136, 72.8697),
    'pathankot': (32.2746, 75.6526), 'hoshiarpur': (31.5288, 75.9112),
    'batala': (31.8185, 75.2028), 'kapurthala': (31.3808, 75.3815),
    'barnala': (30.3819, 75.5459), 'sangrur': (30.2477, 75.8387),
    'moga': (30.8163, 75.1707), 'firozpur': (30.9417, 74.6133),
    'bathinda': (30.2104, 74.9455), 'muktsar': (30.4711, 74.5147),
    'ambala': (30.3782, 76.7767), 'karnal': (29.6857, 76.9905),
    'panipat': (29.3909, 76.9635), 'sonipat': (28.9931, 77.0151),
    'rohtak': (28.8955, 76.6066), 'hisar': (29.1492, 75.7217),
    'sirsa': (29.5340, 75.0274), 'bhiwani': (28.7931, 76.1399),
    'rewari': (28.1970, 76.6193), 'mahendragarh': (28.2791, 76.1523),
    'yamunanagar': (30.1290, 77.2674), 'kurukshetra': (29.9695, 76.8783),
    'panchkula': (30.6942, 76.8606),
    'haridwar': (29.9457, 78.1642), 'rishikesh': (30.0869, 78.2676),
    'nainital': (29.3803, 79.4636), 'mussoorie': (30.4598, 78.0644),
    'roorkee': (29.8543, 77.8880), 'haldwani': (29.2183, 79.5130),
    'rudrapur': (28.9753, 79.3994), 'kashipur': (29.2104, 78.9569),
    'mathura': (27.4924, 77.6737), 'vrindavan': (27.5806, 77.7009),
    'ayodhya': (26.7922, 82.1998), 'prayagraj': (25.4358, 81.8463),
    'sultanpur': (26.2648, 82.0727), 'azamgarh': (26.0735, 83.1854),
    'jaunpur': (25.7568, 82.6836), 'mirzapur': (25.1337, 82.5644),
    'banda': (25.4766, 80.3333), 'hamirpur': (25.9569, 80.1531),
    'unnao': (26.5473, 80.4879), 'hardoi': (27.3939, 80.1311),
    'sitapur': (27.5648, 80.6826), 'lakhimpur': (27.9462, 80.7742),
    'shahjahanpur': (27.8768, 79.9108), 'rampur': (28.7890, 79.0250),
    'sambhal': (28.5855, 78.5608), 'muzaffarnagar': (29.4727, 77.7085),
    'saharanpur': (29.9680, 77.5510), 'bijnor': (29.3725, 78.1365),
    'firozabad': (27.1503, 78.3958), 'mainpuri': (27.2367, 79.0246),
    'etawah': (26.7728, 79.0244), 'farrukhabad': (27.3906, 79.5750),
    'fatehpur': (25.9301, 80.8045),
    'siliguri': (26.7271, 88.3953), 'darjeeling': (27.0360, 88.2627),
    'howrah': (22.5958, 88.2636), 'durgapur': (23.5204, 87.3119),
    'asansol': (23.6739, 86.9524), 'bardhaman': (23.2324, 87.8615),
    'kharagpur': (22.3460, 87.3239), 'haldia': (22.0257, 88.0583),
    'malda': (25.0108, 88.1411), 'baharampur': (24.1052, 88.2511),
    'krishnanagar': (23.4013, 88.4942),
    'bokaro': (23.6693, 86.1511), 'hazaribagh': (23.9966, 85.3618),
    'deoghar': (24.4764, 86.6947), 'giridih': (24.1903, 86.3012),
    'dumka': (24.2641, 87.2506),
    'muzaffarpur': (26.1209, 85.3647), 'gaya': (24.7955, 85.0002),
    'bhagalpur': (25.2425, 86.9842), 'darbhanga': (26.1542, 85.8918),
    'purnia': (25.7771, 87.4753), 'arrah': (25.5561, 84.6631),
    'begusarai': (25.4182, 86.1272), 'samastipur': (25.8625, 85.7807),
    'katihar': (25.5393, 87.5716),
    'rourkela': (22.2604, 84.8536), 'sambalpur': (21.4669, 83.9812),
    'berhampur': (19.3149, 84.7941), 'balasore': (21.4942, 86.9234),
    'puri': (19.7983, 85.8249), 'konark': (19.8876, 86.0945),
    'bilaspur': (22.0797, 82.1409), 'korba': (22.3595, 82.7501),
    'durg': (21.1904, 81.2849), 'bhilai': (21.2167, 81.4167),
    'rajnandgaon': (21.0974, 81.0290),
    'gwalior': (26.2183, 78.1828), 'ujjain': (23.1765, 75.7885),
    'sagar': (23.8388, 78.7378), 'satna': (24.5802, 80.8322),
    'rewa': (24.5373, 81.3042), 'chhindwara': (22.0574, 78.9382),
    'khandwa': (21.8262, 76.3526), 'burhanpur': (21.3104, 76.2301),
    'dewas': (22.9623, 76.0508), 'ratlam': (23.3340, 75.0367),
    'mandsaur': (24.0716, 75.0696),
    'bhuj': (23.2420, 69.6669), 'gandhidham': (23.0753, 70.1337),
    'jamnagar': (22.4707, 70.0577), 'junagadh': (21.5222, 70.4579),
    'bhavnagar': (21.7645, 72.1519), 'porbandar': (21.6417, 69.6293),
    'anand': (22.5645, 72.9289), 'nadiad': (22.6916, 72.8634),
    'mehsana': (23.5880, 72.3693), 'palanpur': (24.1680, 72.4382),
    'morbi': (22.8120, 70.8378), 'surendranagar': (22.7277, 71.6480),
    'vapi': (20.3722, 72.9047), 'navsari': (20.9467, 72.9520),
    'bharuch': (21.7051, 72.9959), 'godhra': (22.7788, 73.6143),
    'gandhinagar': (23.2156, 72.6369),
    'tirunelveli': (8.7130, 77.7567), 'thoothukudi': (8.7642, 78.1348),
    'tuticorin': (8.7642, 78.1348), 'dindigul': (10.3624, 77.9695),
    'erode': (11.3410, 77.7172), 'tirupur': (11.1085, 77.3411),
    'vellore': (12.9165, 79.1325), 'thanjavur': (10.7870, 79.1378),
    'cuddalore': (11.7480, 79.7714), 'kanchipuram': (12.8342, 79.7036),
    'kumbakonam': (10.9617, 79.3881), 'nagapattinam': (10.7672, 79.8449),
    'ramanathapuram': (9.3762, 78.8308), 'sivaganga': (9.8477, 78.4839),
    'karur': (10.9601, 78.0766), 'namakkal': (11.2189, 78.1674),
    'nagercoil': (8.1833, 77.4119), 'hosur': (12.7409, 77.8253),
    'ooty': (11.4102, 76.6950), 'kodaikanal': (10.2381, 77.4892),
    'thrissur': (10.5276, 76.2144), 'kozhikode': (11.2588, 75.7804),
    'calicut': (11.2588, 75.7804), 'palakkad': (10.7867, 76.6548),
    'kannur': (11.8745, 75.3704), 'kollam': (8.8932, 76.6141),
    'alappuzha': (9.4981, 76.3388), 'kottayam': (9.5916, 76.5222),
    'malappuram': (11.0510, 76.0711), 'wayanad': (11.6854, 76.1320),
    'kasaragod': (12.4996, 74.9869), 'idukki': (9.8504, 76.9711),
    'munnar': (10.0889, 77.0595),
    'bellary': (15.1394, 76.9214), 'davangere': (14.4644, 75.9218),
    'shimoga': (13.9299, 75.5681), 'tumkur': (13.3379, 77.1173),
    'udupi': (13.3409, 74.7421), 'bidar': (17.9104, 77.5199),
    'gulbarga': (17.3297, 76.8343), 'kalaburagi': (17.3297, 76.8343),
    'raichur': (16.2076, 77.3463), 'hassan': (13.0072, 76.0962),
    'chitradurga': (14.2226, 76.3984), 'mandya': (12.5218, 76.8951),
    'chikmagalur': (13.3161, 75.7720), 'dharwad': (15.4589, 75.0078),
    'vijayapura': (16.8302, 75.7100), 'bijapur': (16.8302, 75.7100),
    'london': (51.5074, -0.1278),
    'new york': (40.7128, -74.0060),
    'los angeles': (34.0522, -118.2437),
    'chicago': (41.8781, -87.6298),
    'toronto': (43.6532, -79.3832),
    'sydney': (-33.8688, 151.2093),
    'singapore': (1.3521, 103.8198),
    'dubai': (25.2048, 55.2708),
    'hong kong': (22.3193, 114.1694),
    'tokyo': (35.6762, 139.6503),
}

# ── South Indian Chart Layout ────────────────────────────────
# Maps sign index (0=Aries) to grid position (row, col) in 4x4 grid
SOUTH_INDIAN_LAYOUT = {
    11: (0, 0),  # Pisces
    0:  (0, 1),  # Aries
    1:  (0, 2),  # Taurus
    2:  (0, 3),  # Gemini
    3:  (1, 3),  # Cancer
    4:  (2, 3),  # Leo
    5:  (3, 3),  # Virgo
    6:  (3, 2),  # Libra
    7:  (3, 1),  # Scorpio
    8:  (3, 0),  # Sagittarius
    9:  (2, 0),  # Capricorn
    10: (1, 0),  # Aquarius
}

# ── Divisional Chart Formulas ─────────────────────────────────
# D9 (Navamsha): Starting sign for each element
D9_START = {
    'Fire': 0,    # Aries signs start from Aries
    'Earth': 9,   # Taurus signs start from Capricorn
    'Air': 6,     # Gemini signs start from Libra
    'Water': 3,   # Cancer signs start from Cancer
}

# Element of each sign (by index)
SIGN_ELEMENT = ['Fire', 'Earth', 'Air', 'Water'] * 3
