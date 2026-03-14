"""
Yoga Identification — Classical Vedic Astrology Yogas
Comprehensive detection: Raj Yogas (conjunction + aspect), Dhana Yogas,
Pancha Mahapurusha, Solar Yogas, Chandra Yogas, Kartari Yogas,
planetary dignity yogas, and challenging combinations.
"""

from constants import *


def identify_all_yogas(chart):
    """Master function: identify all yogas in the chart."""
    yogas = []
    yogas.extend(pancha_mahapurusha(chart))
    yogas.extend(gajakesari(chart))
    yogas.extend(raj_yogas(chart))
    yogas.extend(dhana_yogas(chart))
    yogas.extend(viparita_raj_yogas(chart))
    yogas.extend(neecha_bhanga(chart))
    yogas.extend(budhaditya(chart))
    yogas.extend(chandra_yogas(chart))
    yogas.extend(kemadruma(chart))
    yogas.extend(saraswati_yoga(chart))
    yogas.extend(mahabhagya(chart))
    yogas.extend(adhi_yoga(chart))
    yogas.extend(dharma_karmadhipati(chart))
    yogas.extend(parivartana(chart))
    yogas.extend(solar_yogas(chart))
    yogas.extend(amala_yoga(chart))
    yogas.extend(chandra_mangal(chart))
    yogas.extend(exalted_planet_yogas(chart))
    yogas.extend(lord_in_own_house(chart))
    yogas.extend(kartari_yogas(chart))
    yogas.extend(kahala_yoga(chart))
    yogas.extend(shubha_yoga(chart))
    yogas.extend(rahu_saturn_yoga(chart))
    yogas.extend(jupiter_aspect_benefics(chart))
    yogas.extend(malefic_in_upachaya(chart))
    yogas.extend(retrograde_yogas(chart))
    yogas.extend(negative_yogas(chart))
    return yogas


# ── Helpers ───────────────────────────────────────────────────

def _get_house_lord(chart, house_num):
    return chart['houses'][house_num]['lord']

def _planet_house(chart, planet):
    return chart['planets'][planet]['house']

def _planet_sign(chart, planet):
    return chart['planets'][planet]['sign']

def _planet_sign_idx(chart, planet):
    return chart['planets'][planet]['sign_idx']

def _is_kendra(house):
    return house in [1, 4, 7, 10]

def _is_trikona(house):
    return house in [1, 5, 9]

def _is_dusthana(house):
    return house in [6, 8, 12]

def _is_upachaya(house):
    return house in [3, 6, 10, 11]

def _lords_of(chart, houses):
    return [_get_house_lord(chart, h) for h in houses]

def _aspects_sign(planet_name, planet_sign_idx):
    """Return list of sign indices aspected by this planet."""
    aspected = []
    # All planets aspect 7th
    aspected.append((planet_sign_idx + 6) % 12)
    if planet_name in SPECIAL_ASPECTS:
        for offset in SPECIAL_ASPECTS[planet_name]:
            aspected.append((planet_sign_idx + offset - 1) % 12)
    return aspected

def _planet_aspects_planet(chart, p1, p2):
    """Check if p1 aspects p2 (by sign-based Graha Drishti)."""
    p1_sign = _planet_sign_idx(chart, p1)
    p2_sign = _planet_sign_idx(chart, p2)
    return p2_sign in _aspects_sign(p1, p1_sign)

def _mutual_aspect(chart, p1, p2):
    """Check if two planets mutually aspect each other."""
    return _planet_aspects_planet(chart, p1, p2) and _planet_aspects_planet(chart, p2, p1)

def _conjunct(chart, p1, p2):
    """Check if two planets are in the same house."""
    return _planet_house(chart, p1) == _planet_house(chart, p2)

def _connected(chart, p1, p2):
    """Check if two planets are conjunct OR have mutual aspect OR one aspects the other."""
    if _conjunct(chart, p1, p2):
        return 'conjunction'
    if _mutual_aspect(chart, p1, p2):
        return 'mutual aspect'
    if _planet_aspects_planet(chart, p1, p2):
        return f'{p1} aspects {p2}'
    if _planet_aspects_planet(chart, p2, p1):
        return f'{p2} aspects {p1}'
    return None


# ── Pancha Mahapurusha ────────────────────────────────────────

def pancha_mahapurusha(chart):
    yogas = []
    yoga_names = {
        'Mars': ('Ruchaka', 'Courage, leadership, military success, physical strength'),
        'Mercury': ('Bhadra', 'Intelligence, eloquence, commercial success, learning'),
        'Jupiter': ('Hamsa', 'Wisdom, spirituality, righteousness, respected by all'),
        'Venus': ('Malavya', 'Luxury, beauty, artistic talent, marital happiness'),
        'Saturn': ('Sasa', 'Authority, discipline, political power, command over masses'),
    }
    for planet, (name, effect) in yoga_names.items():
        p = chart['planets'][planet]
        if _is_kendra(p['house']) and p['dignity'] in ('Exalted', 'Own Sign', 'Moolatrikona'):
            yogas.append({
                'name': f'{name} Yoga (Pancha Mahapurusha)',
                'type': 'Pancha Mahapurusha',
                'planets': [planet],
                'strength': 'Strong',
                'effect': effect,
            })
    return yogas


# ── Gajakesari ────────────────────────────────────────────────

def gajakesari(chart):
    yogas = []
    moon_sign = chart['planets']['Moon']['sign_idx']
    jup_sign = chart['planets']['Jupiter']['sign_idx']
    diff = (jup_sign - moon_sign) % 12
    if diff in [0, 3, 6, 9]:
        strength = 'Strong'
        if chart['planets']['Jupiter']['dignity'] in ('Debilitated', 'Enemy'):
            strength = 'Weak'
        yogas.append({
            'name': 'Gajakesari Yoga',
            'type': 'Wealth & Fame',
            'planets': ['Jupiter', 'Moon'],
            'strength': strength,
            'effect': 'Fame, wealth, intelligence, lasting reputation. '
                      'Person commands respect and leaves a legacy.',
        })
    return yogas


# ── Raj Yogas (conjunction + aspect) ─────────────────────────

def raj_yogas(chart):
    yogas = []
    kendra_houses = [1, 4, 7, 10]
    trikona_houses = [1, 5, 9]

    kendra_lords = set(_lords_of(chart, kendra_houses))
    trikona_lords = set(_lords_of(chart, trikona_houses))

    # Yogakarakas: planet that lords both kendra and trikona
    yogakarakas = kendra_lords & trikona_lords
    for planet in yogakarakas:
        if planet not in ('Rahu', 'Ketu'):
            yogas.append({
                'name': f'Yogakaraka — {planet}',
                'type': 'Raj Yoga',
                'planets': [planet],
                'strength': 'Strong',
                'effect': f'{planet} is lord of both kendra and trikona, making it '
                          f'the most benefic planet for this ascendant.',
            })

    # Kendra lord + Trikona lord connected (conjunction, aspect, or one-way aspect)
    checked = set()
    for kl in kendra_lords:
        for tl in trikona_lords:
            if kl == tl:
                continue
            if kl in ('Rahu', 'Ketu') or tl in ('Rahu', 'Ketu'):
                continue
            pair = tuple(sorted([kl, tl]))
            if pair in checked:
                continue

            connection = _connected(chart, kl, tl)
            if connection:
                checked.add(pair)
                # Determine which is kendra lord and which is trikona lord
                kl_houses = [h for h in kendra_houses if _get_house_lord(chart, h) == kl]
                tl_houses = [h for h in trikona_houses if _get_house_lord(chart, h) == tl]
                kl_str = ','.join(str(h) for h in kl_houses)
                tl_str = ','.join(str(h) for h in tl_houses)

                strength = 'Strong' if connection == 'conjunction' else 'Moderate'

                yogas.append({
                    'name': f'Raj Yoga — {kl} (H{kl_str}L) + {tl} (H{tl_str}L)',
                    'type': 'Raj Yoga',
                    'planets': list(pair),
                    'strength': strength,
                    'effect': f'Kendra lord {kl} and trikona lord {tl} connected by {connection}. '
                              f'Brings power, status, and success.',
                })
    return yogas


# ── Dhana Yogas (comprehensive) ──────────────────────────────

def dhana_yogas(chart):
    yogas = []
    l2 = _get_house_lord(chart, 2)
    l5 = _get_house_lord(chart, 5)
    l9 = _get_house_lord(chart, 9)
    l11 = _get_house_lord(chart, 11)

    checked_pairs = set()

    # All pairwise connections among wealth lords (2, 5, 9, 11)
    wealth_combos = [
        (2, 11, 'Stored wealth + gains'),
        (2, 5, 'Wealth + past merit/speculation'),
        (2, 9, 'Wealth + fortune/dharma'),
        (5, 9, 'Past merit + fortune (Lakshmi variant)'),
        (5, 11, 'Creativity/merit + gains'),
        (9, 11, 'Fortune + fulfillment of desires'),
    ]

    for h1, h2, desc in wealth_combos:
        lord1 = _get_house_lord(chart, h1)
        lord2 = _get_house_lord(chart, h2)
        if lord1 == lord2:
            continue
        if lord1 in ('Rahu', 'Ketu') or lord2 in ('Rahu', 'Ketu'):
            continue
        pair = tuple(sorted([lord1, lord2]))
        if pair in checked_pairs:
            continue

        connection = _connected(chart, lord1, lord2)
        if connection:
            checked_pairs.add(pair)
            strength = 'Strong' if connection == 'conjunction' else 'Moderate'
            yogas.append({
                'name': f'Dhana Yoga — {lord1} ({h1}L) + {lord2} ({h2}L)',
                'type': 'Dhana Yoga',
                'planets': list(pair),
                'strength': strength,
                'effect': f'{desc}. Connected by {connection}. Financial prosperity.',
            })

    # 2nd lord in 2nd house (own house wealth)
    if l2 not in ('Rahu', 'Ketu'):
        l2_house = _planet_house(chart, l2)
        l2_dignity = chart['planets'][l2]['dignity']
        if l2_house == 2:
            yogas.append({
                'name': f'Dhana Yoga — {l2} (2L in 2H)',
                'type': 'Dhana Yoga',
                'planets': [l2],
                'strength': 'Strong' if l2_dignity in ('Own Sign', 'Exalted', 'Moolatrikona') else 'Moderate',
                'effect': f'2nd lord in its own house. Strong foundation for wealth '
                          f'accumulation, stable family finances. {l2} in {l2_dignity} makes it even stronger.'
                          if l2_dignity in ('Own Sign', 'Exalted') else
                          f'2nd lord in its own house. Good wealth potential.',
            })

    # 11th lord in 11th (gains lord in gains house)
    if l11 not in ('Rahu', 'Ketu'):
        l11_house = _planet_house(chart, l11)
        if l11_house == 11:
            yogas.append({
                'name': f'Dhana Yoga — {l11} (11L in 11H)',
                'type': 'Dhana Yoga',
                'planets': [l11],
                'strength': 'Strong',
                'effect': f'11th lord in its own house. Steady gains and '
                          f'fulfillment of desires.',
            })

    # Lakshmi Yoga: 9th lord in kendra in own/exalted
    if l9 not in ('Rahu', 'Ketu'):
        l9_house = _planet_house(chart, l9)
        l9_dignity = chart['planets'][l9]['dignity']
        if _is_kendra(l9_house) and l9_dignity in ('Exalted', 'Own Sign', 'Moolatrikona'):
            yogas.append({
                'name': f'Lakshmi Yoga — {l9}',
                'type': 'Dhana Yoga',
                'planets': [l9],
                'strength': 'Strong',
                'effect': 'Great wealth, fortune, and prosperity. '
                          '9th lord strong in kendra blesses with abundance.',
            })

    return yogas


# ── Viparita Raj Yogas ───────────────────────────────────────

def viparita_raj_yogas(chart):
    yogas = []
    dusthana_lords = {h: _get_house_lord(chart, h) for h in [6, 8, 12]}
    for h, lord in dusthana_lords.items():
        if lord in ('Rahu', 'Ketu'):
            continue
        lord_in = _planet_house(chart, lord)
        if _is_dusthana(lord_in) and lord_in != h:
            names = {6: 'Harsha', 8: 'Sarala', 12: 'Vimala'}
            yogas.append({
                'name': f'{names.get(h, "Viparita")} Raj Yoga — {lord} ({h}L in {lord_in}H)',
                'type': 'Viparita Raj Yoga',
                'planets': [lord],
                'strength': 'Moderate',
                'effect': f'Dusthana lord in another dusthana. Success through '
                          f'adversity, overcoming enemies/obstacles. Unexpected gains.',
            })
    return yogas


# ── Neecha Bhanga Raj Yoga ────────────────────────────────────

def neecha_bhanga(chart):
    yogas = []
    for name in PLANETS:
        p = chart['planets'][name]
        if p['dignity'] != 'Debilitated':
            continue
        cancelled = False
        reasons = []
        deb_sign = p['sign']
        deb_lord = SIGN_LORDS[deb_sign]
        if deb_lord in chart['planets']:
            if _is_kendra(_planet_house(chart, deb_lord)):
                cancelled = True
                reasons.append(f'{deb_lord} (lord of {deb_sign}) in kendra')
        if name in EXALTATION:
            ex_sign = EXALTATION[name][0]
            ex_lord = SIGN_LORDS[ex_sign]
            if ex_lord in chart['planets'] and _is_kendra(_planet_house(chart, ex_lord)):
                cancelled = True
                reasons.append(f'{ex_lord} (lord of exaltation sign {ex_sign}) in kendra')
        if cancelled:
            yogas.append({
                'name': f'Neecha Bhanga Raj Yoga — {name}',
                'type': 'Neecha Bhanga',
                'planets': [name],
                'strength': 'Strong',
                'effect': f'{name} debilitated but cancelled: {"; ".join(reasons)}. '
                          f'Transforms weakness into strength after initial struggles.',
            })
    return yogas


# ── Budhaditya Yoga ──────────────────────────────────────────

def budhaditya(chart):
    yogas = []
    if _conjunct(chart, 'Sun', 'Mercury'):
        h = _planet_house(chart, 'Sun')
        strength = 'Strong' if _is_kendra(h) or _is_trikona(h) else 'Moderate'
        if chart['planets']['Mercury']['is_combust']:
            strength = 'Weak (Mercury combust)'
        yogas.append({
            'name': 'Budhaditya Yoga',
            'type': 'Intelligence',
            'planets': ['Sun', 'Mercury'],
            'strength': strength,
            'effect': 'Intelligence, analytical ability, fame through intellect. '
                      'Strong communication skills and sharp mind.',
        })
    return yogas


# ── Chandra Yogas (Sunapha, Anapha, Durdhura) ────────────────

def chandra_yogas(chart):
    yogas = []
    moon_sign = chart['planets']['Moon']['sign_idx']
    sign_2nd = (moon_sign + 1) % 12
    sign_12th = (moon_sign - 1) % 12

    exclude = ('Moon', 'Rahu', 'Ketu')
    planets_2nd = [n for n in PLANETS if n not in exclude
                   and chart['planets'][n]['sign_idx'] == sign_2nd]
    planets_12th = [n for n in PLANETS if n not in exclude
                    and chart['planets'][n]['sign_idx'] == sign_12th]

    if planets_2nd and not planets_12th:
        yogas.append({
            'name': f'Sunapha Yoga ({", ".join(planets_2nd)} in 2nd from Moon)',
            'type': 'Chandra Yoga',
            'planets': planets_2nd + ['Moon'],
            'strength': 'Moderate',
            'effect': 'Self-made wealth, good intelligence. Earns through own efforts.',
        })
    elif planets_12th and not planets_2nd:
        yogas.append({
            'name': f'Anapha Yoga ({", ".join(planets_12th)} in 12th from Moon)',
            'type': 'Chandra Yoga',
            'planets': planets_12th + ['Moon'],
            'strength': 'Moderate',
            'effect': 'Good reputation, healthy body, comfortable life.',
        })
    elif planets_2nd and planets_12th:
        yogas.append({
            'name': f'Durdhura Yoga (planets on both sides of Moon)',
            'type': 'Chandra Yoga',
            'planets': planets_2nd + planets_12th + ['Moon'],
            'strength': 'Strong',
            'effect': 'Wealth, vehicles, generous nature. Well-supported life with comforts.',
        })
    return yogas


# ── Kemadruma ─────────────────────────────────────────────────

def kemadruma(chart):
    yogas = []
    moon_sign = chart['planets']['Moon']['sign_idx']
    sign_2nd = (moon_sign + 1) % 12
    sign_12th = (moon_sign - 1) % 12
    planets_around = [n for n in PLANETS if n not in ('Moon', 'Rahu', 'Ketu')
                      and chart['planets'][n]['sign_idx'] in (sign_2nd, sign_12th)]
    if not planets_around:
        moon_house = _planet_house(chart, 'Moon')
        cancelled = _is_kendra(moon_house)
        if cancelled:
            yogas.append({
                'name': 'Kemadruma Yoga (Cancelled)',
                'type': 'Cancelled Negative',
                'planets': ['Moon'],
                'strength': 'Cancelled',
                'effect': 'Kemadruma formed but cancelled by Moon in kendra. '
                          'Initial struggles overcome.',
            })
        else:
            yogas.append({
                'name': 'Kemadruma Yoga',
                'type': 'Negative',
                'planets': ['Moon'],
                'strength': 'Active',
                'effect': 'Loneliness, poverty, mental distress. Moon unsupported. '
                          'Remedies recommended.',
            })
    return yogas


# ── Saraswati Yoga ────────────────────────────────────────────

def saraswati_yoga(chart):
    yogas = []
    required = ['Jupiter', 'Venus', 'Mercury']
    all_good = all(
        _is_kendra(_planet_house(chart, p)) or _is_trikona(_planet_house(chart, p)) or _planet_house(chart, p) == 2
        for p in required
    )
    if all_good:
        yogas.append({
            'name': 'Saraswati Yoga',
            'type': 'Knowledge & Arts',
            'planets': required,
            'strength': 'Strong',
            'effect': 'Mastery of arts, music, literature, and learning. '
                      'Highly educated, eloquent, and wise.',
        })
    return yogas


# ── Mahabhagya Yoga ───────────────────────────────────────────

def mahabhagya(chart):
    yogas = []
    sun_sign = chart['planets']['Sun']['sign_idx']
    moon_sign = chart['planets']['Moon']['sign_idx']
    asc_sign = chart['ascendant']['sign_idx']
    hour = chart['birth']['hour']
    is_day = 6 <= hour < 18

    # Traditional: odd signs = Aries(1), Gemini(3), Leo(5)... (1-indexed odd)
    # In 0-indexed: 0,2,4,6,8,10 are traditionally odd signs
    if is_day:
        if asc_sign % 2 == 0 and sun_sign % 2 == 0 and moon_sign % 2 == 0:
            yogas.append({
                'name': 'Mahabhagya Yoga (Male)',
                'type': 'Fortune',
                'planets': ['Sun', 'Moon'],
                'strength': 'Strong',
                'effect': 'Great fortune. Long life, leadership, wealth, and fame.',
            })
    else:
        if asc_sign % 2 == 1 and sun_sign % 2 == 1 and moon_sign % 2 == 1:
            yogas.append({
                'name': 'Mahabhagya Yoga (Female)',
                'type': 'Fortune',
                'planets': ['Sun', 'Moon'],
                'strength': 'Strong',
                'effect': 'Great fortune. Long life, virtuous character, wealthy spouse.',
            })
    return yogas


# ── Adhi Yoga ─────────────────────────────────────────────────

def adhi_yoga(chart):
    yogas = []
    moon_sign = chart['planets']['Moon']['sign_idx']
    benefics_in_position = []
    for offset in [5, 6, 7]:
        target_sign = (moon_sign + offset) % 12
        for b in ['Jupiter', 'Venus', 'Mercury']:
            if chart['planets'][b]['sign_idx'] == target_sign:
                benefics_in_position.append(b)
    if len(benefics_in_position) >= 2:
        yogas.append({
            'name': f'Adhi Yoga ({", ".join(benefics_in_position)})',
            'type': 'Power & Status',
            'planets': benefics_in_position,
            'strength': 'Strong' if len(benefics_in_position) == 3 else 'Moderate',
            'effect': 'Leadership, authority, polite nature, defeats enemies. '
                      'Person rises to high position.',
        })
    return yogas


# ── Dharma-Karmadhipati Yoga ─────────────────────────────────

def dharma_karmadhipati(chart):
    yogas = []
    l9 = _get_house_lord(chart, 9)
    l10 = _get_house_lord(chart, 10)
    if l9 in ('Rahu', 'Ketu') or l10 in ('Rahu', 'Ketu'):
        return yogas

    connection = _connected(chart, l9, l10)
    if connection:
        strength = 'Very Strong' if connection == 'conjunction' else 'Strong'
        yogas.append({
            'name': f'Dharma-Karmadhipati Yoga — {l9} (9L) + {l10} (10L)',
            'type': 'Raj Yoga',
            'planets': [l9, l10],
            'strength': strength,
            'effect': f'Union of dharma (9th) and karma (10th) by {connection}. '
                      f'Great success in career aligned with purpose.',
        })

    # Exchange
    h9 = _planet_house(chart, l9)
    h10 = _planet_house(chart, l10)
    if h9 == 10 and h10 == 9:
        yogas.append({
            'name': f'Dharma-Karma Parivartana — {l9} <> {l10}',
            'type': 'Raj Yoga',
            'planets': [l9, l10],
            'strength': 'Very Strong',
            'effect': 'Exchange between 9th and 10th lords. Exceptional career success.',
        })
    return yogas


# ── Parivartana Yoga ──────────────────────────────────────────

def parivartana(chart):
    yogas = []
    checked = set()
    for name in PLANETS:
        if name in ('Rahu', 'Ketu'):
            continue
        p_sign = _planet_sign(chart, name)
        for owned_sign in PLANET_OWNS.get(name, []):
            for other in PLANETS:
                if other == name or other in ('Rahu', 'Ketu'):
                    continue
                if chart['planets'][other]['sign'] == owned_sign:
                    if p_sign in PLANET_OWNS.get(other, []):
                        pair = tuple(sorted([name, other]))
                        if pair not in checked:
                            checked.add(pair)
                            h1 = _planet_house(chart, name)
                            h2 = _planet_house(chart, other)
                            if _is_dusthana(h1) and _is_dusthana(h2):
                                ptype = 'Dainya'
                            elif _is_dusthana(h1) or _is_dusthana(h2):
                                ptype = 'Dainya (mixed)'
                            else:
                                ptype = 'Maha (auspicious)'
                            yogas.append({
                                'name': f'Parivartana Yoga — {name} <> {other} (H{h1} <> H{h2})',
                                'type': f'Parivartana ({ptype})',
                                'planets': list(pair),
                                'strength': 'Strong' if 'Maha' in ptype else 'Mixed',
                                'effect': f'{name} and {other} exchange signs. '
                                          f'Both houses ({h1} and {h2}) mutually strengthen.',
                            })
    return yogas


# ── Solar Yogas (Veshi, Voshi, Ubhayachari) ──────────────────

def solar_yogas(chart):
    """Planets in 2nd and/or 12th from Sun (excluding Moon, Rahu, Ketu)."""
    yogas = []
    sun_sign = chart['planets']['Sun']['sign_idx']
    sign_2nd = (sun_sign + 1) % 12
    sign_12th = (sun_sign - 1) % 12

    exclude = ('Sun', 'Moon', 'Rahu', 'Ketu')
    planets_2nd = [n for n in PLANETS if n not in exclude
                   and chart['planets'][n]['sign_idx'] == sign_2nd]
    planets_12th = [n for n in PLANETS if n not in exclude
                    and chart['planets'][n]['sign_idx'] == sign_12th]

    if planets_2nd and planets_12th:
        yogas.append({
            'name': f'Ubhayachari Yoga (planets on both sides of Sun)',
            'type': 'Solar Yoga',
            'planets': planets_2nd + planets_12th + ['Sun'],
            'strength': 'Strong',
            'effect': 'Surrounded by planetary support. Strong personality, '
                      'leadership, wealth. Well-rounded success.',
        })
    elif planets_2nd:
        # Benefic = Veshi, Malefic = Papa Veshi
        has_benefic = any(p in NATURAL_BENEFICS for p in planets_2nd)
        yoga_name = 'Veshi Yoga' if has_benefic else 'Papa Veshi Yoga'
        effect = ('Truthful, ambitious, balanced nature. Good reputation.' if has_benefic
                  else 'Struggles with authority or father. Hard-working but obstacles.')
        yogas.append({
            'name': f'{yoga_name} ({", ".join(planets_2nd)} in 2nd from Sun)',
            'type': 'Solar Yoga',
            'planets': planets_2nd + ['Sun'],
            'strength': 'Moderate',
            'effect': effect,
        })
    elif planets_12th:
        has_benefic = any(p in NATURAL_BENEFICS for p in planets_12th)
        yoga_name = 'Voshi Yoga' if has_benefic else 'Papa Voshi Yoga'
        effect = ('Charitable, learned, and virtuous. Good speech.' if has_benefic
                  else 'Wicked speech or harsh nature. Needs to channel energy constructively.')
        yogas.append({
            'name': f'{yoga_name} ({", ".join(planets_12th)} in 12th from Sun)',
            'type': 'Solar Yoga',
            'planets': planets_12th + ['Sun'],
            'strength': 'Moderate',
            'effect': effect,
        })
    return yogas


# ── Amala Yoga ────────────────────────────────────────────────

def amala_yoga(chart):
    """Natural benefic in 10th from Lagna or Moon."""
    yogas = []
    asc_sign = chart['ascendant']['sign_idx']
    moon_sign = chart['planets']['Moon']['sign_idx']

    for ref_name, ref_sign in [('Lagna', asc_sign), ('Moon', moon_sign)]:
        tenth_sign = (ref_sign + 9) % 12
        benefics_in_10th = [n for n in ['Jupiter', 'Venus', 'Mercury', 'Moon']
                            if chart['planets'][n]['sign_idx'] == tenth_sign]
        if benefics_in_10th:
            yogas.append({
                'name': f'Amala Yoga ({", ".join(benefics_in_10th)} in 10th from {ref_name})',
                'type': 'Fame & Virtue',
                'planets': benefics_in_10th,
                'strength': 'Moderate',
                'effect': 'Spotless character, fame, and respect. Good deeds bring '
                          'lasting reputation. Charitable and virtuous nature.',
            })
    return yogas


# ── Chandra-Mangal Yoga ──────────────────────────────────────

def chandra_mangal(chart):
    """Moon-Mars conjunction or mutual aspect."""
    yogas = []
    connection = _connected(chart, 'Moon', 'Mars')
    if connection:
        yogas.append({
            'name': f'Chandra-Mangal Yoga ({connection})',
            'type': 'Wealth',
            'planets': ['Moon', 'Mars'],
            'strength': 'Moderate',
            'effect': 'Wealth through entrepreneurship and bold action. '
                      'Earning capacity through courage and emotional intelligence.',
        })
    return yogas


# ── Exalted Planet in Kendra/Trikona ─────────────────────────

def exalted_planet_yogas(chart):
    """Planets exalted in kendras or trikonas — powerful placements."""
    yogas = []
    for name in PLANETS:
        p = chart['planets'][name]
        if p['dignity'] != 'Exalted':
            continue
        h = p['house']
        if _is_kendra(h) or _is_trikona(h):
            yogas.append({
                'name': f'{name} Exalted in House {h}',
                'type': 'Planetary Strength',
                'planets': [name],
                'strength': 'Strong',
                'effect': f'{name} at peak strength in {p["sign"]} (House {h}). '
                          f'{KARAKAS.get(name, "")}. '
                          f'Gives excellent results related to House {h} '
                          f'({HOUSE_SIGNIFICATIONS.get(h, "").split(",")[0].strip().lower()}).',
            })
    return yogas


# ── Lord in Own House ─────────────────────────────────────────

def lord_in_own_house(chart):
    """Any planet sitting in its own sign — strengthens that house."""
    yogas = []
    for h in range(1, 13):
        lord = chart['houses'][h]['lord']
        if lord in ('Rahu', 'Ketu'):
            continue
        lord_house = _planet_house(chart, lord)
        dignity = chart['planets'][lord]['dignity']
        if lord_house == h and dignity in ('Own Sign', 'Moolatrikona'):
            desc = HOUSE_SIGNIFICATIONS.get(h, '')
            yogas.append({
                'name': f'{lord} in Own Sign (House {h})',
                'type': 'Planetary Strength',
                'planets': [lord],
                'strength': 'Strong',
                'effect': f'{lord} strong in its own house. House {h} matters '
                          f'({desc.split(",")[0].strip().lower()}) are well-supported and stable.',
            })
    return yogas


# ── Kartari Yogas (Shubha/Papa) ──────────────────────────────

def kartari_yogas(chart):
    """Shubha Kartari (benefics hemming) or Papa Kartari (malefics hemming) a house."""
    yogas = []
    benefic_names = {'Jupiter', 'Venus', 'Mercury', 'Moon'}
    malefic_names = {'Sun', 'Mars', 'Saturn', 'Rahu', 'Ketu'}

    for h in [1, 5, 7, 9, 10]:  # Check important houses only
        h_sign = chart['houses'][h]['sign_idx']
        prev_sign = (h_sign - 1) % 12
        next_sign = (h_sign + 1) % 12

        planets_prev = set(n for n in PLANETS if chart['planets'][n]['sign_idx'] == prev_sign)
        planets_next = set(n for n in PLANETS if chart['planets'][n]['sign_idx'] == next_sign)

        if not planets_prev or not planets_next:
            continue

        benefics_prev = planets_prev & benefic_names
        benefics_next = planets_next & benefic_names
        malefics_prev = planets_prev & malefic_names
        malefics_next = planets_next & malefic_names

        if benefics_prev and benefics_next and not malefics_prev and not malefics_next:
            yogas.append({
                'name': f'Shubha Kartari Yoga (House {h})',
                'type': 'Protective',
                'planets': list(benefics_prev | benefics_next),
                'strength': 'Strong',
                'effect': f'House {h} ({chart["houses"][h]["sign"]}) hemmed by benefics. '
                          f'Protected and strengthened. Positive results for {HOUSE_SIGNIFICATIONS.get(h, "").split(",")[0].strip().lower()}.',
            })
        elif malefics_prev and malefics_next and not benefics_prev and not benefics_next:
            yogas.append({
                'name': f'Papa Kartari Yoga (House {h})',
                'type': 'Challenging',
                'planets': list(malefics_prev | malefics_next),
                'strength': 'Moderate',
                'effect': f'House {h} ({chart["houses"][h]["sign"]}) hemmed by malefics. '
                          f'Pressure and challenges regarding {HOUSE_SIGNIFICATIONS.get(h, "").split(",")[0].strip().lower()}.',
            })
    return yogas


# ── Kahala Yoga ───────────────────────────────────────────────

def kahala_yoga(chart):
    """4th lord and Jupiter in mutual kendras — strong and bold."""
    yogas = []
    l4 = _get_house_lord(chart, 4)
    if l4 in ('Rahu', 'Ketu') or l4 == 'Jupiter':
        return yogas
    l4_house = _planet_house(chart, l4)
    jup_house = _planet_house(chart, 'Jupiter')
    diff = abs(l4_house - jup_house) % 12
    if diff in [0, 3, 6, 9]:
        yogas.append({
            'name': 'Kahala Yoga',
            'type': 'Strength & Courage',
            'planets': [l4, 'Jupiter'],
            'strength': 'Moderate',
            'effect': 'Bold, courageous, capable of leading. Strong personality '
                      'with determination to achieve goals.',
        })
    return yogas


# ── Shubha Yoga (benefic aspects on key houses) ──────────────

def shubha_yoga(chart):
    """Jupiter aspecting Lagna, Moon, or Sun — protective influence."""
    yogas = []
    jup_sign = chart['planets']['Jupiter']['sign_idx']
    aspected_signs = _aspects_sign('Jupiter', jup_sign)

    # Jupiter aspects Lagna sign
    asc_sign = chart['ascendant']['sign_idx']
    if asc_sign in aspected_signs:
        yogas.append({
            'name': 'Jupiter aspects Lagna',
            'type': 'Protective',
            'planets': ['Jupiter'],
            'strength': 'Moderate',
            'effect': 'Jupiter\'s benevolent gaze on the ascendant. Protects health, '
                      'brings wisdom and optimism to the personality.',
        })

    # Jupiter aspects Moon
    moon_sign = chart['planets']['Moon']['sign_idx']
    if moon_sign in aspected_signs:
        yogas.append({
            'name': 'Jupiter aspects Moon (Gaja Kesari variant)',
            'type': 'Protective',
            'planets': ['Jupiter', 'Moon'],
            'strength': 'Moderate',
            'effect': 'Jupiter protects the mind. Emotional stability, wisdom, '
                      'and good judgment. Reduces negative Moon effects.',
        })

    return yogas


# ── Rahu-Saturn Yoga ──────────────────────────────────────────

def rahu_saturn_yoga(chart):
    """Rahu + Saturn conjunction or Rahu in Saturn's sign."""
    yogas = []
    rahu = chart['planets']['Rahu']
    saturn = chart['planets']['Saturn']

    if _conjunct(chart, 'Rahu', 'Saturn'):
        yogas.append({
            'name': 'Shani-Rahu Conjunction (Shrapit Dosha)',
            'type': 'Karmic',
            'planets': ['Saturn', 'Rahu'],
            'strength': 'Moderate',
            'effect': f'Saturn and Rahu together in House {rahu["house"]}. Past-life karmic debts '
                      f'surface. Delays and unusual obstacles, but also capacity for extraordinary '
                      f'discipline in unconventional fields. Success comes through persistent effort.',
        })

    # Rahu in Saturn's signs (Capricorn/Aquarius) — empowered
    if rahu['sign'] in ('Capricorn', 'Aquarius') and not _conjunct(chart, 'Rahu', 'Saturn'):
        yogas.append({
            'name': f'Empowered Rahu in {rahu["sign"]}',
            'type': 'Planetary Strength',
            'planets': ['Rahu'],
            'strength': 'Moderate',
            'effect': f'Rahu in Saturn\'s sign gains Saturnine discipline and structure. '
                      f'Ambition channeled productively. Good for technology, research, and politics.',
        })

    return yogas


# ── Jupiter Aspecting Benefics ────────────────────────────────

def jupiter_aspect_benefics(chart):
    """Jupiter aspecting Venus, Mercury, or Moon — protective, enriching."""
    yogas = []
    for target in ['Venus', 'Mercury', 'Moon']:
        if target == 'Jupiter':
            continue
        if _planet_aspects_planet(chart, 'Jupiter', target) and not _conjunct(chart, 'Jupiter', target):
            target_data = chart['planets'][target]
            theme = {'Venus': 'love, marriage, and creativity',
                     'Mercury': 'intelligence, communication, and business',
                     'Moon': 'emotions, mind, and public image'}.get(target, '')
            yogas.append({
                'name': f'Jupiter aspects {target}',
                'type': 'Protective',
                'planets': ['Jupiter', target],
                'strength': 'Moderate',
                'effect': f'Jupiter\'s wisdom and expansion blesses {target} in '
                          f'{target_data["sign"]} (House {target_data["house"]}). '
                          f'Enhances {theme}.',
            })
    return yogas


# ── Malefics in Upachaya ──────────────────────────────────────

def malefic_in_upachaya(chart):
    """Mars, Saturn, Rahu in upachaya houses (3, 6, 10, 11) — strength through struggle."""
    yogas = []
    malefics = ['Mars', 'Saturn', 'Rahu']
    for name in malefics:
        p = chart['planets'][name]
        if _is_upachaya(p['house']) and p['house'] != 10:  # H10 covered elsewhere
            yogas.append({
                'name': f'{name} in Upachaya House {p["house"]}',
                'type': 'Growth',
                'planets': [name],
                'strength': 'Moderate',
                'effect': f'Malefic planets improve with time in upachaya houses. '
                          f'{name} in House {p["house"]} gives increasing strength, '
                          f'competitive edge, and ability to overcome opposition as years progress.',
            })
    return yogas


# ── Retrograde Planet Yogas ───────────────────────────────────

def retrograde_yogas(chart):
    """Retrograde planets in strong positions — intensified results."""
    yogas = []
    for name in ['Mars', 'Mercury', 'Jupiter', 'Venus', 'Saturn']:
        p = chart['planets'][name]
        if not p['is_retrograde']:
            continue
        h = p['house']
        if _is_kendra(h) or _is_trikona(h):
            yogas.append({
                'name': f'Retrograde {name} in House {h}',
                'type': 'Intensified',
                'planets': [name],
                'strength': 'Moderate',
                'effect': f'Retrograde {name} in a strong house gives intensified but '
                          f'delayed results. Like a planet going back to finish unfinished '
                          f'business. {KARAKAS.get(name, "").split(",")[0].strip()} themes '
                          f'manifest powerfully after age 30-35.',
            })
    return yogas


# ── Negative / Challenging Yogas ──────────────────────────────

def negative_yogas(chart):
    yogas = []

    # Shakata Yoga: Jupiter in 6/8/12 from Moon
    moon_sign = chart['planets']['Moon']['sign_idx']
    jup_sign = chart['planets']['Jupiter']['sign_idx']
    diff = (jup_sign - moon_sign) % 12
    if diff in [5, 7, 11]:
        yogas.append({
            'name': 'Shakata Yoga',
            'type': 'Challenging',
            'planets': ['Jupiter', 'Moon'],
            'strength': 'Moderate',
            'effect': 'Fluctuations in fortune. Ups and downs like a cart wheel. '
                      'Reduced benefits of Jupiter.',
        })

    # Guru Chandal: Jupiter + Rahu/Ketu
    jup_house = _planet_house(chart, 'Jupiter')
    rahu_house = _planet_house(chart, 'Rahu')
    ketu_house = _planet_house(chart, 'Ketu')
    if jup_house == rahu_house:
        yogas.append({
            'name': 'Guru Chandal Yoga (Jupiter-Rahu)',
            'type': 'Challenging',
            'planets': ['Jupiter', 'Rahu'],
            'strength': 'Moderate',
            'effect': 'Unconventional beliefs, challenges traditions. Can give sudden '
                      'wisdom if Jupiter is strong.',
        })
    if jup_house == ketu_house:
        yogas.append({
            'name': 'Guru Chandal Yoga (Jupiter-Ketu)',
            'type': 'Challenging',
            'planets': ['Jupiter', 'Ketu'],
            'strength': 'Moderate',
            'effect': 'Spiritual confusion or deep mystical insight. Can be positive '
                      'for spiritual seekers.',
        })

    # Grahan Yoga: Sun/Moon with Rahu/Ketu
    sun_house = _planet_house(chart, 'Sun')
    moon_house = _planet_house(chart, 'Moon')
    if sun_house == rahu_house or sun_house == ketu_house:
        node = 'Rahu' if sun_house == rahu_house else 'Ketu'
        yogas.append({
            'name': f'Grahan Yoga (Sun-{node})',
            'type': 'Challenging',
            'planets': ['Sun', node],
            'strength': 'Moderate',
            'effect': 'Father-related challenges, ego struggles, authority issues.',
        })
    if moon_house == rahu_house or moon_house == ketu_house:
        node = 'Rahu' if moon_house == rahu_house else 'Ketu'
        yogas.append({
            'name': f'Grahan Yoga (Moon-{node})',
            'type': 'Challenging',
            'planets': ['Moon', node],
            'strength': 'Moderate',
            'effect': 'Emotional turbulence, anxiety. Strong intuition but restlessness.',
        })

    # Angarak (Mars-Saturn conjunction)
    if _conjunct(chart, 'Mars', 'Saturn'):
        yogas.append({
            'name': 'Angarak Yoga (Mars-Saturn)',
            'type': 'Challenging',
            'planets': ['Mars', 'Saturn'],
            'strength': 'Moderate',
            'effect': 'Conflict between action and patience. Can give iron discipline '
                      'if well-placed.',
        })

    # Kemdrum already handled separately

    # Manglik / Kuja Dosha (Mars in 1, 2, 4, 7, 8, 12)
    mars_house = _planet_house(chart, 'Mars')
    if mars_house in [1, 2, 4, 7, 8, 12]:
        severity = 'Mild' if mars_house in [1, 2] else 'Moderate'
        yogas.append({
            'name': f'Manglik Dosha (Mars in House {mars_house})',
            'type': 'Dosha',
            'planets': ['Mars'],
            'strength': severity,
            'effect': f'Mars in House {mars_house} creates Manglik Dosha. '
                      f'Affects marriage timing and compatibility. '
                      f'{"Considered mild from this house." if severity == "Mild" else "Check spouse chart for cancellation."}',
        })

    return yogas
