"""
Structured Analysis Engine — Generates comprehensive text analysis
from chart data: house analysis, lord placements, strength assessment,
predictive timeline, and life area readings.
"""

from constants import *
from calculator import find_current_dasha


def generate_full_analysis(chart, yogas_list):
    """Generate complete structured analysis text."""
    sections = []
    sections.append(birth_summary(chart))
    sections.append(ascendant_analysis(chart))
    sections.append(planetary_positions_table(chart))
    sections.append(house_analysis(chart))
    sections.append(planetary_strength_summary(chart))
    sections.append(yoga_analysis(yogas_list))
    sections.append(divisional_summary(chart))
    sections.append(dasha_analysis(chart))
    sections.append(life_areas_reading(chart))
    sections.append(predictive_timeline(chart))
    return '\n'.join(sections)


def birth_summary(chart):
    """Section 1: Birth details summary."""
    b = chart['birth']
    asc = chart['ascendant']
    moon = chart['planets']['Moon']
    sun = chart['planets']['Sun']

    name = b.get('name', '')
    lines = [
        '=' * 80,
        '  VEDIC BIRTH CHART ANALYSIS (Parashari System)',
        '=' * 80,
        '',
    ]
    if name:
        lines.append(f"  Name           : {name}")
    lines += [
        f"  Date of Birth  : {b['day']:02d}/{b['month']:02d}/{b['year']}",
        f"  Time of Birth  : {b['hour']:02d}:{b['minute']:02d}",
        f"  Coordinates    : {b['lat']:.4f}°N, {b['lon']:.4f}°E",
        f"  Timezone       : {b['timezone']}",
        f"  Ayanamsa       : Lahiri ({chart['ayanamsa']:.4f}°)",
        '',
        f"  Lagna (Asc)    : {asc['sign']} {asc['degree']:.2f}° — {asc['nakshatra']} Pada {asc['pada']}",
        f"  Moon Sign      : {moon['sign']} {moon['degree']:.2f}° — {moon['nakshatra']} Pada {moon['pada']}",
        f"  Sun Sign       : {sun['sign']} {sun['degree']:.2f}° — {sun['nakshatra']} Pada {sun['pada']}",
        f"  Lagna Lord     : {asc['lord']} in {chart['planets'][asc['lord']]['sign']} (House {chart['planets'][asc['lord']]['house']})",
        '',
    ]
    return '\n'.join(lines)


def ascendant_analysis(chart):
    """Section 2: Detailed ascendant / lagna analysis."""
    asc = chart['ascendant']
    lord = asc['lord']
    lord_data = chart['planets'][lord]

    sign_desc = {
        'Aries': 'Dynamic, pioneering, independent. Natural leader with strong will.',
        'Taurus': 'Stable, sensual, determined. Values comfort, beauty, and security.',
        'Gemini': 'Curious, adaptable, communicative. Quick mind, versatile nature.',
        'Cancer': 'Nurturing, emotional, intuitive. Deep attachment to home and family.',
        'Leo': 'Confident, generous, dramatic. Natural authority and creative expression.',
        'Virgo': 'Analytical, practical, service-oriented. Attention to detail and health.',
        'Libra': 'Diplomatic, aesthetic, partnership-oriented. Seeks balance and harmony.',
        'Scorpio': 'Intense, transformative, secretive. Deep psychological understanding.',
        'Sagittarius': 'Philosophical, adventurous, optimistic. Seeker of truth and meaning.',
        'Capricorn': 'Ambitious, disciplined, responsible. Steady climb toward achievement.',
        'Aquarius': 'Innovative, humanitarian, independent. Unconventional thinker.',
        'Pisces': 'Spiritual, compassionate, imaginative. Connected to the transcendent.',
    }

    lines = [
        '-' * 80,
        '  ASCENDANT (LAGNA) ANALYSIS',
        '-' * 80,
        '',
        f"  {asc['sign']} Ascendant: {sign_desc.get(asc['sign'], '')}",
        '',
        f"  Lagna Lord {lord} is in {lord_data['sign']} (House {lord_data['house']})",
        f"  Dignity: {lord_data['dignity']}",
        f"  Nakshatra: {lord_data['nakshatra']} (lord: {lord_data['nakshatra_lord']})",
    ]

    if lord_data['is_retrograde']:
        lines.append(f"  ** {lord} is RETROGRADE — internalized expression, revisiting past patterns")

    if lord_data.get('is_combust'):
        lines.append(f"  ** {lord} is COMBUST — ego challenges, father themes intertwined with self")

    # Lagna lord placement interpretation
    lord_house = lord_data['house']
    placement_reading = lagna_lord_in_house(lord, lord_house)
    lines.append(f"\n  Lagna Lord in House {lord_house}: {placement_reading}")
    lines.append('')

    return '\n'.join(lines)


def lagna_lord_in_house(lord, house):
    """Interpret lagna lord placement in houses."""
    readings = {
        1: 'Strong self-identity, good health, independent nature. Self-made person.',
        2: 'Focus on wealth, family, and speech. Earnings through own effort. Strong values.',
        3: 'Courageous, good with communication. Sibling bonds important. Short travels.',
        4: 'Attached to home, mother, and comforts. Education important. Emotional security.',
        5: 'Creative, intelligent, children bring joy. Past-life merit supports this life.',
        6: 'Competitive nature, overcoming obstacles. Health awareness. Service-oriented.',
        7: 'Partnership-focused life. Spouse has strong influence. Business acumen.',
        8: 'Transformative life events. Interest in occult/hidden matters. Inheritance possible.',
        9: 'Fortunate placement. Father supportive. Interest in dharma, philosophy, travel.',
        10: 'Career-driven. Strong public image. Achievement and status are central themes.',
        11: 'Gains come easily. Social network is important. Desires tend to be fulfilled.',
        12: 'Spiritual orientation. Foreign connections. May live away from birthplace. Expenses.',
    }
    return readings.get(house, '')


def planetary_positions_table(chart):
    """Section 3: Formatted planetary positions table."""
    lines = [
        '-' * 80,
        '  PLANETARY POSITIONS',
        '-' * 80,
        '',
        f"  {'Planet':<10} {'Sign':<14} {'Degree':>8} {'Nakshatra':<20} {'Pada':>4} {'House':>6} {'Dignity':<14} {'Status':<8}",
        '  ' + '-' * 90,
    ]

    for name in PLANETS:
        p = chart['planets'][name]
        status = []
        if p['is_retrograde']:
            status.append('R')
        if p.get('is_combust'):
            status.append('C')
        status_str = ','.join(status) if status else '—'

        lines.append(
            f"  {name:<10} {p['sign']:<14} {p['degree']:>7.2f}° "
            f"{p['nakshatra']:<20} {p['pada']:>4} {p['house']:>6} "
            f"{p['dignity']:<14} {status_str:<8}"
        )

    lines.append('')
    return '\n'.join(lines)


def house_analysis(chart):
    """Section 4: House-by-house analysis with lords and occupants."""
    lines = [
        '-' * 80,
        '  HOUSE ANALYSIS (BHAVA ANALYSIS)',
        '-' * 80,
        '',
    ]

    for h in range(1, 13):
        hd = chart['houses'][h]
        sig = HOUSE_SIGNIFICATIONS.get(h, '')
        occupants = hd['occupants']
        occ_str = ', '.join(occupants) if occupants else 'Empty'

        lord = hd['lord']
        lord_h = hd['lord_house']
        lord_sign = chart['planets'][lord]['sign'] if lord in chart['planets'] else '?'
        lord_dignity = chart['planets'][lord]['dignity'] if lord in chart['planets'] else '?'

        lines.append(f"  House {h:>2} | {hd['sign']:<13} | Lord: {lord:<8} in H{lord_h} ({lord_sign}, {lord_dignity})")
        lines.append(f"           | Occupants: {occ_str}")
        lines.append(f"           | Signifies: {sig}")

        # Key interpretations for occupied houses
        if occupants:
            for occ in occupants:
                p = chart['planets'][occ]
                note = planet_in_house_note(occ, h, p['dignity'])
                if note:
                    lines.append(f"           | >> {occ}: {note}")

        lines.append('')

    return '\n'.join(lines)


def planet_in_house_note(planet, house, dignity):
    """Brief interpretation note for planet in house."""
    strength = 'well-placed' if dignity in ('Exalted', 'Own Sign', 'Moolatrikona', 'Friendly') else \
               'challenged' if dignity in ('Debilitated', 'Enemy') else 'average'

    key_placements = {
        ('Jupiter', 1): f'Jupiter in 1st ({strength}): Wisdom, optimism, good fortune. Protected life.',
        ('Saturn', 1): f'Saturn in 1st ({strength}): Discipline, delays in early life, mature outlook.',
        ('Mars', 1): f'Mars in 1st ({strength}): Energy, courage, aggressive drive. Manglik consideration.',
        ('Venus', 7): f'Venus in 7th ({strength}): Beautiful spouse, harmonious partnerships.',
        ('Saturn', 7): f'Saturn in 7th ({strength}): Delayed marriage, mature partner, karmic relationships.',
        ('Mars', 7): f'Mars in 7th ({strength}): Passionate partnerships, possible conflicts. Manglik.',
        ('Jupiter', 5): f'Jupiter in 5th ({strength}): Blessed with children, creative intelligence.',
        ('Saturn', 10): f'Saturn in 10th ({strength}): Career through discipline, slow but steady rise.',
        ('Sun', 10): f'Sun in 10th ({strength}): Authority, government favor, leadership career.',
        ('Rahu', 10): f'Rahu in 10th: Ambitious career, unconventional path, foreign connections in work.',
        ('Ketu', 12): f'Ketu in 12th: Spiritual liberation, strong intuition, past-life spiritual merit.',
        ('Moon', 4): f'Moon in 4th ({strength}): Emotional fulfillment, strong mother bond, property.',
    }

    return key_placements.get((planet, house), '')


def planetary_strength_summary(chart):
    """Section 5: Overall planetary strength assessment."""
    lines = [
        '-' * 80,
        '  PLANETARY STRENGTH & DIGNITY',
        '-' * 80,
        '',
    ]

    for name in PLANETS:
        p = chart['planets'][name]
        strengths = []
        weaknesses = []

        # Dignity
        if p['dignity'] in ('Exalted', 'Moolatrikona', 'Own Sign'):
            strengths.append(f"{p['dignity']} in {p['sign']}")
        elif p['dignity'] == 'Debilitated':
            weaknesses.append(f"Debilitated in {p['sign']}")
        elif p['dignity'] == 'Enemy':
            weaknesses.append(f"In enemy sign {p['sign']}")

        # Directional strength
        if name in DIG_BALA and p['house'] == DIG_BALA[name]:
            strengths.append(f"Dig Bala (directional strength) in House {p['house']}")

        # Retrograde
        if p['is_retrograde'] and name not in ('Rahu', 'Ketu'):
            note = 'Retrograde — intensified but internalized energy'
            strengths.append(note)  # Retrograde is not purely negative

        # Combust
        if p.get('is_combust'):
            weaknesses.append(f"Combust (within {p.get('sun_distance', 0):.1f}° of Sun)")

        # House placement
        if p['house'] in (6, 8, 12):
            weaknesses.append(f"In dusthana (House {p['house']})")
        elif p['house'] in (1, 4, 7, 10):
            strengths.append(f"In kendra (House {p['house']})")
        elif p['house'] in (5, 9):
            strengths.append(f"In trikona (House {p['house']})")

        status = 'STRONG' if len(strengths) > len(weaknesses) else \
                 'WEAK' if len(weaknesses) > len(strengths) else 'MODERATE'

        lines.append(f"  {name:<10} [{status}]")
        for s in strengths:
            lines.append(f"    + {s}")
        for w in weaknesses:
            lines.append(f"    - {w}")
        if not strengths and not weaknesses:
            lines.append(f"    ~ Average placement, no special strength or weakness")
        lines.append('')

    return '\n'.join(lines)


def yoga_analysis(yogas_list):
    """Section 6: Yoga analysis with explanations."""
    lines = [
        '-' * 80,
        '  YOGA ANALYSIS',
        '-' * 80,
        '',
    ]

    if not yogas_list:
        lines.append('  No major yogas identified.')
        lines.append('')
        return '\n'.join(lines)

    # Group by type
    by_type = {}
    for y in yogas_list:
        t = y['type']
        by_type.setdefault(t, []).append(y)

    for yoga_type, yogas in by_type.items():
        lines.append(f"  [{yoga_type}]")
        for y in yogas:
            planets_str = ', '.join(y['planets'])
            lines.append(f"    {y['name']}")
            lines.append(f"    Planets: {planets_str} | Strength: {y['strength']}")
            lines.append(f"    Effect: {y['effect']}")
            lines.append('')

    return '\n'.join(lines)


def divisional_summary(chart):
    """Section 7: Summary of key divisional charts."""
    lines = [
        '-' * 80,
        '  DIVISIONAL CHART SUMMARY',
        '-' * 80,
        '',
    ]

    # D9 Navamsha
    d9 = chart['divisional']['D9']
    lines.append('  NAVAMSHA (D9) — Marriage, Dharma, Inner Nature')
    lines.append(f"  D9 Lagna: {d9['ascendant']['sign']}")
    for name in PLANETS:
        d = d9[name]
        lines.append(f"    {name:<10} -> {d['sign']:<13} (House {d['house']}, Lord: {d['lord']})")

    # Check Vargottama (same sign in D1 and D9)
    vargottama = []
    for name in PLANETS:
        if chart['planets'][name]['sign_idx'] == d9[name]['sign_idx']:
            vargottama.append(name)
    if vargottama:
        lines.append(f"\n  Vargottama planets (same sign in D1 & D9): {', '.join(vargottama)}")
        lines.append(f"  >> These planets are especially strong and give consistent results.")

    # Check Pushkara Navamsha for key planets
    lines.append('')

    # D10 Dasamsha
    d10 = chart['divisional']['D10']
    lines.append('  DASAMSHA (D10) — Career, Professional Life')
    lines.append(f"  D10 Lagna: {d10['ascendant']['sign']}")
    for name in PLANETS:
        d = d10[name]
        lines.append(f"    {name:<10} -> {d['sign']:<13} (House {d['house']})")

    lines.append('')

    # D7 Saptamsha
    d7 = chart['divisional']['D7']
    lines.append('  SAPTAMSHA (D7) — Children, Progeny')
    lines.append(f"  D7 Lagna: {d7['ascendant']['sign']}")
    # Just key planets for children
    for name in ['Jupiter', 'Venus', 'Moon', 'Sun', 'Mars']:
        d = d7[name]
        lines.append(f"    {name:<10} -> {d['sign']:<13} (House {d['house']})")

    lines.append('')
    return '\n'.join(lines)


def dasha_analysis(chart):
    """Section 8: Vimshottari Dasha timeline and current period analysis."""
    dashas = chart['dashas']
    lines = [
        '-' * 80,
        '  VIMSHOTTARI DASHA ANALYSIS',
        '-' * 80,
        '',
        f"  Moon Nakshatra: {dashas['moon_nakshatra']}",
        f"  Nakshatra Lord: {dashas['moon_nak_lord']}",
        f"  Balance at Birth: {dashas['balance_at_birth']*100:.1f}% of {dashas['moon_nak_lord']} Mahadasha",
        '',
        '  MAHADASHA TIMELINE:',
        '',
    ]

    current_maha, current_antar = find_current_dasha(dashas)

    for d in dashas['dashas']:
        marker = ' >> ' if d.get('is_current') else '    '
        years_str = f"{d['years']:.1f}y"
        lines.append(
            f"  {marker}{d['lord']:<10} {d['start'].strftime('%d %b %Y')} — "
            f"{d['end'].strftime('%d %b %Y')}  ({years_str})"
        )

    lines.append('')

    if current_maha:
        lines.append(f"  CURRENT PERIOD: {current_maha['lord']} Mahadasha")
        lord = current_maha['lord']
        p = chart['planets'][lord]
        lines.append(f"  {lord} is in {p['sign']} (House {p['house']}), {p['dignity']}")
        lines.append(f"  Nakshatra: {p['nakshatra']}, Pada {p['pada']}")
        lines.append('')

        # Mahadasha lord interpretation
        maha_reading = mahadasha_reading(lord, p['house'], p['dignity'], chart)
        lines.append(f"  Reading: {maha_reading}")
        lines.append('')

        if current_antar:
            lines.append(f"  Current Antardasha: {current_antar['lord']}")
            lines.append(f"  Period: {current_antar['start'].strftime('%d %b %Y')} — "
                        f"{current_antar['end'].strftime('%d %b %Y')}")
            antar_lord = current_antar['lord']
            ap = chart['planets'][antar_lord]
            lines.append(f"  {antar_lord} in {ap['sign']} (House {ap['house']}), {ap['dignity']}")
            antar_reading = antardasha_reading(lord, antar_lord, chart)
            lines.append(f"  Reading: {antar_reading}")
            lines.append('')

        # Upcoming Antardashas
        lines.append('  UPCOMING ANTARDASHAS:')
        found_current = False
        count = 0
        for ad in current_maha['antardashas']:
            if ad.get('is_current'):
                found_current = True
                continue
            if found_current and count < 4:
                lines.append(
                    f"    {ad['lord']:<10} {ad['start'].strftime('%d %b %Y')} — "
                    f"{ad['end'].strftime('%d %b %Y')}"
                )
                count += 1
        lines.append('')

    return '\n'.join(lines)


def mahadasha_reading(lord, house, dignity, chart):
    """Generate reading for Mahadasha lord."""
    themes = KARAKAS.get(lord, '')
    house_sig = HOUSE_SIGNIFICATIONS.get(house, '')

    strength = 'favorable' if dignity in ('Exalted', 'Own Sign', 'Moolatrikona', 'Friendly') else \
               'challenging' if dignity in ('Debilitated', 'Enemy') else 'mixed'

    return (f"The {lord} Mahadasha activates themes of {themes.lower()}. "
            f"Placed in House {house} ({house_sig.split(',')[0].strip().lower()}), "
            f"the period is generally {strength}. "
            f"Events related to House {house} matters will be prominent.")


def antardasha_reading(maha_lord, antar_lord, chart):
    """Generate reading for Antardasha within a Mahadasha."""
    mp = chart['planets'][maha_lord]
    ap = chart['planets'][antar_lord]

    # Check relationship between the two planets
    relationship = 'neutral'
    if antar_lord in NATURAL_FRIENDS.get(maha_lord, []):
        relationship = 'friendly'
    elif antar_lord in NATURAL_ENEMIES.get(maha_lord, []):
        relationship = 'conflicting'

    # Same house = conjunction effect
    if mp['house'] == ap['house']:
        conjunction = f"Both planets in House {mp['house']} intensify each other's themes."
    else:
        conjunction = f"{maha_lord} (H{mp['house']}) and {antar_lord} (H{ap['house']}) connect these two life areas."

    return (f"{maha_lord}-{antar_lord} period. Their relationship is {relationship}. "
            f"{conjunction} "
            f"{antar_lord} themes ({KARAKAS.get(antar_lord, 'general').split(',')[0].strip().lower()}) "
            f"will color this sub-period.")


def life_areas_reading(chart):
    """Section 9: Key life area readings — career, marriage, wealth, health."""
    lines = [
        '-' * 80,
        '  LIFE AREAS READING',
        '-' * 80,
        '',
    ]

    # Career (10th house, 10th lord, planets in 10th, D10)
    lines.append('  CAREER & PROFESSION')
    h10 = chart['houses'][10]
    l10 = h10['lord']
    l10_data = chart['planets'][l10]
    lines.append(f"  10th House: {h10['sign']} | Lord: {l10} in House {h10['lord_house']} ({l10_data['dignity']})")
    if h10['occupants']:
        lines.append(f"  Planets in 10th: {', '.join(h10['occupants'])}")
    lines.append(f"  Career nature: {career_indication(chart)}")
    lines.append('')

    # Marriage (7th house, Venus, Jupiter, D9)
    lines.append('  MARRIAGE & PARTNERSHIPS')
    h7 = chart['houses'][7]
    l7 = h7['lord']
    l7_data = chart['planets'][l7]
    lines.append(f"  7th House: {h7['sign']} | Lord: {l7} in House {h7['lord_house']} ({l7_data['dignity']})")
    if h7['occupants']:
        lines.append(f"  Planets in 7th: {', '.join(h7['occupants'])}")
    venus = chart['planets']['Venus']
    lines.append(f"  Venus: {venus['sign']} (House {venus['house']}, {venus['dignity']})")
    d9_7_sign = chart['divisional']['D9']['ascendant']['sign_idx']
    d9_7_sign = (d9_7_sign + 6) % 12
    lines.append(f"  D9 7th sign: {SIGNS[d9_7_sign]}")
    lines.append(f"  Marriage outlook: {marriage_indication(chart)}")
    lines.append('')

    # Wealth (2nd, 11th houses)
    lines.append('  WEALTH & FINANCES')
    h2 = chart['houses'][2]
    h11 = chart['houses'][11]
    lines.append(f"  2nd House: {h2['sign']} | Lord: {h2['lord']} in House {h2['lord_house']}")
    lines.append(f"  11th House: {h11['sign']} | Lord: {h11['lord']} in House {h11['lord_house']}")
    lines.append(f"  Wealth outlook: {wealth_indication(chart)}")
    lines.append('')

    # Health (1st, 6th houses)
    lines.append('  HEALTH')
    h1 = chart['houses'][1]
    h6 = chart['houses'][6]
    lines.append(f"  Lagna: {h1['sign']} | 6th House: {h6['sign']} (Lord: {h6['lord']} in House {h6['lord_house']})")
    if h6['occupants']:
        lines.append(f"  Planets in 6th: {', '.join(h6['occupants'])}")
    lines.append(f"  Health areas: {health_indication(chart)}")
    lines.append('')

    return '\n'.join(lines)


def career_indication(chart):
    """Brief career reading based on 10th house and lord."""
    h10 = chart['houses'][10]
    lord = h10['lord']
    sign = h10['sign']

    career_by_sign = {
        'Aries': 'Leadership, military, sports, surgery, engineering',
        'Taurus': 'Finance, agriculture, luxury goods, hospitality, art',
        'Gemini': 'Communication, writing, media, trading, teaching',
        'Cancer': 'Nurturing professions, hospitality, real estate, public dealing',
        'Leo': 'Government, politics, entertainment, management, royalty',
        'Virgo': 'Healthcare, accounting, analysis, editing, service industry',
        'Libra': 'Law, diplomacy, fashion, beauty, partnerships',
        'Scorpio': 'Research, investigation, medicine, occult, insurance',
        'Sagittarius': 'Education, philosophy, law, religion, foreign trade',
        'Capricorn': 'Administration, mining, manufacturing, traditional business',
        'Aquarius': 'Technology, social work, innovation, networking, science',
        'Pisces': 'Healing, arts, spirituality, charity, film, photography',
    }
    return career_by_sign.get(sign, 'Various fields depending on other factors')


def marriage_indication(chart):
    """Brief marriage reading."""
    h7 = chart['houses'][7]
    lord = h7['lord']
    lord_house = h7['lord_house']
    venus = chart['planets']['Venus']

    notes = []
    if lord_house in (1, 4, 7, 10):
        notes.append('7th lord in kendra — stable marriage prospects')
    elif lord_house in (6, 8, 12):
        notes.append('7th lord in dusthana — some challenges in partnerships')

    if venus['dignity'] in ('Exalted', 'Own Sign'):
        notes.append('Venus strong — harmonious relationships')
    elif venus['dignity'] == 'Debilitated':
        notes.append('Venus debilitated — relationship lessons to learn')

    return '. '.join(notes) if notes else 'Average marriage prospects, check dasha timing for marriage period.'


def wealth_indication(chart):
    """Brief wealth reading."""
    h2_lord = chart['houses'][2]['lord']
    h11_lord = chart['houses'][11]['lord']
    h2_lord_h = chart['houses'][2]['lord_house']
    h11_lord_h = chart['houses'][11]['lord_house']

    notes = []
    if h2_lord_h in (1, 2, 5, 9, 11):
        notes.append(f'2nd lord in House {h2_lord_h} — good for wealth accumulation')
    if h11_lord_h in (1, 2, 5, 9, 11):
        notes.append(f'11th lord in House {h11_lord_h} — favorable for gains')
    if not notes:
        notes.append('Moderate wealth potential, enhanced during favorable dashas')

    return '. '.join(notes)


def health_indication(chart):
    """Brief health reading based on ascendant and 6th house."""
    asc_sign = chart['ascendant']['sign']
    vulnerable_areas = {
        'Aries': 'Head, brain, blood pressure',
        'Taurus': 'Throat, thyroid, neck',
        'Gemini': 'Lungs, arms, nervous system',
        'Cancer': 'Stomach, chest, digestion',
        'Leo': 'Heart, spine, blood circulation',
        'Virgo': 'Intestines, digestion, nerves',
        'Libra': 'Kidneys, lower back, skin',
        'Scorpio': 'Reproductive system, chronic conditions',
        'Sagittarius': 'Hips, liver, thighs',
        'Capricorn': 'Knees, bones, joints, teeth',
        'Aquarius': 'Ankles, circulation, nervous disorders',
        'Pisces': 'Feet, lymphatic system, immunity',
    }
    return f"Watch areas: {vulnerable_areas.get(asc_sign, 'General health awareness')}"


def predictive_timeline(chart):
    """Section 10: Predictive timeline based on upcoming dashas."""
    dashas = chart['dashas']
    current_maha, current_antar = find_current_dasha(dashas)

    lines = [
        '-' * 80,
        '  PREDICTIVE TIMELINE',
        '-' * 80,
        '',
    ]

    if not current_maha:
        lines.append('  Unable to determine current dasha period.')
        return '\n'.join(lines)

    lines.append(f"  Currently running: {current_maha['lord']} Mahadasha")
    if current_antar:
        lines.append(f"  Sub-period: {current_antar['lord']} Antardasha")
    lines.append('')

    # Upcoming Antardashas with predictions
    found_current = False
    lines.append('  UPCOMING PERIODS & THEMES:')
    lines.append('')

    for ad in current_maha['antardashas']:
        if ad.get('is_current'):
            found_current = True
            lines.append(f"  ** NOW: {current_maha['lord']}-{ad['lord']} **")
            lines.append(f"     {ad['start'].strftime('%b %Y')} to {ad['end'].strftime('%b %Y')}")
            prediction = period_prediction(current_maha['lord'], ad['lord'], chart)
            lines.append(f"     {prediction}")
            lines.append('')
            continue
        if found_current:
            lines.append(f"  NEXT: {current_maha['lord']}-{ad['lord']}")
            lines.append(f"     {ad['start'].strftime('%b %Y')} to {ad['end'].strftime('%b %Y')}")
            prediction = period_prediction(current_maha['lord'], ad['lord'], chart)
            lines.append(f"     {prediction}")
            lines.append('')

    # Next Mahadasha
    found_maha = False
    for d in dashas['dashas']:
        if d.get('is_current'):
            found_maha = True
            continue
        if found_maha:
            lines.append(f"  NEXT MAHADASHA: {d['lord']}")
            lines.append(f"  Period: {d['start'].strftime('%b %Y')} to {d['end'].strftime('%b %Y')}")
            p = chart['planets'][d['lord']]
            lines.append(f"  {d['lord']} in {p['sign']} (House {p['house']}), {p['dignity']}")
            lines.append(f"  Themes: {KARAKAS.get(d['lord'], 'General life themes')}")
            lines.append('')
            break

    lines.append('=' * 80)
    lines.append('  End of Analysis')
    lines.append('=' * 80)
    return '\n'.join(lines)


def period_prediction(maha_lord, antar_lord, chart):
    """Generate a brief prediction for a Maha-Antar period."""
    mp = chart['planets'][maha_lord]
    ap = chart['planets'][antar_lord]

    # Houses activated
    houses_active = sorted(set([mp['house'], ap['house']]))
    house_themes = []
    for h in houses_active:
        sig = HOUSE_SIGNIFICATIONS.get(h, '')
        if sig:
            house_themes.append(f"H{h}({sig.split(',')[0].strip()})")

    # Friendship
    is_friend = antar_lord in NATURAL_FRIENDS.get(maha_lord, [])
    is_enemy = antar_lord in NATURAL_ENEMIES.get(maha_lord, [])

    quality = 'supportive period' if is_friend else 'tense period' if is_enemy else 'neutral period'

    return f"Houses {', '.join(str(h) for h in houses_active)} activated. {' + '.join(house_themes)}. Generally {quality}."
