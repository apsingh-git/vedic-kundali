"""
Core Vedic Astrology Calculator — Planetary positions, houses, nakshatras,
divisional charts, dashas, planetary strength.
Uses Swiss Ephemeris (pyswisseph) with Lahiri Ayanamsa.
"""

import swisseph as swe
from datetime import datetime, timedelta
from timezonefinder import TimezoneFinder
import pytz
from constants import *

# Use Lahiri Ayanamsa (standard for Vedic/Indian astrology)
swe.set_sid_mode(swe.SIDM_LAHIRI)


def get_timezone(lat, lon):
    """Get timezone string from coordinates."""
    tf = TimezoneFinder()
    tz_str = tf.timezone_at(lat=lat, lng=lon)
    return tz_str or 'UTC'


def to_julian_day(year, month, day, hour, minute, lat, lon):
    """Convert local date/time to Julian Day, accounting for timezone."""
    tz_str = get_timezone(lat, lon)
    tz = pytz.timezone(tz_str)
    local_dt = tz.localize(datetime(year, month, day, hour, minute))
    utc_dt = local_dt.astimezone(pytz.utc)
    decimal_hour = utc_dt.hour + utc_dt.minute / 60.0 + utc_dt.second / 3600.0
    jd = swe.julday(utc_dt.year, utc_dt.month, utc_dt.day, decimal_hour)
    return jd, tz_str


def get_ayanamsa(jd):
    """Get Lahiri ayanamsa value for given Julian Day."""
    return swe.get_ayanamsa(jd)


def get_sidereal_position(jd, planet_id):
    """Get sidereal longitude, latitude, speed for a planet."""
    flags = swe.FLG_SIDEREAL | swe.FLG_SPEED
    result = swe.calc_ut(jd, planet_id, flags)
    lon = result[0][0]
    lat = result[0][1]
    speed = result[0][3]
    return lon, lat, speed


def lon_to_sign(lon):
    """Convert sidereal longitude to sign index (0-11) and degree within sign."""
    sign_idx = int(lon / 30) % 12
    degree = lon % 30
    return sign_idx, degree


def lon_to_nakshatra(lon):
    """Convert sidereal longitude to nakshatra index, pada, and degree within nakshatra."""
    nak_idx = int(lon / NAKSHATRA_SPAN) % 27
    degree_in_nak = lon % NAKSHATRA_SPAN
    pada = int(degree_in_nak / (NAKSHATRA_SPAN / 4)) + 1
    if pada > 4:
        pada = 4
    return nak_idx, pada, degree_in_nak


def get_ascendant(jd, lat, lon):
    """Calculate sidereal ascendant (Lagna)."""
    flags = swe.FLG_SIDEREAL
    cusps, ascmc = swe.houses(jd, lat, lon, b'W')  # Whole Sign
    asc_lon = ascmc[0]
    # Convert to sidereal
    ayanamsa = get_ayanamsa(jd)
    sid_asc = (asc_lon - ayanamsa) % 360
    return sid_asc


def calculate_chart(year, month, day, hour, minute, lat, lon):
    """
    Master calculation: compute full birth chart data.
    Returns a dict with all planetary and house information.
    """
    jd, tz_str = to_julian_day(year, month, day, hour, minute, lat, lon)
    ayanamsa = get_ayanamsa(jd)
    asc_lon = get_ascendant(jd, lat, lon)
    asc_sign, asc_deg = lon_to_sign(asc_lon)

    # ── Planetary Positions ───────────────────────────────
    planets_data = {}
    for name in PLANETS:
        if name == 'Ketu':
            # Ketu is always 180° from Rahu
            rahu_lon = planets_data['Rahu']['longitude']
            p_lon = (rahu_lon + 180) % 360
            p_lat = -planets_data['Rahu']['latitude']
            p_speed = planets_data['Rahu']['speed']
        else:
            planet_id = SWE_PLANETS[name]
            p_lon, p_lat, p_speed = get_sidereal_position(jd, planet_id)

        sign_idx, deg_in_sign = lon_to_sign(p_lon)
        nak_idx, pada, deg_in_nak = lon_to_nakshatra(p_lon)

        # House placement (whole sign from ascendant)
        house = ((sign_idx - asc_sign) % 12) + 1

        # Retrograde check (negative speed, not applicable to Sun/Moon/Rahu/Ketu)
        is_retrograde = False
        if name not in ('Sun', 'Moon', 'Rahu', 'Ketu') and p_speed < 0:
            is_retrograde = True

        # Rahu/Ketu are always retrograde in mean node
        if name in ('Rahu', 'Ketu'):
            is_retrograde = True

        planets_data[name] = {
            'longitude': p_lon,
            'latitude': p_lat,
            'speed': p_speed,
            'sign_idx': sign_idx,
            'sign': SIGNS[sign_idx],
            'degree': deg_in_sign,
            'nakshatra_idx': nak_idx,
            'nakshatra': NAKSHATRAS[nak_idx],
            'pada': pada,
            'house': house,
            'is_retrograde': is_retrograde,
            'nakshatra_lord': NAKSHATRA_LORDS[nak_idx],
        }

    # ── Combustion Check ──────────────────────────────────
    sun_lon = planets_data['Sun']['longitude']
    for name in ['Moon', 'Mars', 'Mercury', 'Jupiter', 'Venus', 'Saturn']:
        diff = abs(planets_data[name]['longitude'] - sun_lon)
        if diff > 180:
            diff = 360 - diff
        threshold = COMBUSTION_DEGREES.get(name, 15)
        planets_data[name]['is_combust'] = diff <= threshold
        planets_data[name]['sun_distance'] = diff

    for name in ['Sun', 'Rahu', 'Ketu']:
        planets_data[name]['is_combust'] = False
        planets_data[name]['sun_distance'] = 0

    # ── Planetary Dignity ─────────────────────────────────
    for name in PLANETS:
        p = planets_data[name]
        dignity = get_dignity(name, p['sign'], p['degree'])
        p['dignity'] = dignity

    # ── Houses Data ───────────────────────────────────────
    houses = {}
    for h in range(1, 13):
        sign_idx = (asc_sign + h - 1) % 12
        sign = SIGNS[sign_idx]
        lord = SIGN_LORDS[sign]
        lord_house = planets_data[lord]['house'] if lord in planets_data else None
        occupants = [name for name, pd in planets_data.items() if pd['house'] == h]
        houses[h] = {
            'sign_idx': sign_idx,
            'sign': sign,
            'lord': lord,
            'lord_house': lord_house,
            'occupants': occupants,
        }

    # ── Aspects ───────────────────────────────────────────
    aspects = compute_aspects(planets_data)

    # ── Divisional Charts ─────────────────────────────────
    d9 = compute_navamsha(planets_data, asc_lon)
    d10 = compute_dasamsha(planets_data, asc_lon)
    d7 = compute_saptamsha(planets_data, asc_lon)
    d60 = compute_shashtiamsha(planets_data, asc_lon)

    # ── Vimshottari Dasha ─────────────────────────────────
    moon_lon = planets_data['Moon']['longitude']
    dashas = compute_vimshottari(moon_lon, year, month, day, hour, minute, tz_str)

    return {
        'birth': {
            'year': year, 'month': month, 'day': day,
            'hour': hour, 'minute': minute,
            'lat': lat, 'lon': lon, 'timezone': tz_str,
        },
        'jd': jd,
        'ayanamsa': ayanamsa,
        'ascendant': {
            'longitude': asc_lon,
            'sign_idx': asc_sign,
            'sign': SIGNS[asc_sign],
            'degree': asc_deg,
            'nakshatra': NAKSHATRAS[lon_to_nakshatra(asc_lon)[0]],
            'pada': lon_to_nakshatra(asc_lon)[1],
            'lord': SIGN_LORDS[SIGNS[asc_sign]],
        },
        'planets': planets_data,
        'houses': houses,
        'aspects': aspects,
        'divisional': {'D9': d9, 'D10': d10, 'D7': d7, 'D60': d60},
        'dashas': dashas,
    }


def get_dignity(planet, sign, degree):
    """Determine planetary dignity: exalted, moolatrikona, own, friend, neutral, enemy, debilitated."""
    # Exaltation
    if planet in EXALTATION and EXALTATION[planet][0] == sign:
        return 'Exalted'
    # Debilitation
    if planet in DEBILITATION and DEBILITATION[planet][0] == sign:
        return 'Debilitated'
    # Moolatrikona
    if planet in MOOLATRIKONA:
        mt_sign, mt_start, mt_end = MOOLATRIKONA[planet]
        if sign == mt_sign and mt_start <= degree < mt_end:
            return 'Moolatrikona'
    # Own sign
    if planet in PLANET_OWNS and sign in PLANET_OWNS[planet]:
        return 'Own Sign'
    # Friend / Neutral / Enemy
    lord = SIGN_LORDS.get(sign)
    if lord:
        if planet in NATURAL_FRIENDS and lord in NATURAL_FRIENDS.get(planet, []):
            return 'Friendly'
        if planet in NATURAL_ENEMIES and lord in NATURAL_ENEMIES.get(planet, []):
            return 'Enemy'
    return 'Neutral'


def compute_aspects(planets_data):
    """Compute all planetary aspects (Graha Drishti)."""
    aspects = {}
    for name in PLANETS:
        p = planets_data[name]
        sign_idx = p['sign_idx']
        aspected_signs = []
        aspected_houses = []

        # All planets aspect 7th from their position
        asp_7 = (sign_idx + 6) % 12
        aspected_signs.append(asp_7)

        # Special aspects
        if name in SPECIAL_ASPECTS:
            for offset in SPECIAL_ASPECTS[name]:
                asp = (sign_idx + offset - 1) % 12
                aspected_signs.append(asp)

        # Convert to houses
        asc_sign = None
        for nm, pd in planets_data.items():
            if pd['house'] == 1:
                asc_sign = pd['sign_idx']
                break
        if asc_sign is None:
            asc_sign = 0

        for s in aspected_signs:
            h = ((s - asc_sign) % 12) + 1
            aspected_houses.append(h)

        aspects[name] = {
            'aspected_signs': aspected_signs,
            'aspected_houses': aspected_houses,
        }
    return aspects


def compute_divisional_sign(lon, division):
    """Generic divisional chart calculation."""
    sign_idx = int(lon / 30) % 12
    deg = lon % 30
    part_size = 30.0 / division
    part = int(deg / part_size)
    return sign_idx, part


def compute_navamsha(planets_data, asc_lon):
    """D9 — Navamsha chart. Each sign divided into 9 parts of 3°20'."""
    d9 = {}
    # Process ascendant
    asc_sign_idx = int(asc_lon / 30) % 12
    asc_deg = asc_lon % 30
    asc_part = int(asc_deg / (30.0 / 9))
    if asc_part > 8:
        asc_part = 8
    element = SIGN_ELEMENT[asc_sign_idx]
    start = D9_START[element]
    d9_asc_sign = (start + asc_part) % 12
    d9['ascendant'] = {'sign_idx': d9_asc_sign, 'sign': SIGNS[d9_asc_sign]}

    for name in PLANETS:
        lon = planets_data[name]['longitude']
        sign_idx = int(lon / 30) % 12
        deg = lon % 30
        part = int(deg / (30.0 / 9))
        if part > 8:
            part = 8
        element = SIGN_ELEMENT[sign_idx]
        start = D9_START[element]
        d9_sign = (start + part) % 12
        house = ((d9_sign - d9_asc_sign) % 12) + 1
        d9[name] = {
            'sign_idx': d9_sign,
            'sign': SIGNS[d9_sign],
            'house': house,
            'lord': SIGN_LORDS[SIGNS[d9_sign]],
        }
    return d9


def compute_dasamsha(planets_data, asc_lon):
    """D10 — Dasamsha chart. Each sign divided into 10 parts of 3°."""
    d10 = {}
    asc_sign_idx = int(asc_lon / 30) % 12
    asc_deg = asc_lon % 30
    asc_part = int(asc_deg / 3)
    if asc_part > 9:
        asc_part = 9
    # Odd sign: start from same sign. Even sign: start from 9th from it.
    if asc_sign_idx % 2 == 0:  # Odd signs (0-indexed: 0=Aries=odd)
        d10_asc = (asc_sign_idx + asc_part) % 12
    else:
        d10_asc = (asc_sign_idx + 8 + asc_part) % 12
    d10['ascendant'] = {'sign_idx': d10_asc, 'sign': SIGNS[d10_asc]}

    for name in PLANETS:
        lon = planets_data[name]['longitude']
        sign_idx = int(lon / 30) % 12
        deg = lon % 30
        part = int(deg / 3)
        if part > 9:
            part = 9
        if sign_idx % 2 == 0:  # Odd
            d10_sign = (sign_idx + part) % 12
        else:  # Even
            d10_sign = (sign_idx + 8 + part) % 12
        house = ((d10_sign - d10_asc) % 12) + 1
        d10[name] = {
            'sign_idx': d10_sign,
            'sign': SIGNS[d10_sign],
            'house': house,
            'lord': SIGN_LORDS[SIGNS[d10_sign]],
        }
    return d10


def compute_saptamsha(planets_data, asc_lon):
    """D7 — Saptamsha chart. Each sign divided into 7 parts of ~4°17'."""
    d7 = {}
    part_size = 30.0 / 7
    asc_sign_idx = int(asc_lon / 30) % 12
    asc_deg = asc_lon % 30
    asc_part = int(asc_deg / part_size)
    if asc_part > 6:
        asc_part = 6
    if asc_sign_idx % 2 == 0:  # Odd
        d7_asc = (asc_sign_idx + asc_part) % 12
    else:  # Even
        d7_asc = (asc_sign_idx + 6 + asc_part) % 12
    d7['ascendant'] = {'sign_idx': d7_asc, 'sign': SIGNS[d7_asc]}

    for name in PLANETS:
        lon = planets_data[name]['longitude']
        sign_idx = int(lon / 30) % 12
        deg = lon % 30
        part = int(deg / part_size)
        if part > 6:
            part = 6
        if sign_idx % 2 == 0:
            d7_sign = (sign_idx + part) % 12
        else:
            d7_sign = (sign_idx + 6 + part) % 12
        house = ((d7_sign - d7_asc) % 12) + 1
        d7[name] = {
            'sign_idx': d7_sign,
            'sign': SIGNS[d7_sign],
            'house': house,
            'lord': SIGN_LORDS[SIGNS[d7_sign]],
        }
    return d7


def compute_shashtiamsha(planets_data, asc_lon):
    """D60 — Shashtiamsha chart. Each sign divided into 60 parts of 0°30'."""
    d60 = {}
    part_size = 0.5  # 30 minutes = 0.5 degrees
    asc_sign_idx = int(asc_lon / 30) % 12
    asc_deg = asc_lon % 30
    asc_part = int(asc_deg / part_size)
    if asc_part > 59:
        asc_part = 59
    # D60: for odd signs start from same sign, for even signs start from 7th
    if asc_sign_idx % 2 == 0:
        d60_asc = (asc_sign_idx + (asc_part * 1) % 12) % 12
    else:
        d60_asc = (asc_sign_idx + 6 + (asc_part * 1) % 12) % 12
    d60['ascendant'] = {'sign_idx': d60_asc, 'sign': SIGNS[d60_asc]}

    for name in PLANETS:
        lon = planets_data[name]['longitude']
        sign_idx = int(lon / 30) % 12
        deg = lon % 30
        part = int(deg / part_size)
        if part > 59:
            part = 59
        if sign_idx % 2 == 0:
            d60_sign = (sign_idx + part) % 12
        else:
            d60_sign = (sign_idx + 6 + part) % 12
        house = ((d60_sign - d60_asc) % 12) + 1
        d60[name] = {
            'sign_idx': d60_sign,
            'sign': SIGNS[d60_sign],
            'house': house,
            'lord': SIGN_LORDS[SIGNS[d60_sign]],
        }
    return d60


def compute_vimshottari(moon_lon, year, month, day, hour, minute, tz_str):
    """
    Calculate Vimshottari Dasha timeline from Moon's nakshatra position.
    Returns list of Mahadashas with start/end dates and Antardashas.
    """
    nak_idx, pada, deg_in_nak = lon_to_nakshatra(moon_lon)
    nak_lord = NAKSHATRA_LORDS[nak_idx]

    # Proportion of nakshatra already traversed
    traversed = deg_in_nak / NAKSHATRA_SPAN
    remaining = 1 - traversed

    # Find starting dasha lord in the cycle
    start_idx = DASHA_ORDER.index(nak_lord)

    # Birth datetime
    tz = pytz.timezone(tz_str)
    birth_dt = tz.localize(datetime(year, month, day, hour, minute))

    # First dasha: remaining portion of current nakshatra lord's dasha
    dashas = []
    current_date = birth_dt

    for i in range(9):  # 9 dashas complete one cycle
        lord_idx = (start_idx + i) % 9
        lord = DASHA_ORDER[lord_idx]
        total_years = DASHA_YEARS[lord]

        if i == 0:
            # First dasha: only remaining portion
            effective_years = total_years * remaining
        else:
            effective_years = total_years

        effective_days = effective_years * 365.25
        end_date = current_date + timedelta(days=effective_days)

        # Compute Antardashas (sub-periods)
        antardashas = compute_antardashas(lord, current_date, end_date, effective_years)

        dashas.append({
            'lord': lord,
            'start': current_date,
            'end': end_date,
            'years': effective_years,
            'is_current': False,
            'antardashas': antardashas,
        })

        current_date = end_date

    # Continue for next cycle if needed (for 120-year coverage)
    # Add one more complete cycle
    for i in range(9):
        lord_idx = (start_idx + i) % 9
        lord = DASHA_ORDER[lord_idx]
        total_years = DASHA_YEARS[lord]
        effective_days = total_years * 365.25
        end_date = current_date + timedelta(days=effective_days)
        antardashas = compute_antardashas(lord, current_date, end_date, total_years)
        dashas.append({
            'lord': lord,
            'start': current_date,
            'end': end_date,
            'years': total_years,
            'is_current': False,
            'antardashas': antardashas,
        })
        current_date = end_date

    # Mark current dasha
    now = datetime.now(tz)
    for d in dashas:
        if d['start'] <= now < d['end']:
            d['is_current'] = True
            for ad in d['antardashas']:
                if ad['start'] <= now < ad['end']:
                    ad['is_current'] = True
                    break
            break

    return {
        'moon_nakshatra': NAKSHATRAS[nak_idx],
        'moon_nak_lord': nak_lord,
        'balance_at_birth': remaining,
        'dashas': dashas,
    }


def compute_antardashas(maha_lord, start, end, maha_years):
    """Compute Antardasha (sub-periods) within a Mahadasha."""
    maha_idx = DASHA_ORDER.index(maha_lord)
    total_days = (end - start).total_seconds() / 86400
    antardashas = []
    current = start

    for i in range(9):
        antar_idx = (maha_idx + i) % 9
        antar_lord = DASHA_ORDER[antar_idx]
        antar_years = DASHA_YEARS[antar_lord]
        # Antardasha duration = (Maha years * Antar years / 120) proportioned
        proportion = antar_years / TOTAL_DASHA_YEARS
        antar_days = total_days * proportion
        antar_end = current + timedelta(days=antar_days)

        antardashas.append({
            'lord': antar_lord,
            'start': current,
            'end': antar_end,
            'is_current': False,
        })
        current = antar_end

    return antardashas


def find_current_dasha(dashas):
    """Find the currently running Mahadasha and Antardasha."""
    for d in dashas['dashas']:
        if d['is_current']:
            current_antar = None
            for ad in d['antardashas']:
                if ad.get('is_current'):
                    current_antar = ad
                    break
            return d, current_antar
    return None, None
