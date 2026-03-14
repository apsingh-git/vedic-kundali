"""
Predictions Engine — Comprehensive Vedic Astrology Predictions & Remedies
Sections: Doshas, Planetary Analysis, Lal Kitab, Life Predictions,
Year-by-Year Forecast, Remedies, House Strengthening, Karmic Lessons, Daily Rituals.
"""

from datetime import datetime, timedelta
from constants import *


# ════════════════════════════════════════════════════════════════
# HELPERS
# ════════════════════════════════════════════════════════════════

def _house(chart, planet):
    return chart['planets'][planet]['house']

def _sign(chart, planet):
    return chart['planets'][planet]['sign']

def _sign_idx(chart, planet):
    return chart['planets'][planet]['sign_idx']

def _dignity(chart, planet):
    return chart['planets'][planet]['dignity']

def _house_lord(chart, h):
    return chart['houses'][h]['lord']

def _is_kendra(h):
    return h in (1, 4, 7, 10)

def _is_trikona(h):
    return h in (1, 5, 9)

def _is_dusthana(h):
    return h in (6, 8, 12)

def _conjunct(chart, p1, p2):
    return _house(chart, p1) == _house(chart, p2)

def _aspects_planet(chart, p1, p2):
    """Does p1 aspect p2 by Graha Drishti?"""
    s1 = _sign_idx(chart, p1)
    s2 = _sign_idx(chart, p2)
    aspected = [(s1 + 6) % 12]
    if p1 in SPECIAL_ASPECTS:
        for off in SPECIAL_ASPECTS[p1]:
            aspected.append((s1 + off - 1) % 12)
    return s2 in aspected


# ════════════════════════════════════════════════════════════════
# SECTION 1: DOSHAS
# ════════════════════════════════════════════════════════════════

def detect_doshas(chart):
    """Detect all major doshas with severity, impact, and remedies."""
    doshas = []
    doshas.extend(_kaal_sarp_dosha(chart))
    doshas.extend(_pitra_dosha(chart))
    doshas.extend(_manglik_dosha(chart))
    doshas.extend(_grahan_dosha(chart))
    doshas.extend(_shrapit_dosha(chart))
    doshas.extend(_guru_chandal_dosha(chart))
    return doshas


def _kaal_sarp_dosha(chart):
    """All 7 planets between Rahu-Ketu axis."""
    rahu_idx = _sign_idx(chart, 'Rahu')
    ketu_idx = _sign_idx(chart, 'Ketu')

    # Check if all 7 planets (Sun-Saturn) fall between Rahu and Ketu
    # "Between" means going from Rahu to Ketu clockwise
    check_planets = ['Sun', 'Moon', 'Mars', 'Mercury', 'Jupiter', 'Venus', 'Saturn']

    def _between_rahu_ketu(p_idx):
        """Is planet between Rahu (start) and Ketu (end) going clockwise?"""
        if rahu_idx < ketu_idx:
            return rahu_idx < p_idx < ketu_idx
        else:
            return p_idx > rahu_idx or p_idx < ketu_idx

    def _between_ketu_rahu(p_idx):
        if ketu_idx < rahu_idx:
            return ketu_idx < p_idx < rahu_idx
        else:
            return p_idx > ketu_idx or p_idx < rahu_idx

    all_rk = all(_between_rahu_ketu(_sign_idx(chart, p)) for p in check_planets)
    all_kr = all(_between_ketu_rahu(_sign_idx(chart, p)) for p in check_planets)

    if not all_rk and not all_kr:
        return []

    # Determine type based on Rahu's house
    rahu_house = _house(chart, 'Rahu')
    ksd_names = {
        1: 'Anant', 2: 'Kulik', 3: 'Vasuki', 4: 'Shankhpal',
        5: 'Padma', 6: 'Mahapadma', 7: 'Takshak', 8: 'Karkotak',
        9: 'Shankhachud', 10: 'Ghatak', 11: 'Vishdhar', 12: 'Sheshnag',
    }
    ksd_name = ksd_names.get(rahu_house, 'Kaal Sarp')
    direction = 'ascending' if all_rk else 'descending'

    # Cancellation checks
    cancellations = []
    for p in check_planets:
        if _sign_idx(chart, p) == rahu_idx or _sign_idx(chart, p) == ketu_idx:
            cancellations.append(f'{p} conjunct Rahu/Ketu breaks the axis')
    if chart['planets']['Jupiter']['dignity'] in ('Exalted', 'Own Sign') and _is_kendra(_house(chart, 'Jupiter')):
        cancellations.append('Strong Jupiter in kendra partially neutralizes')

    severity = 'Severe'
    if cancellations:
        severity = 'Partial (mitigated)'

    # Impact based on Rahu's house
    impacts = {
        1: 'Health issues, identity struggles, feeling restricted in self-expression. Life feels like swimming against the current.',
        2: 'Financial instability, family tensions, speech-related issues. Wealth comes and goes in waves.',
        3: 'Strained sibling relations, courage tested repeatedly. Communication efforts face blocks.',
        4: 'Domestic unrest, property disputes, mother\'s health concerns. Inner peace is hard to find.',
        5: 'Delays in children, education obstacles, speculation losses. Creative projects hit walls.',
        6: 'Legal troubles, health scares, hidden enemies surface. Debts accumulate despite efforts.',
        7: 'Marriage delays or turbulence, partnership betrayals. Relationships require extra patience.',
        8: 'Sudden upheavals, accidents, inheritance disputes. Transformation through crisis.',
        9: 'Father-related struggles, blocked fortune, religious disillusionment. Luck arrives late.',
        10: 'Career instability, authority clashes, reputation ups and downs. Success comes after 36.',
        11: 'Gains are unpredictable, elder sibling issues. Desires fulfilled only after sustained struggle.',
        12: 'Foreign settlement struggles, spiritual confusion, hidden expenses. Sleep disturbances.',
    }

    remedies = [
        'Perform Kaal Sarp Dosha Puja at Trimbakeshwar (Nashik) or Mahakaleshwar (Ujjain)',
        'Recite "Om Namah Shivaya" 108 times daily',
        'Keep a silver Nag (serpent) idol at home puja place',
        'Donate black sesame seeds (til) on Saturdays',
        'Feed milk to a live snake (Nag Panchami) or pour milk on a Shivling',
        'Wear a Gomed (Hessonite) or Cat\'s Eye after consulting an astrologer',
        'Visit Rahu-Ketu temple (Kalahasti in Andhra Pradesh)',
    ]

    return [{
        'name': f'Kaal Sarp Dosha ({ksd_name})',
        'type': 'Kaal Sarp',
        'severity': severity,
        'direction': direction,
        'rahu_house': rahu_house,
        'impact': impacts.get(rahu_house, 'General life obstacles and delays.'),
        'cancellations': cancellations,
        'remedies': remedies,
    }]


def _pitra_dosha(chart):
    """Sun or 9th lord afflicted by Rahu/Ketu, or Saturn in 9th."""
    results = []
    sun_house = _house(chart, 'Sun')
    rahu_house = _house(chart, 'Rahu')
    ketu_house = _house(chart, 'Ketu')
    l9 = _house_lord(chart, 9)
    saturn_house = _house(chart, 'Saturn')

    triggers = []

    # Sun conjunct Rahu/Ketu
    if sun_house == rahu_house:
        triggers.append('Sun conjunct Rahu — father\'s karma overshadowed by worldly obsessions')
    if sun_house == ketu_house:
        triggers.append('Sun conjunct Ketu — father\'s karma disconnected, ancestral debts')

    # 9th lord with Rahu/Ketu
    if l9 not in ('Rahu', 'Ketu'):
        l9_house = _house(chart, l9)
        if l9_house == rahu_house:
            triggers.append(f'9th lord {l9} conjunct Rahu — fortune blocked by past-life debts')
        if l9_house == ketu_house:
            triggers.append(f'9th lord {l9} conjunct Ketu — ancestral spiritual debts unresolved')

    # Saturn in 9th house
    if saturn_house == 9:
        triggers.append('Saturn in 9th house — heavy karmic burden from father\'s lineage')

    # Rahu in 9th house
    if rahu_house == 9:
        triggers.append('Rahu in 9th house — ancestral sins creating obstacles in fortune')

    if not triggers:
        return []

    severity = 'Severe' if len(triggers) >= 2 else 'Moderate'

    return [{
        'name': 'Pitra Dosha',
        'type': 'Pitra',
        'severity': severity,
        'triggers': triggers,
        'impact': (
            'Obstacles in career despite talent, delayed marriage, difficulty in having children, '
            'father\'s health issues, recurring financial setbacks. The native carries unresolved '
            'karma from the paternal lineage that manifests as unexplained blocks in life.'
        ),
        'remedies': [
            'Perform Pitra Tarpan on every Amavasya (new moon day)',
            'Do Pind Daan at Gaya, Varanasi, or Haridwar',
            'Feed Brahmins on father\'s death anniversary (Shraddha)',
            'Donate food to the poor on Sundays',
            'Plant a Peepal tree and water it regularly',
            'Recite Pitra Gayatri Mantra: "Om Pitrubhyah Devatabhyah Mahayogibhyash Cha, Namah Swadhayai Swahayai Nityamev Namah"',
            'Keep a portion of food aside for crows before eating (ancestors\' representatives)',
        ],
    }]


def _manglik_dosha(chart):
    """Mars in houses 1, 2, 4, 7, 8, or 12 from Lagna."""
    mars_house = _house(chart, 'Mars')
    if mars_house not in (1, 2, 4, 7, 8, 12):
        return []

    # Cancellation rules
    cancellations = []
    mars_sign = _sign(chart, 'Mars')

    # Mars in own sign or exalted
    if chart['planets']['Mars']['dignity'] in ('Exalted', 'Own Sign', 'Moolatrikona'):
        cancellations.append(f'Mars in {chart["planets"]["Mars"]["dignity"]} ({mars_sign}) — significantly reduced')

    # Mars in Aries/Scorpio in 1st, Capricorn in 8th, etc.
    if mars_house == 1 and mars_sign in ('Aries', 'Scorpio'):
        cancellations.append('Mars in own sign in 1st house — cancelled')
    if mars_house == 2 and mars_sign in ('Gemini', 'Virgo'):
        cancellations.append('Mars in Mercury\'s sign in 2nd house — cancelled')
    if mars_house == 4 and mars_sign in ('Aries', 'Scorpio'):
        cancellations.append('Mars in own sign in 4th house — cancelled')
    if mars_house == 7 and mars_sign in ('Cancer', 'Capricorn'):
        cancellations.append('Mars exalted/debilitated in 7th — reduced impact')
    if mars_house == 8 and mars_sign in ('Sagittarius', 'Pisces'):
        cancellations.append('Mars in Jupiter\'s sign in 8th — cancelled')
    if mars_house == 12 and mars_sign in ('Taurus', 'Libra'):
        cancellations.append('Mars in Venus\'s sign in 12th — cancelled')

    # Jupiter aspects Mars
    if _aspects_planet(chart, 'Jupiter', 'Mars') or _conjunct(chart, 'Jupiter', 'Mars'):
        cancellations.append('Jupiter aspects/conjuncts Mars — greatly reduced')

    # Venus conjunct Mars (in 7th)
    if mars_house == 7 and _conjunct(chart, 'Venus', 'Mars'):
        cancellations.append('Venus conjunct Mars in 7th — passion replaces aggression')

    # Spouse also Manglik — mutual cancellation (can't check here, noted in text)

    severity_map = {1: 'Mild', 2: 'Moderate', 4: 'Strong', 7: 'Strong', 8: 'Severe', 12: 'Moderate'}
    severity = severity_map.get(mars_house, 'Moderate')
    if cancellations:
        severity = 'Cancelled' if any('cancelled' in c.lower() for c in cancellations) else 'Mild (mitigated)'

    impact_map = {
        1: 'Aggressive temperament, dominating personality in marriage. Spouse may feel overpowered.',
        2: 'Harsh speech affecting family harmony. Financial disputes with in-laws possible.',
        4: 'Domestic unrest, frequent arguments at home. Property-related conflicts with spouse.',
        7: 'Most significant placement. Delays marriage, creates friction with partner. Spouse may be aggressive or face health issues.',
        8: 'Risk of accidents, surgeries. Sudden disruptions in married life. In-laws create problems.',
        12: 'Excessive expenses after marriage. Bed pleasures may cause complications. Spouse may be from distant place.',
    }

    return [{
        'name': f'Manglik Dosha (Mars in House {mars_house})',
        'type': 'Manglik',
        'severity': severity,
        'mars_house': mars_house,
        'cancellations': cancellations,
        'impact': impact_map.get(mars_house, 'Affects marriage and partnerships.'),
        'remedies': [
            'Recite Mangal Chandika Stotra or Hanuman Chalisa on Tuesdays',
            'Perform Kumbh Vivah (symbolic marriage to a pot/tree) before actual marriage',
            'Wear a Red Coral (Moonga) on the ring finger after consultation',
            'Donate red lentils (masoor dal), jaggery, or red cloth on Tuesdays',
            'Visit Mangalnath Temple in Ujjain',
            'Fast on Tuesdays and offer vermilion to Hanuman',
            'Marry after age 28 for reduced intensity',
            'Match with another Manglik — mutual cancellation',
        ],
    }]


def _grahan_dosha(chart):
    """Sun or Moon conjunct Rahu or Ketu."""
    results = []
    rahu_house = _house(chart, 'Rahu')
    ketu_house = _house(chart, 'Ketu')

    for luminary in ('Sun', 'Moon'):
        lum_house = _house(chart, luminary)
        for node in ('Rahu', 'Ketu'):
            node_house = _house(chart, node)
            if lum_house != node_house:
                continue

            if luminary == 'Sun':
                name = f'Surya Grahan Dosha (Sun-{node} in House {lum_house})'
                impact = (
                    'Father\'s health or relationship suffers. Authority figures create obstacles. '
                    'Government dealings face delays. Self-confidence fluctuates. '
                    'Career progress is interrupted by unexpected events.'
                )
                remedies = [
                    'Recite Aditya Hridayam Stotra daily at sunrise',
                    'Offer water (Arghya) to the Sun every morning',
                    'Donate wheat, jaggery, and copper on Sundays',
                    'Wear a Ruby (Manik) only if Sun is the lagna lord or yogakaraka',
                    'Perform Surya Graha Shanti Puja',
                ]
            else:
                name = f'Chandra Grahan Dosha (Moon-{node} in House {lum_house})'
                impact = (
                    'Mental restlessness, anxiety, and mood swings. Mother\'s health may suffer. '
                    'Emotional decision-making leads to problems. Sleep disturbances and overthinking. '
                    'Public image fluctuates — people misunderstand your intentions.'
                )
                remedies = [
                    'Recite Chandra Kavach or "Om Som Somaya Namah" 108 times on Mondays',
                    'Wear a Pearl (Moti) set in silver on the little finger',
                    'Donate white rice, milk, or white cloth on Mondays',
                    'Keep a silver bowl of water near your bed at night',
                    'Perform Chandra Graha Shanti Puja',
                    'Drink water from a silver glass regularly',
                ]

            severity = 'Strong'
            # Closer conjunction is worse
            lum_lon = chart['planets'][luminary]['longitude']
            node_lon = chart['planets'][node]['longitude']
            diff = abs(lum_lon - node_lon)
            if diff > 180:
                diff = 360 - diff
            if diff < 5:
                severity = 'Severe (tight conjunction)'
            elif diff > 20:
                severity = 'Mild (wide conjunction)'

            results.append({
                'name': name,
                'type': 'Grahan',
                'severity': severity,
                'luminary': luminary,
                'node': node,
                'house': lum_house,
                'impact': impact,
                'remedies': remedies,
            })

    return results


def _shrapit_dosha(chart):
    """Saturn conjunct Rahu — past-life karmic curse."""
    if not _conjunct(chart, 'Saturn', 'Rahu'):
        return []

    house = _house(chart, 'Saturn')
    sign = _sign(chart, 'Saturn')

    impact_map = {
        1: 'Chronic health issues, delayed progress. Life feels like an uphill battle from birth.',
        2: 'Family disharmony, financial losses through deceit. Speech may cause problems.',
        3: 'Sibling betrayals, communication blocks. Courage tested through unusual circumstances.',
        4: 'No peace at home, property losses. Mother\'s suffering. Vehicles cause trouble.',
        5: 'Children-related sorrows, education disrupted. Investments go wrong. Romance disappoints.',
        6: 'Legal battles, health scares, enemies disguised as friends. Debt traps.',
        7: 'Marriage severely delayed or troubled. Partner may deceive or abandon. Business partnerships fail.',
        8: 'Accidents, surgeries, sudden losses. Inheritance disputes. Occult experiences.',
        9: 'Father\'s suffering, fortune blocked, faith tested. Pilgrimages bring temporary relief.',
        10: 'Career setbacks despite hard work. Boss/authority figure creates constant problems.',
        11: 'Gains come with strings attached. Friends betray. Elder siblings face difficulties.',
        12: 'Exile/isolation, foreign land struggles. Spiritual confusion. Hidden enemies.',
    }

    return [{
        'name': f'Shrapit Dosha (Saturn-Rahu in House {house}, {sign})',
        'type': 'Shrapit',
        'severity': 'Severe',
        'house': house,
        'impact': impact_map.get(house, 'Past-life karmic debts create recurring obstacles.'),
        'remedies': [
            'Recite Maha Mrityunjaya Mantra 108 times daily for 40 days',
            'Perform Shrapit Dosha Nivaran Puja',
            'Donate black blankets, mustard oil, and iron items on Saturdays',
            'Feed crows and stray dogs regularly',
            'Visit Shani temple on Saturdays and pour mustard oil on Shani idol',
            'Recite Shani Chalisa every Saturday',
            'Do Rudrabhishek on Mondays to invoke Lord Shiva\'s protection',
            'Donate to old-age homes or orphanages',
        ],
    }]


def _guru_chandal_dosha(chart):
    """Jupiter conjunct Rahu or Ketu."""
    results = []

    for node in ('Rahu', 'Ketu'):
        if not _conjunct(chart, 'Jupiter', node):
            continue

        house = _house(chart, 'Jupiter')
        jup_dignity = _dignity(chart, 'Jupiter')

        if node == 'Rahu':
            name = f'Guru Chandal Dosha (Jupiter-Rahu in House {house})'
            impact = (
                'Wisdom gets corrupted by worldly obsession. Person may follow wrong gurus or '
                'unethical paths thinking they are righteous. Children face difficulties. '
                'Religious hypocrisy or loss of faith. Financial decisions are poor despite '
                'appearing intelligent. Teachers/mentors may mislead.'
            )
        else:
            name = f'Guru Chandal Dosha (Jupiter-Ketu in House {house})'
            impact = (
                'Spiritual extremism or complete detachment from dharma. Children may be '
                'estranged. Higher education disrupted. Can give deep mystical insight if '
                'Jupiter is strong, but otherwise creates confusion between material and '
                'spiritual goals. Person oscillates between extremes.'
            )

        severity = 'Moderate'
        if jup_dignity in ('Debilitated', 'Enemy'):
            severity = 'Severe'
        elif jup_dignity in ('Exalted', 'Own Sign'):
            severity = 'Mild (Jupiter strong enough to handle)'

        results.append({
            'name': name,
            'type': 'Guru Chandal',
            'severity': severity,
            'house': house,
            'node': node,
            'impact': impact,
            'remedies': [
                'Recite Vishnu Sahasranama or "Om Guru Devaya Namah" daily',
                'Wear a Yellow Sapphire (Pukhraj) on the index finger after consultation',
                'Donate yellow items (turmeric, yellow cloth, gold) on Thursdays',
                'Feed Brahmins or donate to educational institutions on Thursdays',
                'Worship Lord Vishnu or Brihaspati Dev',
                'Plant a banana tree and water it with turmeric water on Thursdays',
                'Recite Guru Beej Mantra: "Om Graam Greem Graum Sah Gurave Namah"',
            ],
        })

    return results


# ════════════════════════════════════════════════════════════════
# SECTION 2: DETAILED PLANETARY ANALYSIS
# ════════════════════════════════════════════════════════════════

# Planet placement meanings by house (chart-specific interpretations)
_PLANET_IN_HOUSE = {
    'Sun': {
        1: 'Strong personality with natural leadership qualities and a commanding presence that others instinctively follow. This placement creates a deep psychological need for recognition and respect, often making the person unable to function well in subordinate roles or environments where they feel unseen. In real life, this manifests as gravitating toward government jobs, politics, senior management, or any arena where personal authority is exercised; the person becomes the "face" of whatever they do. The Sun\'s influence on the 1st house intensifies after the mid-20s when career identity solidifies, and the native often hits their stride around 33-36 when the solar maturity cycle completes. Watch out for ego clashes in relationships, a tendency to dismiss others\' opinions, and health issues related to heart, bones, or eyes, especially during Sun dasha or adverse transits.',
        2: 'Wealth comes through positions of authority, government connections, or family legacy tied to status and power. Psychologically, there is an intense identification with family prestige: the person feels personally diminished when the family\'s reputation is questioned and will fight hard to uphold or restore family honor. This plays out as gravitating toward careers in administration, treasury, or family businesses where they are the decision-maker; speech tends to be authoritative and at times harsh, especially when they feel their authority is being undermined. Financial stability typically improves after 24-25, with significant gains possible during the Sun\'s mahadasha or when transiting Jupiter aspects the 2nd house. Be cautious of conflicts with father over money, a tendency toward dictatorial family dynamics, and eye or dental problems that surface periodically.',
        3: 'Courageous and bold in communication, with a voice that commands attention in meetings, negotiations, and public discourse. This placement creates a psychological drive to prove oneself through effort, initiative, and self-made accomplishments rather than inherited advantage, often leading to sibling rivalries or a competitive dynamic with peers. In practice, the person excels in media, short-distance travel for government work, writing with authority on serious subjects, or any role requiring decisive communication under pressure. The effects strengthen noticeably in the late 20s, and the native often finds their voice and true courage after overcoming an early-life communication challenge or conflict with siblings. Watch out for overbearing communication style, strained sibling relationships where the native dominates, and shoulder or right-ear problems during adverse transits.',
        4: 'A deep desire for a grand, impressive home that reflects personal status and achievement. Psychologically, this person struggles to separate personal identity from domestic environment: if home life is chaotic, their entire self-esteem crumbles, and they may overcompensate by investing heavily in property or interior displays of success. This manifests as acquiring government-linked housing, ancestral property disputes, or a career in real estate or land administration. The effects shift around age 30-35, when the tension between career ambition and domestic peace reaches a peak; the native must consciously choose balance or risk burnout. Be cautious of power struggles with the mother, suppressed emotions masquerading as authority at home, and heart or chest-related ailments exacerbated by domestic stress.',
        5: 'Brilliant intellect with a natural flair for creative authority, teaching, and mentorship. This placement generates a psychological need to leave a legacy through children, creative works, or intellectual contributions that carry the native\'s personal stamp. In practice, the person is drawn to education, politics, speculative investments with insider knowledge, or creative fields where they hold directorial control; romance tends to be with powerful or high-status individuals. The 5th house Sun gains tremendous strength after age 25, and the period between 30-40 often brings the most significant creative and intellectual achievements. Watch out for excessive pride in children\'s accomplishments (living vicariously), authoritarian parenting style, stomach or digestive issues, and a tendency toward speculative risks that are ego-driven rather than calculated.',
        6: 'Victory over enemies and competitors comes naturally, with a robust ability to recover from health setbacks and emerge stronger. Psychologically, this native thrives in conflict and competition rather than avoiding it; they feel most alive when there is a problem to solve, an enemy to defeat, or a service to render under difficult conditions. This makes them excellent in government service, military leadership, medical practice, law enforcement, or legal advocacy where authority is exercised in adversarial settings. The 6th house Sun truly comes into its own after age 22-24, with the person developing an almost immune-like resistance to professional and personal attacks by their 30s. Be cautious of developing a combative personality that alienates allies, workaholism justified as "service," and chronic issues with blood pressure, acidity, or heart strain from constant high-alert mode.',
        7: 'The spouse is likely authoritative, accomplished, or from a family of higher social standing, bringing prestige to the partnership. Psychologically, this native tends to seek validation through relationships, often marrying later after establishing their own career identity, because they cannot tolerate a partner who overshadows them. In real life, this manifests as business partnerships with government or authority figures, marriages that function like professional alliances, and public-facing roles where the partner plays a visible role. The marriage dynamic shifts significantly after age 30-35, often improving as both partners settle into defined roles; if married too young, ego battles can be destabilizing. Watch out for power struggles within marriage, a tendency to treat the spouse as subordinate, delayed marriage causing family pressure, and digestive or lower-back issues tied to partnership stress.',
        8: 'Transformation through crisis is the defining theme, with the native repeatedly experiencing breakdowns that force fundamental identity reconstruction. Psychologically, there is a deep fascination with hidden knowledge, power structures, mortality, and what lies beneath the surface; the person is rarely satisfied with superficial explanations of anything. This translates to careers in research, investigation, insurance, taxation, occult sciences, or surgery, and there is often an inheritance dispute or sudden shift in family fortune tied to the father. The 8th house Sun typically brings its most intense transformations between ages 28-42, with the period around 33 being a particularly significant turning point. Watch out for father\'s health concerns (especially heart and bones), a secretive nature that damages trust in close relationships, chronic low vitality, and the tendency to be drawn into power struggles over shared resources or inheritance.',
        9: 'Father is typically influential, principled, or connected to government and religious institutions, shaping the native\'s worldview profoundly. This placement creates a deep psychological identification with a particular philosophy, belief system, or moral code, to the point where the native may become rigid or evangelical about their convictions. In real life, the person is drawn to law, higher education, foreign diplomacy, religious leadership, or government roles with international scope; scholarships, mentorships, and recognition from authority figures come naturally. Fortune truly expands after age 24, with the most blessed period often arriving between 33-45 when the solar influence on the dharma house fully matures. Watch out for self-righteousness that alienates others, conflicts with father over life direction, a tendency to impose beliefs on family, and health concerns during long journeys or foreign stays.',
        10: 'Peak career success with a powerful drive toward public recognition, government authority, and lasting professional legacy. This is one of the strongest Sun placements: psychologically, the native\'s entire self-worth is built around professional achievement, and they experience existential crisis during career setbacks in a way others do not. They naturally gravitate to administrative leadership, politics, government service, corporate CEO roles, or any position where they sit at the top of a hierarchy. The career trajectory typically accelerates after age 24-25, with the most prominent achievements between 35-50; however, the drive for recognition may come at the cost of personal relationships and domestic peace. Watch out for defining yourself entirely by your job title, neglecting family for career, creating enemies through authoritarian management, and heart or spinal issues that worsen with the stress of leadership.',
        11: 'Gains flow through government connections, authority figures, and powerful social networks that the native cultivates deliberately. Psychologically, this person derives enormous satisfaction from influential friendships and being part of elite circles; there is a deep need to feel that one\'s social circle reflects personal status and worth. In practice, the eldest sibling is often successful and well-placed, income comes through official channels or organizations, and the native achieves long-held ambitions through strategic networking rather than solo effort. Financial gains and social influence peak after age 30, with the most rewarding period typically between 35-50 when the accumulated network begins to yield returns. Watch out for using friendships instrumentally, neglecting genuine emotional bonds in favor of "useful" connections, disappointment when powerful friends fail to deliver, and a tendency to overcommit to social obligations at the expense of health.',
        12: 'Government work abroad or expenditure through official channels defines this placement, with the father often living at a distance or having a significant foreign connection. Psychologically, the ego undergoes a gradual dissolution process: the native is repeatedly placed in situations where personal identity, status, and authority are stripped away, forcing spiritual growth through surrender rather than assertion. This manifests as foreign postings, hospital or institutional work, spiritual retreats, charitable service that goes unrecognized, or careers in isolation like research labs or ashrams. The effects intensify after age 30, with the period between 36-48 often bringing the most profound spiritual openings alongside material losses that serve as catalysts. Watch out for depression triggered by lack of recognition, strained relationship with father, excessive spending that depletes savings, sleep disturbances, and eye problems that worsen in foreign or unfamiliar environments.',
    },
    'Moon': {
        1: 'Emotional, nurturing personality that is deeply attuned to the moods of others, creating instant public appeal and a face that reflects inner feelings transparently. Psychologically, the sense of self is fluid and heavily influenced by the mother, early childhood experiences, and current emotional environment; there is a tendency to absorb others\' emotions, leading to identity confusion if boundaries are not established. In real life, this manifests as popularity with the public, careers in hospitality, nursing, counseling, or food industries, and a physical appearance that genuinely shifts with mood, weight, and emotional state. The Moon\'s influence on personality stabilizes somewhat after age 24-27 (lunar maturity), but emotional volatility may resurface during major life transitions. Watch out for excessive dependence on others\' approval, mood-driven decision-making, water retention and hormonal fluctuations, and a tendency to mother everyone at the expense of personal boundaries.',
        2: 'Family-oriented with deep emotional attachment to traditions, food culture, and inherited values. Psychologically, financial security is directly linked to emotional wellbeing: when money is tight, the person becomes anxious, irritable, and may even fall physically ill, because wealth represents emotional safety, not just material comfort. This plays out as careers in food business, dairy, textiles, hospitality, or any nurturing commerce; speech is sweet and persuasive when the mood is good but can become emotionally manipulative when insecure. Wealth fluctuates in cycles much like lunar tides, with financial stability improving after age 30 and peaking around 40-48. Watch out for emotional eating as a coping mechanism, hoarding behavior driven by scarcity fears, family enmeshment where personal identity is subsumed by family role, and throat or thyroid issues that correlate with unexpressed emotions.',
        3: 'Emotionally expressive communicator with a natural gift for writing that touches people\'s hearts rather than just their minds. The psychological pattern here is processing emotions through communication: the native needs to talk, write, or express creatively in order to understand their own feelings, and suppression of expression can lead to anxiety or physical symptoms. In practice, this creates success in creative writing, blogging, social media, emotional storytelling, journalism with a human-interest angle, or counseling work with siblings and neighbors. The communicative abilities strengthen after age 24 and become particularly powerful in the mid-30s when emotional maturity combines with developed skill. Watch out for emotional volatility in sibling relationships, restless short travels driven by emotional avoidance rather than genuine purpose, a tendency to overshare personal feelings publicly, and upper-respiratory or shoulder issues tied to emotional stress.',
        4: 'Very close to mother, with the domestic environment serving as the primary source of emotional security and psychological stability. This is one of the strongest Moon placements: the person\'s entire emotional architecture is built around home, and being uprooted or having an unstable domestic life causes deep psychological distress that affects every other area. In real life, this creates a beautiful, well-maintained home, success in real estate, interior design, agriculture, or any property-related field, and a person who is the emotional anchor for the entire family. The attachment to home and mother intensifies through the 20s and may evolve into a healthier independence after age 30-36, when the native can nurture others without losing themselves. Watch out for inability to leave the parental home even when it is necessary, making major life decisions based on mother\'s opinions, emotional manipulation through guilt within the family, and chest or breast-related health concerns.',
        5: 'Romantic, creative, and deeply intuitive mind that processes knowledge through feeling rather than pure logic. Psychologically, the native needs creative and romantic expression the way others need food and water; without an emotional outlet, whether through children, art, romance, or spiritual practice, they experience a sense of purposelessness that can become debilitating. This manifests as natural talent in music, poetry, cinema, or any art that evokes emotion, strong intuitive stock-market instincts (though volatile), and children who are deeply emotionally bonded to the parent. The creative powers peak between ages 25-40, and the relationship with children becomes the defining emotional experience after parenthood. Watch out for love affairs driven by emotional neediness rather than genuine connection, mood-dependent creative output that lacks professional consistency, over-identification with children\'s success, and stomach or digestive issues during emotional upheaval.',
        6: 'Emotional stress from enemies, competition, and daily conflicts takes a disproportionate toll on mental and physical health. The psychological pattern is one of absorbing workplace toxicity and interpersonal hostility on a visceral level: the native literally feels sick when there is conflict, which can either make them exceptional healers and caregivers or chronic worriers depending on how the energy is channeled. In real life, this creates careers in healthcare, social work, veterinary care, or any service where emotional labor is the primary offering; however, the person may attract emotionally draining situations repeatedly. Effects are most challenging in youth and typically ease after age 30-33, when the native learns to set emotional boundaries. Watch out for psychosomatic illness triggered by workplace stress, stomach and digestive disorders that directly correlate with anxiety, maternal health issues that mirror the native\'s stress, and a martyr complex that prevents asking for help.',
        7: 'Spouse is caring, nurturing, and emotionally expressive, with the marriage serving as the primary emotional anchor in life. Psychologically, there is a deep, almost primal need for partnership: the native does not feel complete alone and may rush into relationships or stay in unhealthy ones simply to avoid the void of solitude. This manifests as success in public-facing businesses, client relationships built on emotional trust, and a marriage where emotional intimacy matters far more than practical compatibility. The partnership dynamic matures significantly after age 27-30, and the best marriages for this placement are those that begin after the native has developed independent emotional stability. Watch out for codependency, choosing partners based on emotional intensity rather than long-term compatibility, mood swings that destabilize the marriage, and reproductive or hormonal health issues that are aggravated by relationship stress.',
        8: 'Deep emotional transformations occur cyclically throughout life, with each crisis stripping away a layer of psychological defense and revealing deeper intuitive capacity. The psychological pattern is one of emotional death and rebirth: the native experiences losses, betrayals, or upheavals that would permanently damage others but somehow emerge with heightened perception and wisdom. In real life, this manifests as powerful intuition about hidden motives, success in psychology, research, insurance, or occult sciences, and an uncanny ability to sense when something is wrong before evidence appears. The transformative episodes are most intense between ages 24-42, and the native often undergoes a complete psychological rebuilding around age 36. Watch out for mother\'s health deteriorating after the native\'s middle age, obsessive attachment to emotional pain as identity, depression triggered by inability to control outcomes, and reproductive or hormonal disorders that coincide with emotional crises.',
        9: 'Fortune flows through emotional intelligence, public dealings, and a deeply felt connection to spirituality and philosophical wisdom. Psychologically, the native\'s moral compass is guided by feeling rather than doctrine: they know what is right through emotional resonance, not intellectual argument, and their faith is devotional rather than theological. This creates success in religious or charitable organizations, pilgrimage tourism, teaching with emotional impact, and cross-cultural work where emotional sensitivity bridges language barriers; the mother is often religious or spiritually inclined. Fortune builds steadily after age 24 and often brings its greatest blessings between 36-48, especially through foreign connections or spiritual mentors. Watch out for religious sentimentality that substitutes emotion for genuine spiritual discipline, guru dependence, moody fluctuations in faith, and health issues during foreign travel related to water or food sensitivity.',
        10: 'Public career success driven by mass appeal, emotional intelligence, and an instinctive understanding of what people need. This is a powerful placement for careers in politics, entertainment, hospitality, food industry, healthcare, and any field where public sentiment determines success. Psychologically, professional identity and emotional state are inseparable: a bad day at work genuinely ruins the person\'s entire emotional world, and career achievements provide the deepest emotional highs. Career paths tend to change frequently before age 30 as the native searches for work that "feels right," with stability and recognition arriving between 33-45. Watch out for taking professional criticism deeply personally, mood-driven career decisions that appear erratic to others, public reputation fluctuating with emotional state, and chronic stress-related health issues in the upper body tied to professional pressure.',
        11: 'Gains flow through public-facing networks, women, nurturing industries, and emotional connections that the native cultivates naturally. Psychologically, friendships are not casual for this person: each friendship carries emotional weight, and betrayal by a friend is experienced as profoundly as romantic rejection. In practice, the social circle includes many women, emotionally open people, and those in caring professions; income comes through food, textiles, hospitality, healthcare, or public-service networks. Desires are emotionally driven and tend to be fulfilled after age 27-30, with the most abundant period arriving between 36-48 when emotional maturity and social capital converge. Watch out for emotionally draining friendships that take more than they give, fulfilling desires that provide temporary emotional relief rather than lasting satisfaction, elder sibling relationship stress, and hormonal or fluid-related health issues that intensify with social overextension.',
        12: 'Vivid dreams, psychic abilities, and a rich inner emotional life that may be completely invisible to others. Psychologically, there is a deep pull toward emotional solitude: the native needs significant alone time to process feelings, and without it, they become irritable, scattered, and eventually ill. This manifests as success in foreign lands, spiritual retreats, hospital or institutional work, behind-the-scenes roles, and creative work done in isolation; the mother may live abroad or be emotionally unavailable in some fundamental way. The spiritual and psychic dimensions of this placement deepen throughout life, with the most significant openings occurring after age 30 and peaking around 42-48. Watch out for emotional isolation that crosses into depression, sleep disturbances driven by unprocessed emotions, unconscious spending on comfort items to fill emotional voids, and a tendency to retreat from problems rather than addressing them.',
    },
    'Mars': {
        1: 'Athletic build with an aggressive, action-oriented personality that makes the native a natural pioneer and fighter in every arena of life. Psychologically, there is a primal need to assert, compete, and conquer: the person feels psychologically diminished in passive roles and may create conflict unconsciously simply to feel alive and engaged. In real life, this creates soldiers, athletes, surgeons, entrepreneurs, police officers, and anyone who leads through physical courage and decisive action; scars or marks on the face or head are common, reflecting the warrior energy of this placement. The Mars energy is most raw and uncontrolled before age 28, with the native learning to channel aggression productively between 28-35. Watch out for road rage, impulsive decisions driven by anger, chronic headaches or blood-pressure issues, starting fights that damage important relationships, and the pattern of acting first and regretting later.',
        2: 'Harsh, direct speech that cuts to the point without diplomatic cushioning, combined with earning power through courage-driven fields. Psychologically, financial matters are a battleground: the native fights for every rupee, argues about money within the family, and experiences a deep link between self-worth and financial independence. This manifests as careers in engineering, surgery, defense, real estate, or any field requiring technical courage; family dynamics involve heated arguments, and the dinner table can be a war zone. Financial stability improves significantly after age 28 and peaks between 35-45, though impulsive spending may undermine savings. Watch out for damaging family relationships through harsh words spoken in anger, dental or facial injuries, arguments about inheritance that fracture family bonds permanently, and a diet heavy in spicy or heat-producing foods that aggravates pitta-related health issues.',
        3: 'Exceptional courage, quick decision-making ability, and a competitive dominance over siblings and peers. Psychologically, the native processes the world through action: they understand situations by doing, not by thinking, and they grow restless and irritable when forced into prolonged analysis without action. In real life, this creates excellence in sports, military service, police work, journalism in conflict zones, and any field requiring split-second physical decisions; siblings are often dominated by or in competition with the native. The competitive drive sharpens in the late 20s and produces its greatest victories between 30-42. Watch out for bullying siblings or peers, road accidents during short travels due to aggressive driving, shoulder or arm injuries from sports or physical overexertion, and a communication style so blunt that it damages professional networks.',
        4: 'Property acquisition through persistent effort and conflict, with a restless domestic life that rarely achieves the calm the native secretly desires. Psychologically, there is a deep internal contradiction: the person craves the security of home while simultaneously feeling trapped by domestic routine, leading to cycles of building and disrupting their own peace. This manifests as property disputes, renovation projects driven by restlessness, vehicles acquired through hard-won effort, and tensions with the mother who may be strong-willed herself. The domestic situation typically stabilizes after age 30-35, once the native channels Martian energy into property investment rather than domestic conflict. Watch out for fire hazards in the home, arguments with mother that leave lasting emotional scars, impulsive property decisions driven by competitive urgency, and blood-pressure or chest issues aggravated by domestic stress.',
        5: 'Sharp, technical intellect combined with impulsive decision-making that makes speculation a high-risk, high-reward game. Psychologically, the native approaches romance, creativity, and children with competitive intensity: love is pursued like a conquest, creative work is produced in passionate bursts rather than steady discipline, and children are pushed toward achievement from an early age. In practice, this creates success in technical education, competitive sports coaching, speculative trading with high volatility, and creative fields requiring physical energy like dance, action cinema, or sculpture. The intellectual sharpness peaks between 25-40, and the relationship with children evolves significantly once the native tempers competitiveness with patience. Watch out for impulsive love affairs that burn fast and end in conflict, speculation losses driven by overconfidence, pushing children too hard academically or athletically, and stomach issues linked to anger and stress.',
        6: 'One of the best Mars placements: the native destroys enemies, wins competitions, and thrives in adversarial environments where others crumble. Psychologically, conflict is not just tolerated but genuinely energizing; the person performs at their best under threat, deadline, or direct challenge, and may unconsciously seek out competitive situations to feel fully engaged. In real life, this produces outstanding military officers, surgeons, trial lawyers, competitive athletes, police investigators, and anyone who fights for a living. The 6th house Mars becomes increasingly powerful after age 24, with peak effectiveness between 28-45 when physical stamina and strategic experience converge. Watch out for defining yourself entirely through opposition, becoming addicted to conflict even in personal relationships, chronic inflammatory conditions driven by perpetual fight-or-flight mode, and workplace rivalries that consume energy better spent on growth.',
        7: 'Passionate, physically intense marriage with a spouse who is energetic, assertive, and potentially argumentative or dominant. Psychologically, partnerships are experienced as arenas of power: the native must constantly negotiate between desire for an equal partner and an instinct to dominate, creating a push-pull dynamic that keeps relationships exciting but unstable. In practice, business partnerships require strong legal frameworks because disputes are likely, the spouse may be in engineering, military, medicine, or sports, and physical attraction is the primary initial bond. Marriage dynamics improve significantly after age 30-33, once both partners learn to channel competitive energy outward rather than at each other. Watch out for Manglik dosha effects on marital harmony, physical altercations or verbal aggression during arguments, multiple relationships before settling down, and reproductive or lower-abdominal health issues tied to partnership stress.',
        8: 'Accident-prone with a life punctuated by sudden physical challenges, surgeries, and inheritance conflicts that force deep transformation. Psychologically, the native has an intimate relationship with danger, crisis, and mortality: they are drawn to extreme situations and may even feel most alive in the presence of risk, which can become a self-destructive pattern if unmanaged. In real life, this creates surgeons, emergency responders, forensic investigators, insurance professionals, and deep researchers who are unafraid of taboo subjects. The most critical periods for accidents and health crises are between ages 18-28 and during Mars dasha/antardasha; the transformative wisdom of this placement typically consolidates after age 35. Watch out for surgical scars, accidents involving fire or sharp objects, inheritance disputes that turn bitter, chronic inflammatory conditions in the reproductive or eliminative systems, and a tendency to engage in high-risk behavior as emotional self-medication.',
        9: 'A fighter for beliefs, principles, and justice, with a father who may be in military, police, engineering, or any action-oriented field. Psychologically, the native\'s moral code is absolute and physically defended: they do not merely believe in right and wrong, they are willing to fight for it, which makes them crusaders, social activists, or, if channeled negatively, fanatics. This manifests as adventurous pilgrimages, learning through physical travel rather than classroom study, involvement in dharmic or legal battles, and a philosophy forged through lived experience rather than theory. The 9th house Mars produces its most meaningful results between ages 27-42, when the native has enough life experience to channel warrior energy toward wisdom. Watch out for religious extremism, physical conflicts during travel, strained father-son/daughter dynamics rooted in ideological differences, and hip or thigh injuries during sports or adventure activities.',
        10: 'Commanding career authority built through action, courage, and technical expertise rather than political maneuvering or charm. Psychologically, professional identity is inseparable from physical action: the native needs to do, build, and execute to feel professionally fulfilled, and managerial roles that are purely strategic without hands-on involvement feel hollow. In real life, this creates engineers, surgeons, military commanders, construction leaders, professional athletes, and entrepreneurs in technical fields; authority is earned through demonstrated competence under fire. Career power builds steadily from age 24 and reaches its peak between 32-48, with the native often being known as the toughest but most effective person in their organization. Watch out for workplace enemies created by an overly direct management style, career setbacks from impulsive professional decisions, chronic stress-related health issues in the back and joints, and the tendency to define self-worth entirely through professional achievement.',
        11: 'Gains through courage, competitive victory, and friendships with warriors, athletes, engineers, and military personnel. Psychologically, the social circle is a brotherhood forged through shared challenges: the native values friends who have proven themselves under fire and has little patience for superficial socializing. In practice, income comes through engineering, sports, defense contracts, property, or competitive fields; elder siblings tend to be strong-willed and possibly combative. The gains accelerate significantly after age 28 and peak between 35-50, especially through joint ventures with trusted, battle-tested allies. Watch out for aggressive pursuit of goals that alienates supporters, rivalries within friend groups, elder sibling conflicts over money or territory, and a tendency to push physical limits in sports or exercise that leads to injuries.',
        12: 'Hidden anger that simmers beneath a calm exterior, with expenses on foreign property, hospitalization due to surgery, or losses through impulsive action taken without full information. Psychologically, the native struggles with suppressed aggression: unable to express Mars energy openly, they may internalize rage, leading to passive-aggressive behavior, insomnia, or sudden explosive outbursts that seem disproportionate to the trigger. In real life, this manifests as foreign military service, hospitalization for surgical procedures, working in prisons or institutions, expenses on vehicles or property abroad, and a sexual life conducted with significant secrecy. The suppressed energy pattern intensifies between ages 24-36 and often resolves after age 40 when the native finds healthy outlets. Watch out for chronic insomnia driven by unexpressed anger, hospitalization for accidents that could have been avoided with patience, legal troubles abroad, and feet or left-eye issues that correlate with periods of intense suppressed frustration.',
    },
    'Mercury': {
        1: 'Intelligent, quick-witted personality with a youthful appearance that persists well into middle age, creating an impression of perpetual curiosity and adaptability. Psychologically, the mind is always active, always processing, always seeking new information, which can be a tremendous asset for learning but also creates anxiety when there is nothing to analyze. In real life, this produces businesspeople, writers, speakers, traders, IT professionals, and anyone whose livelihood depends on mental agility and communication skill; the person appears younger than their actual age and maintains a boyish/girlish energy throughout life. Mercury\'s influence on personality strengthens after age 22 and peaks between 30-42, when the native develops the depth to complement their natural breadth. Watch out for superficiality driven by an interest in everything but mastery of nothing, nervous disorders stemming from mental overactivity, skin conditions that correlate with stress, and a tendency to be perceived as untrustworthy due to excessive cleverness.',
        2: 'Excellent speech and earning capacity through intellectual work, with a natural talent for calculations, languages, and commercial transactions. Psychologically, wealth is conceptualized as a score in an ongoing mental game: the native derives as much pleasure from the cleverness of a deal as from the money itself, and they may undervalue opportunities that are lucrative but intellectually boring. This manifests as careers in banking, accounting, trading, bookkeeping, financial analysis, or any commerce requiring numerical precision and verbal skill. Financial acumen sharpens significantly after age 24 and produces the most consistent wealth between 30-45. Watch out for overthinking financial decisions until opportunities pass, using clever speech to manipulate family members, nervousness about money that manifests as obsessive tracking, and throat or dental issues that correlate with communication stress.',
        3: 'Outstanding communicator with natural talent in writing, media, journalism, technology, and any field requiring the rapid processing and transmission of information. Psychologically, the sibling bond and peer network serve as the primary intellectual proving ground: the native hones their mental skills through constant interaction with siblings, neighbors, and age-mates, and isolation stunts their intellectual development significantly. In real life, this creates journalists, bloggers, social media strategists, salespeople, translators, and tech entrepreneurs; the native typically has a strong bond with at least one sibling and maintains an extensive network of contacts. Communication skills reach professional maturity between ages 25-35, with the period from 30-45 often being the most productive for writing and media work. Watch out for information overload leading to shallow knowledge, gossiping that damages reputations, nervous system strain from constant digital connectivity, and shoulder or hand problems from excessive typing or writing.',
        4: 'An educated, intellectually stimulating home environment with a strong emphasis on academic achievement and mental development. Psychologically, the home is experienced as a library or classroom: the native needs intellectual stimulation in their domestic space and feels suffocated in a home environment that is emotionally warm but mentally stagnant. This manifests as advanced degrees, careers in education or academic administration, property acquired through smart analytical dealings, and a home filled with books, technology, and learning materials. Academic achievements peak between ages 22-32, while property dealings become most successful between 30-45. Watch out for intellectualizing emotions instead of feeling them, creating a home atmosphere that is cerebral but emotionally cold, excessive academic pressure on children, and chest or lung issues aggravated by indoor air quality in study-heavy environments.',
        5: 'Brilliant student with sharp analytical intellect, natural aptitude for mathematics, and children who are notably intelligent and academically inclined. Psychologically, the native approaches romance, creativity, and even spirituality through the lens of intellect: they fall in love with minds rather than bodies, create art that is clever rather than emotionally raw, and analyze spiritual concepts rather than experiencing them directly. In practice, this creates success in competitive exams, stock market analysis through data-driven methods, technical creativity in software or engineering, and mentoring roles where intellectual transmission is the core activity. Intellectual powers peak between ages 22-40, with the most significant speculative and creative successes concentrated between 28-38. Watch out for analysis paralysis in romantic decisions, children who are intellectually brilliant but emotionally underdeveloped, speculative losses from overthinking market timing, and digestive issues driven by mental stress.',
        6: 'Analytical problem-solver who defeats enemies, competitors, and illnesses through superior intelligence, strategic planning, and attention to detail. Psychologically, the native converts anxiety into analytical power: while others are paralyzed by problems, this person dissects them, finds patterns, and implements solutions with surgical precision. In real life, this creates excellent lawyers, physicians, data analysts, auditors, quality-control specialists, and anyone whose job is to find and fix what is wrong. The analytical abilities sharpen significantly after age 24 and reach peak effectiveness between 30-45, when the native has accumulated enough real-world data to complement their theoretical framework. Watch out for becoming so focused on problems that you lose sight of what is working, nervous stomach and intestinal issues driven by chronic worry, developing a reputation as a critic rather than a builder, and skin conditions that flare up during periods of intense analytical work.',
        7: 'Business partnerships succeed through intellectual compatibility, with a spouse who is articulate, educated, and often met through professional or educational networks. Psychologically, the native needs a partner they can talk to more than one they can touch: the relationship thrives on shared ideas, business collaboration, and intellectual respect, and it dies when conversation becomes routine. In practice, this creates successful business partnerships, marriages rooted in friendship and shared intellectual interests, and a social presence as a couple known for their intelligent discourse. The marriage or primary partnership benefits most from Mercury\'s influence between ages 27-40, when the native has developed enough emotional depth to complement their intellectual approach. Watch out for choosing partners based on wit rather than emotional depth, analyzing the relationship instead of feeling it, business disagreements that spill into personal life, and nervous system disorders aggravated by partnership stress.',
        8: 'Powerful research ability, investigative mind, and a fascination with hidden knowledge, occult mechanics, and the underlying systems that others overlook. Psychologically, the native is drawn to mysteries, secrets, and forbidden knowledge with an intensity that can become obsessive: the 8th house Mercury must understand how things work beneath the surface, whether that is forensic accounting, psychological profiling, or esoteric scripture. In real life, this creates insurance analysts, tax consultants, forensic investigators, psychologists, occult researchers, and anyone who makes a living by uncovering hidden information. The investigative powers deepen after age 25 and reach their sharpest between 30-45. Watch out for paranoid thinking patterns where the native sees hidden meanings everywhere, mental health strain from prolonged engagement with dark subject matter, respiratory or skin issues tied to nervous tension, and a tendency to withhold information from loved ones as a form of control.',
        9: 'Higher education, teaching, publishing, and multilingual abilities define this placement, with the father often being an intellectual, teacher, or writer. Psychologically, the native experiences knowledge as a spiritual practice: learning is not just a means to an end but a form of worship, and they feel closest to the divine through understanding rather than devotion. In practice, this creates university professors, publishers, translators, legal scholars, foreign correspondents, and anyone who bridges knowledge between cultures or languages. The intellectual journey accelerates after age 22-24, with the most significant academic or publishing achievements arriving between 30-42. Watch out for intellectual arrogance that substitutes knowledge for wisdom, collecting degrees without applying knowledge practically, a critical attitude toward traditional spiritual practices, and hip or thigh issues during prolonged periods of sedentary study.',
        10: 'Career in communication, media, information technology, trading, writing, or any field requiring versatile intellectual skills and rapid adaptation to change. Psychologically, the native\'s professional identity is tied to being the smartest person in the room: they derive enormous satisfaction from solving problems others cannot, and they feel professionally threatened by colleagues who are equally or more intelligent. In real life, this creates media professionals, IT specialists, management consultants, traders, writers, accountants, and versatile entrepreneurs who may change careers multiple times while maintaining a common thread of intellectual work. Career growth is steady from age 22, with the most significant professional breakthroughs between 28-42. Watch out for job-hopping driven by intellectual boredom rather than genuine growth, being perceived as unreliable due to too many career changes, stress-related skin or nervous disorders, and the pattern of starting many projects brilliantly but finishing few.',
        11: 'Gains through intellectual networks, multiple income sources, and friendships with media professionals, businesspeople, and IT specialists. Psychologically, the social network functions as an extended brain: the native processes ideas, validates business concepts, and stays informed through constant communication with a wide circle of intellectually stimulating contacts. In practice, income flows from consulting, media, trading, writing, technology, or any knowledge-based enterprise; the native often has multiple simultaneous income streams. The network and income both expand significantly after age 27, with the most abundant period between 32-48. Watch out for spreading yourself too thin across too many income streams, friendships that are transactional rather than emotionally fulfilling, elder sibling tensions around intellectual competition, and nervous exhaustion from maintaining too many social and professional connections simultaneously.',
        12: 'Rich imagination, writing in isolation, and an inner mental world that is far more active and creative than what is visible to others. Psychologically, the native needs solitude for intellectual processing: their best ideas come in isolation, during meditation, in foreign lands, or in institutional settings removed from daily stimulation, and they may appear mentally slower in public than they actually are. In real life, this creates researchers, writers who work in seclusion, foreign educators, data analysts in institutional settings, and professionals whose intellectual work happens behind the scenes. The creative and analytical powers in isolation deepen throughout life, with the most significant written or research contributions often emerging after age 30-35. Watch out for expenses on education or technology that exceed practical returns, mental health issues driven by prolonged isolation, overthinking that prevents sleep, and foot problems or left-eye issues that correlate with periods of intense mental labor.',
    },
    'Jupiter': {
        1: 'Wise, optimistic, and generous personality that commands natural respect and positions the native as a teacher, advisor, or moral authority in any group. Psychologically, the sense of self is built around wisdom, righteousness, and the desire to uplift others: the native genuinely believes they have something valuable to teach the world, which can be profoundly inspiring or insufferably preachy depending on self-awareness. In real life, this produces educators, counselors, religious leaders, judges, financial advisors, and anyone whose authority rests on knowledge and ethical character; physical build tends toward heaviness, with weight gain being a lifelong theme. Jupiter\'s influence on personality matures powerfully around age 16 and then again at 32 (double Jupiter cycle), with the most respected period arriving between 40-55. Watch out for weight gain that undermines health, moral self-righteousness that alienates peers, giving unsolicited advice that strains relationships, and a tendency to overcommit to others\' problems at the expense of personal well-being.',
        2: 'Wealthy family with strong cultural and religious values, excellent speech rooted in knowledge rather than mere eloquence, and a natural affinity for finance and banking. Psychologically, wealth is not just financial but dharmic: the native measures family prosperity by adherence to values and scriptural knowledge as much as by bank balance, and a rich family that has lost its ethical compass disturbs them deeply. In real life, this creates bankers, financial advisors, family business leaders, religious scholars, and food industry professionals who value quality over quantity. Family wealth grows steadily after age 24, with the most abundant period typically between 32-50. Watch out for over-indulgence in rich food leading to diabetes or cholesterol issues, using religious or moral authority to control family members, complacency about financial growth because "enough" feels like the spiritual answer, and throat or thyroid issues that manifest in the 40s.',
        3: 'Wisdom expressed through communication, with siblings who are well-educated and generally successful, and a talent for philosophical or educational writing. Psychologically, the native approaches every conversation as a teaching opportunity, which elevates ordinary interactions but can also make casual socializing feel like a lecture. In practice, this creates writers of philosophical, educational, or religious content, advisors to siblings and peers, wise mediators in family disputes, and professionals in publishing or educational media. Communication skills reach their fullest expression between ages 28-42, and the relationship with siblings improves with age as mutual respect deepens. Watch out for being preachy in casual conversations, siblings feeling patronized by the native\'s "wisdom," shoulder or respiratory issues in later years, and a tendency to give courage through advice rather than through personal example.',
        4: 'Beautiful, spacious home with a learned, religious mother, and a deep sense of inner peace that anchors the native through external turbulence. This is one of Jupiter\'s strongest placements: psychologically, the home is a temple, and domestic peace is not just desirable but spiritually necessary for the native to function in the world. In real life, this creates large, well-furnished homes, success in real estate and education, properties near temples or educational institutions, and a domestic atmosphere that neighbors and friends seek out for comfort. Property and domestic happiness build steadily through life, with the most expansive period between 30-50, often coinciding with the purchase of the most significant family home. Watch out for over-investing in property at the expense of liquidity, using spiritual platitudes to avoid addressing genuine domestic problems, weight gain from comfortable sedentary home life, and chest or liver issues that develop in the 40s from indulgent domestic habits.',
        5: 'One of Jupiter\'s best placements: brilliant children, exceptional intellect, strong past-life merit manifesting as ease in education, and natural success in speculative and academic endeavors. Psychologically, the native experiences creativity and intellectual achievement as sacred acts: teaching a student, publishing an insight, or guiding a child feels like fulfilling a divine mandate, not just a professional duty. In real life, this creates university professors, spiritual teachers, successful investors with ethical approach, creators of educational content, and parents whose children achieve remarkable things. Intellectual and creative powers are strong from youth but reach their most impactful expression between 30-48, especially during Jupiter\'s own dasha. Watch out for over-confidence in speculative decisions because "Jupiter protects," living vicariously through children\'s intellectual achievements, complacency that prevents pushing beyond natural talent, and liver or weight issues from a sedentary intellectual lifestyle.',
        6: 'Victory over enemies through wisdom, diplomacy, and moral authority, with strong health recovery and a natural capacity for charitable service. Psychologically, the native approaches conflict not as a battle but as a problem to be solved through understanding, which disarms opponents who expect aggression; however, this can also lead to under-reacting to genuine threats. In practice, this creates successful lawyers, physicians, charitable workers, judges in labor disputes, and professionals in health or conflict resolution; the native often attracts enemies who are ultimately weaker than they appear. The protective quality of this placement strengthens after age 24 and is most reliable between 30-50. Watch out for being so optimistic about enemies that you fail to take defensive measures, weight gain from stress eating during conflicts, liver and digestive issues from worry that is intellectualized rather than felt, and enabling others\' bad behavior through excessive forgiveness.',
        7: 'Wise, educated, and morally upright spouse, with marriage serving as a vehicle for spiritual and intellectual growth. In a woman\'s chart, this is the primary significator for husband, making it one of the strongest indicators of a good marriage. Psychologically, the native needs a partner who is a guru-figure or at least an intellectual and moral equal; a marriage without mutual respect and shared values feels hollow regardless of physical attraction or material comfort. In real life, this creates successful business expansions through partnerships, marriages with teachers, lawyers, bankers, or religious professionals, and a couple known for their ethical standing in the community. Marriage brings its greatest blessings between ages 28-45. Watch out for expecting the spouse to be perfect and feeling disappointed by normal human flaws, the partner gaining significant weight, preachiness within the marriage, and liver or hip issues that develop in the late 30s and require lifestyle modification.',
        8: 'Strong longevity with protection from sudden catastrophe, deep philosophical transformation through crisis, and significant inheritance or insurance benefits. Psychologically, the native approaches death, transformation, and occult knowledge with the curiosity of a scholar rather than the fear of a victim, which allows them to navigate crises that devastate others with remarkable equanimity. In practice, this creates occult researchers, insurance executives, inheritance lawyers, psychologists dealing with trauma, and spiritual teachers who have emerged from their own dark nights of the soul. The protective influence is consistent throughout life, but the deepest transformations occur between ages 28-42, often coinciding with Jupiter\'s transits over key natal points. Watch out for complacency about health because "Jupiter protects" (it does, but lifestyle still matters), using philosophical detachment to avoid processing trauma, liver or reproductive issues that develop slowly, and underestimating financial risks because past crises resolved favorably.',
        9: 'The single best placement for Jupiter in the entire chart: supreme dharma, profound fortune, guru-like wisdom, and a father who is wise, ethical, and supportive. Psychologically, the native carries a sense of cosmic purpose that is not arrogance but genuine alignment with dharma; they instinctively know their path, trust the universe, and attract opportunities that others would call luck but are actually karmic merit. In real life, this creates university deans, supreme court judges, religious heads, international diplomats, successful publishers, and spiritual leaders whose guidance transforms lives; foreign connections bring both wealth and wisdom. Fortune builds from youth but peaks between 33-52, with Jupiter dasha being a golden period. Watch out for spiritual complacency (the danger of having too much grace is taking it for granted), father\'s health in later years, weight gain and liver issues from abundant living, and the rare but real possibility of being so blessed that personal growth stagnates.',
        10: 'High career success achieved through ethical conduct, wisdom, and genuine competence rather than politics or manipulation. Psychologically, the native cannot separate professional ambition from moral purpose: they need to believe their work makes the world better, and a lucrative but unethical career path feels like a spiritual violation. In practice, this creates teachers who become administrators, lawyers who become judges, bankers who become regulators, and professionals who rise to advisory or leadership positions through demonstrated integrity. Career growth is steady from age 24, with the most prestigious appointments arriving between 33-50. Watch out for being too idealistic about workplace politics and getting outmaneuvered by less scrupulous competitors, weight gain from sedentary desk leadership, liver and back issues in the 40s, and the tendency to preach workplace ethics rather than model them silently.',
        11: 'Abundant financial gains, fulfilled long-term desires, wealthy and influential friends, and elder siblings who prosper and provide support. Psychologically, the native experiences wealth not as an end but as evidence of cosmic favor: each gain confirms that they are on the right path, and financial setbacks trigger not just practical concern but existential doubt. In practice, income flows from multiple streams including teaching, advisory work, finance, religious or charitable organizations, and investments guided by optimistic but generally sound instincts. The most abundant financial period typically falls between 33-52, with Jupiter dasha and bhukti being especially prosperous. Watch out for overextending financially because past gains created false confidence, weight gain correlated with increasing prosperity, friends who take advantage of your generosity, and liver or cholesterol issues that develop from the abundant lifestyle this placement tends to create.',
        12: 'Spiritual liberation, meaningful foreign residence, deep devotion through temple visits and charity, and the moksha-karaka (liberation significator) in the moksha house creating one of the most spiritually powerful placements possible. Psychologically, the material world holds diminishing interest as life progresses: the native experiences a gravitational pull toward renunciation, whether literal (ashram life) or figurative (detaching from social status while remaining in the world). In practice, this creates spiritual teachers in foreign lands, charitable workers in hospitals or ashrams, professionals who relocate abroad for meaningful work, and individuals whose greatest wisdom comes through solitude and contemplation. The spiritual dimension deepens throughout life, with the most transformative period occurring between 40-55. Watch out for using spiritual philosophy to justify financial irresponsibility, isolating from family under the guise of spiritual growth, liver issues that develop in foreign lands due to dietary changes, and spending on religious or charitable causes that exceeds actual capacity.',
    },
    'Venus': {
        1: 'Attractive, charming personality with refined aesthetic taste, a magnetic physical presence, and a natural capacity to make others feel comfortable and appreciated. Psychologically, the native\'s sense of self is built around beauty, grace, and the ability to create harmony: they feel personally diminished in ugly, chaotic, or confrontational environments and will invest enormous energy in maintaining pleasant surroundings and relationships. In real life, this creates models, artists, designers, diplomats, hospitality professionals, and anyone whose presence enhances the atmosphere; physical attractiveness is typically above average, and the person ages gracefully. Venus\'s influence on personality is present from childhood but reaches full expression between 25-40, when charm combines with substance. Watch out for vanity and excessive self-focus on appearance, using charm to avoid dealing with difficult truths, relationship dependency where self-worth requires constant romantic validation, and kidney or hormonal issues that manifest in the 30s.',
        2: 'Wealth through beauty, arts, luxury goods, and culturally refined commerce, with sweet, melodious speech and a family background that values aesthetics and social grace. Psychologically, financial security is experienced through sensory pleasure: the native does not just want money but wants money that comes from and is spent on beautiful things, and they feel spiritually depleted in work that is lucrative but aesthetically offensive. In real life, this creates careers in fashion, jewelry, cosmetics, fine dining, art dealing, vocal music, and luxury retail; the family typically has artistic or culturally refined leanings, and the native\'s face is notably attractive. Wealth builds steadily from age 22, with the most prosperous period between 28-45. Watch out for overspending on luxury that outpaces income, using sweet speech to manipulate rather than communicate honestly, diabetes or sugar-related conditions from indulgent eating habits, and a family atmosphere that prioritizes appearance over genuine emotional connection.',
        3: 'Creative, artistic communication with a talent for performing arts, persuasive media work, and graceful interpersonal skills that make the native a natural networker. Psychologically, the native processes and expresses themselves through beauty: they cannot communicate effectively in harsh or ugly environments, and their creative output is directly proportional to the aesthetic quality of their surroundings and relationships. In practice, this creates singers, actors, media personalities, artistic content creators, graphic designers, and professionals in beauty or fashion media; siblings are often artistically inclined or physically attractive. Creative communication skills bloom in the mid-20s and peak between 28-40. Watch out for prioritizing style over substance in communication, siblings who are envious of the native\'s charm, short-distance travel for pleasure that cuts into productive work time, and upper-respiratory issues exacerbated by performance or vocal strain.',
        4: 'Beautiful, luxuriously furnished home with aesthetic vehicles, a mother who is attractive or artistically inclined, and a domestic life centered on comfort and sensory pleasure. Psychologically, home is a sanctuary of beauty: the native cannot relax in a messy, ugly, or poorly designed space, and they may spend disproportionate income on home aesthetics, viewing it as a necessity rather than indulgence. In real life, this creates interior designers, luxury real estate professionals, automotive enthusiasts, and anyone whose career connects beauty with domestic space; the mother-child bond is warm, and the mother may be the native\'s first aesthetic influence. Domestic happiness peaks between 25-45, with the most beautiful home typically acquired between 30-42. Watch out for spending beyond means on home decoration, a domestic life so comfortable that it undermines ambition, using home beauty as a substitute for genuine family harmony, and kidney or reproductive issues that develop in the late 30s from sedentary comfort.',
        5: 'Romantic, deeply creative, and artistically gifted, with beautiful children, passionate love affairs, and a life enriched by aesthetic pleasure and entertainment. Psychologically, the native needs romance and creative expression as fundamental survival requirements: without love, art, or beauty to pursue, they experience a flat, gray existence that can slide into genuine depression. In practice, this creates actors, musicians, painters, cinema professionals, fashion designers, creative directors, and anyone in the entertainment industry; children are typically attractive and artistically inclined, and the love life is rich with intense, often dramatic experiences. Creative and romantic powers peak between 22-38, with the most acclaimed artistic work often produced during Venus dasha. Watch out for serial romantic attachments driven by the need for novelty rather than depth, creative prima donna behavior that alienates collaborators, over-identification with children\'s beauty or talent, and sugar-related or reproductive health issues from an indulgent lifestyle.',
        6: 'Challenging placement for Venus: enemies arise through love matters, romantic complications create health and professional stress, and the native must learn to serve before they can be served. Psychologically, there is a painful contradiction between the desire for beauty and harmony and the reality of conflict, illness, and service that the 6th house demands; the native may feel that life forces them into unpleasant situations that contradict their nature. In real life, this manifests as relationship enemies, workplace romantic complications, health issues related to kidneys, diabetes, or reproductive organs, and eventually, a capacity for compassionate service that transforms suffering into wisdom. The difficult period is typically most intense between ages 20-32, with conditions improving after 33-35 when the native accepts the service orientation. Watch out for workplace affairs that damage careers, health neglect because illness feels aesthetically unacceptable, using romantic charm to avoid genuine conflict resolution, and chronic kidney or sugar conditions that require consistent management.',
        7: 'One of the best marriage placements in the entire chart: a beautiful, loving, culturally refined spouse, harmonious partnerships, and a married life that deepens rather than diminishes over time. Psychologically, the native is genuinely completed by partnership: unlike codependency, this is a natural flourishing where both individuals become more fully themselves through the relationship, creating a whole greater than the sum of its parts. In real life, this creates successful marriages, flourishing business partnerships, careers in wedding planning or couples\' counseling, and a couple that others admire and aspire to emulate. The partnership dimension of life begins to bless the native from the mid-20s, with the most fulfilling period between 28-50. Watch out for the rare possibility of taking a good marriage for granted, avoiding necessary confrontation to maintain surface harmony, the partner gaining weight from comfortable living, and kidney or reproductive health issues in the late 30s that require attention.',
        8: 'Secretive, intensely passionate love life with sudden wealth through spouse, inheritance, or insurance, and a fascination with tantric or esoteric knowledge related to beauty and pleasure. Psychologically, the native is drawn to the hidden, forbidden, or taboo dimensions of love and beauty: they find conventional romance boring and seek transformative intimacy that burns away pretense and leaves something raw and real. In real life, this creates success in insurance, inheritance management, cosmetic surgery, mortuary beautification, tantric practice, and any field combining beauty with transformation or death. Financial windfalls through the spouse or joint resources are likely between ages 25-40. Watch out for secret affairs that create enormous personal and professional damage, obsessive attachment to intense relationships that are actually toxic, reproductive health issues exacerbated by emotional intensity, and a tendency to use sexual or romantic power as a control mechanism.',
        9: 'Fortune through arts, beauty industry, women, and cross-cultural aesthetics, with foreign travel for pleasure and a spiritual life centered on devotion (bhakti) rather than austerity. Psychologically, the native\'s philosophy of life is rooted in beauty, love, and divine feminine energy: they experience the sacred through art, music, nature, and human connection rather than through scripture or renunciation. In practice, this creates international fashion professionals, luxury travel consultants, devotional artists, cross-cultural marriage, and professionals who bring beauty to philosophical or religious expression. Fortune through beauty and art expands significantly after age 24, with the most blessed period between 28-45. Watch out for confusing pleasure-seeking with spiritual growth, guru figures who exploit the native\'s devotion, excessive spending on foreign luxury travel, and hip or thigh issues during the late 30s from a lifestyle heavy on comfort and light on physical discipline.',
        10: 'Career in arts, fashion, beauty, hospitality, entertainment, luxury goods, or diplomacy, with fame and recognition coming through creative work and aesthetic contribution. Psychologically, the native needs to be proud of what they do in an aesthetic sense: they cannot tolerate work that is effective but ugly, and they will choose a lower-paying beautiful career over a higher-paying inelegant one without hesitation. In real life, this creates fashion designers, film directors, luxury brand managers, hotel executives, makeup artists who become celebrities, and diplomats whose charm is a professional asset. Career recognition builds from the mid-20s and peaks between 30-48, with the most acclaimed work often produced during Venus dasha periods. Watch out for prioritizing appearance over substance in professional output, jealousy from less attractive or charming colleagues, career stagnation from comfort with current success, and reproductive or kidney issues that flare during periods of professional overextension.',
        11: 'Gains through women, arts, luxury goods, beauty industry, and aesthetically oriented networks, with wealthy female friends and long-held desires for beauty and comfort being fulfilled. Psychologically, the social circle is a gallery of beauty: the native surrounds themselves with attractive, cultured, aesthetically sensitive people, and they feel out of place in groups that are intellectually stimulating but aesthetically dull. In practice, income flows from fashion, cosmetics, art, entertainment, luxury retail, wedding industry, and any commerce serving refined taste. Financial gains accelerate after age 25, with the most abundant period between 30-48. Watch out for superficial friendships based on appearance rather than substance, spending gains on luxury faster than they accumulate, elder sibling tensions around lifestyle differences, and metabolic or hormonal issues that develop from the rich lifestyle this placement enables.',
        12: 'Bed pleasures, foreign luxury, expenses on comfort and beauty, secret romantic relationships, and a spiritual life rooted in devotion, surrender, and aesthetic contemplation. Psychologically, the native experiences the deepest pleasure in private: public life is performed, but true sensual and aesthetic satisfaction comes in solitude, in foreign lands, or in secret, creating a rich private world that few ever witness. In real life, this creates luxury travelers, foreign-posted professionals with lavish lifestyles, artists whose best work is never shown publicly, spiritual devotees whose practice is deeply personal, and individuals whose expenditure on comfort consistently exceeds their budget. The private dimension of this placement deepens throughout life, with the most significant spiritual or romantic experiences occurring between 30-48. Watch out for secret affairs that unravel and cause public embarrassment, spending on luxury that creates genuine financial hardship, sleep disruption from an overactive romantic or fantasy life, and reproductive or foot-related health issues that manifest in the mid-30s.',
    },
    'Saturn': {
        1: 'Disciplined, serious personality that appears older and more mature than actual age, with a slow start in life but enduring, hard-won success that outlasts flashier peers. Psychologically, the native carries a heavy sense of responsibility from childhood: they feel as though life demands more from them than from others, creating either deep resilience or chronic self-pity depending on how the energy is channeled. In real life, this creates leaders in administration, government, law, manufacturing, and any field requiring sustained discipline over decades; the physical body tends toward leanness in youth and heaviness in old age, with dental and bone issues being lifelong themes. The restrictive effects ease significantly after age 30-33 (Saturn maturity), with the most productive and rewarding period arriving between 36-55. Watch out for chronic pessimism that becomes a self-fulfilling prophecy, health issues in childhood and youth that clear up with age, fear-based decision-making that causes the native to miss opportunities, and joint, bone, or dental problems that require consistent preventive care.',
        2: 'Restricted family wealth in youth with speech that is measured, sparse, and carries the weight of someone who only says what absolutely needs to be said. Psychologically, scarcity is imprinted early: even when the native becomes financially comfortable later in life, there remains a deep anxiety about money running out, leading to either extreme frugality or compensatory overspending during brief periods of false confidence. In real life, this creates wealth that builds very slowly but very solidly after age 30, careers in mining, agriculture, manufacturing, or any industry dealing with raw materials, and a family atmosphere that is serious, traditional, and emotionally restrained. Financial stability arrives between 30-42, with genuine abundance possible between 42-55. Watch out for stinginess that damages family relationships, speech so harsh or sparse that loved ones feel emotionally starved, dental and throat problems that require attention throughout life, and food habits that are either too austere or compensatorily indulgent.',
        3: 'Disciplined, persistent communicator who achieves through sustained effort what others attempt through talent, with hard-working siblings and courage built on endurance rather than impulse. Psychologically, the native approaches every communication task as serious work: they do not dash off emails, speak casually in meetings, or write without careful revision, which produces reliable but slow output that frustrates fast-paced environments. In real life, this creates technical writers, traditional media professionals, government communications officers, and anyone whose communication role requires accuracy over speed; siblings tend to work in labor-intensive or traditional fields. The communication skills mature significantly after age 28-30, with the most authoritative period between 35-50. Watch out for being perceived as boring or overly cautious in communication, strained sibling relationships due to the native\'s judgmental attitude, shoulder, arm, or hearing issues that develop in the 30s, and a tendency to suppress self-expression out of fear of criticism.',
        4: 'Delayed home ownership, a mother who works hard and ages visibly under life\'s pressures, and happiness that arrives late but is deeply appreciated when it comes. Psychologically, the native carries a foundational insecurity about belonging: childhood may have involved frequent moves, a cold home atmosphere, or emotional unavailability from a hardworking mother, creating an adult who either clings to property obsessively or avoids domestic commitment entirely. In real life, this manifests as old, traditional, or inherited property, homes in rural or industrial areas, slow but solid real estate investments, and eventual domestic peace that feels earned rather than given. The home situation typically improves dramatically after age 32-35, with genuine domestic contentment arriving between 40-55. Watch out for chronic dissatisfaction with housing that no renovation can fix, projecting childhood domestic pain onto adult family members, respiratory or chest issues aggravated by damp or old housing, and a home atmosphere so serious that children grow up feeling emotionally restricted.',
        5: 'Delayed children, serious and structured approach to education, losses in speculation, and intelligence built through disciplined effort rather than natural brilliance. Psychologically, the native struggles with spontaneous creativity and play: the inner child is heavily supervised by an internal authority figure, making it difficult to relax into joy, take creative risks, or express affection to children without attaching conditions. In practice, this creates late parenthood (after 30-35), children who are serious and responsible beyond their years, academic success through grinding persistence, and a deep aversion to gambling or speculation of any kind. The restrictive effects on children and creativity ease after age 33-36, with the native often becoming a better parent and more freely creative in their 40s. Watch out for overly strict parenting that damages children\'s spontaneity, treating education as punishment rather than exploration, digestive or stomach issues driven by chronic anxiety, and romantic relationships that feel more like obligations than joys.',
        6: 'Strong placement for defeating enemies through outlasting them, managing chronic but non-fatal health conditions with discipline, and achieving legal victories through patient, thorough preparation. Psychologically, the native accepts suffering as a fact of life rather than fighting against it: while others crumble under sustained adversity, this person keeps grinding, making them formidable in legal battles, workplace politics, and health management. In practice, this creates successful labor lawyers, chronic disease managers, quality-control professionals, government auditors, and anyone whose job requires persistence against ongoing resistance. The ability to handle enemies and health challenges improves significantly after age 28, with peak effectiveness between 33-50. Watch out for normalizing suffering to the point where you do not seek help when it is available, chronic joint, bone, or skin conditions that require lifelong management, workplace enemies who outlast you through institutional power rather than personal stamina, and a tendency to view all relationships through the lens of duty rather than joy.',
        7: 'Delayed marriage with a spouse who is older, mature, or carries heavy responsibilities, and a partnership that improves with time like wine improving with age. Psychologically, the native approaches marriage with the seriousness of a business contract: love is necessary but insufficient, and the partnership must demonstrate practical viability, long-term sustainability, and mutual responsibility before commitment feels justified. In real life, this creates marriages after age 28-32, spouses in traditional professions like law, administration, agriculture, or manufacturing, and relationships that outsiders may perceive as joyless but which provide deep, quiet satisfaction to the partners. The marriage dynamic improves steadily after the initial difficult period, with the best years typically being 35-55. Watch out for being so cautious about marriage that you miss compatible partners, a coldness in the relationship that the spouse experiences as emotional withholding, legal or bureaucratic complications in the marriage process, and back or kidney issues that develop in the late 30s from the stress of partnership responsibilities.',
        8: 'Longevity is enhanced by Saturn\'s natural protection of the 8th house, though chronic health issues and slow, grinding transformations replace sudden catastrophes. Psychologically, the native has an unusually mature relationship with mortality and crisis: they do not fear death or disaster in the way others do, having developed a philosophical acceptance early in life, often through premature exposure to suffering or loss. In real life, this creates careers in insurance, mining, archaeology, gerontology, or any field dealing with slow processes of decay and renewal; inheritance may come late and through legal complexity. The transformative episodes are drawn out rather than sudden, with the most significant occurring between ages 28-42. Watch out for chronic illnesses of the bones, joints, or skin that require lifelong management, depression triggered by the grinding nature of transformation (it never ends quickly), procrastinating necessary medical procedures out of stoic fatalism, and joint or spinal issues that worsen significantly after age 40.',
        9: 'Strict, traditional father who may be emotionally distant or burdened by heavy responsibilities, and fortune that arrives late but through disciplined, orthodox channels. Psychologically, the native\'s relationship with dharma is serious, structured, and devoid of ecstasy: faith is practiced through discipline rather than devotion, and the person may struggle to distinguish between genuine spiritual growth and mere adherence to rules. In practice, this creates success in traditional law, orthodox religious institutions, government administration, elder care, and any field where established structures reward patient compliance; the father is typically hardworking but emotionally reserved. Fortune begins to flow after age 30-33, with the most blessed period arriving between 36-55. Watch out for confusing tradition with truth, rigid religious views that prevent genuine spiritual expansion, a cold or distant relationship with the father that haunts the native throughout life, and hip, thigh, or lower-back problems that develop during long periods of seated traditional study or work.',
        10: 'One of Saturn\'s best placements: career authority built slowly, methodically, and durably, with government, administrative, manufacturing, or structural roles bringing lasting recognition. Psychologically, the native is a builder in the deepest sense: they derive satisfaction not from quick wins but from constructing something that endures beyond their lifetime, whether it is an institution, a career legacy, or a body of work. In practice, this creates government administrators, judges, corporate CEOs who rose from the bottom, manufacturing leaders, structural engineers, and anyone whose career is defined by steady, decades-long ascent through demonstrated reliability. Career acceleration begins around age 28-30, with peak authority arriving between 36-55 and often extending well into the 60s. Watch out for sacrificing personal relationships on the altar of career ambition, becoming so identified with your position that retirement triggers depression, chronic back, knee, or joint issues from years of high-responsibility physical or mental work, and a management style so demanding that talented subordinates leave.',
        11: 'Gains that arrive after middle age, with steady income growth through traditional industries, older or established friends, and long-term desires fulfilled through patient persistence rather than fortunate timing. Psychologically, the native measures success in decades rather than quarters: they accept that major desires will take 10-20 years to fulfill and are genuinely comfortable with this timeline, which gives them an enormous advantage over impatient competitors. In real life, income grows slowly but irreversibly through government, manufacturing, mining, agriculture, or institutional work; friends tend to be older, in traditional fields, and valued for reliability rather than excitement. The most significant gains arrive between ages 36-55, with the period after 45 often being the most financially abundant. Watch out for social isolation due to a serious demeanor that discourages casual friendship, income growth so slow that it tests even Saturn\'s famous patience, elder sibling relationship strain rooted in disagreements over pace and method, and joint or circulatory issues that develop in the late 40s from years of deferred self-care.',
        12: 'Foreign land connections, periods of isolation or institutional confinement, spiritual discipline built on austerity, and work in hospitals, prisons, or ashrams where service to the suffering is the daily reality. Psychologically, the native is drawn to solitude not for escapism but for the genuine spiritual growth that structured isolation provides; they may spend extended periods in monasteries, foreign countries, or institutional settings and emerge more powerful rather than diminished. In real life, this creates workers in foreign mines, hospital administrators, prison officials, monks in austere orders, and anyone whose career involves serving people in confined or restrictive environments. The foreign or institutional dimension of life intensifies after age 28-30, with the most meaningful service or spiritual experiences occurring between 36-55. Watch out for depression triggered by prolonged isolation, foot, ankle, or left-eye problems that require consistent attention, spending on foreign ventures that provide spiritual but not financial returns, and a tendency toward martyrdom where suffering is glorified rather than addressed.',
    },
    'Rahu': {
        1: 'Unconventional, magnetically charismatic personality that fascinates and confuses others in equal measure, with powerful foreign connections and an obsessive relationship with self-image. Psychologically, the native experiences a fundamental uncertainty about who they are: the personality is constantly being reinvented, projected, and tested against social feedback, creating someone who can be anyone but struggles to simply be themselves. In real life, this creates politicians, actors, social media influencers, immigrants, cultural boundary-crossers, and anyone whose power comes from projecting a carefully constructed persona; foreign elements in appearance, lifestyle, or professional field are common. The identity experimentation is most intense between ages 18-36, with greater self-acceptance developing after age 42. Watch out for identity crises that lead to radical and regrettable life changes, substance abuse as a shortcut to altered self-perception, chronic skin or neurological conditions triggered by anxiety about self-image, and a pattern of reinvention that prevents building lasting relationships or career momentum.',
        2: 'Wealth through unconventional, boundary-crossing, or morally ambiguous means, with a family that has mixed cultural backgrounds and speech that can be extraordinarily persuasive or deliberately deceptive. Psychologically, the native has an insatiable hunger for wealth that is never truly satisfied: each financial milestone immediately recalibrates upward, creating perpetual dissatisfaction that drives relentless accumulation. In real life, this creates careers in foreign trade, cryptocurrency, multilingual commerce, cross-cultural business, and any field where conventional rules do not fully apply; the family may include foreign marriages, cultural mixing, or unconventional belief systems. Wealth grows rapidly during Rahu dasha and during the 30s-40s, but volatility remains a lifelong theme. Watch out for tax complications from unconventional income sources, family discord from clashing cultural values, speech used to deceive or manipulate in financial dealings, and throat or dental issues that manifest during periods of intense financial stress.',
        3: 'Bold, fearless communicator with natural dominance in media, technology, and digital platforms, and siblings who are unconventional, foreign-connected, or rebellious. Psychologically, the native craves cutting-edge communication: they are drawn to whatever medium is newest, most disruptive, and most likely to amplify their voice beyond conventional reach. In real life, this creates social media stars, tech entrepreneurs, media disruptors, viral content creators, and anyone whose communication breaks conventional boundaries; siblings may live abroad or work in unusual fields. The communicative power peaks during Rahu\'s dasha and between ages 28-42, when the native learns to combine Rahu\'s boldness with enough substance to sustain attention. Watch out for spreading misinformation for attention, siblings who are unreliable or create scandals, digital addiction that substitutes online presence for real-life connection, and shoulder or nervous system disorders from excessive screen time and stimulation.',
        4: 'Foreign or unusual home environment, a mother with unique cultural or spiritual background, and a domestic life characterized by restlessness and constant desire for something different. Psychologically, the native can never feel fully settled: every home eventually feels like a cage, every neighborhood feels wrong, and there is an unrelenting pull toward somewhere else that may be geographical, emotional, or existential. In real life, this creates frequent relocations, homes in foreign countries or multicultural neighborhoods, unusual living arrangements, and property acquired through unconventional means. The domestic restlessness is most acute between ages 22-40, with the native often finding relative peace after age 42, especially if they embrace a non-traditional definition of home. Watch out for spending recklessly on property that never satisfies, straining the maternal relationship through constant departure, anxiety and insomnia driven by domestic dissatisfaction, and chest or lung issues exacerbated by environmental changes from frequent relocation.',
        5: 'Unconventional intelligence, speculation through technology or foreign markets, children who may live abroad or follow non-traditional paths, and romantic attractions to people outside one\'s cultural norm. Psychologically, the native\'s creative and intellectual process is driven by obsession rather than discipline: they dive deep into subjects with manic intensity, produce brilliant but erratic work, and then abandon the topic entirely when the obsession fades. In real life, this creates tech innovators, foreign-educated scholars, cryptocurrency or options speculators, cross-cultural romance, and creative work that is ahead of its time but poorly understood by contemporaries. The intellectual and creative powers are most volatile between ages 22-38, with greater stability and focused brilliance arriving after 40. Watch out for speculative losses from overconfidence in unconventional strategies, children who rebel against the native\'s own rebelliousness, romantic obsessions that override practical judgment, and stomach or digestive disorders triggered by the anxiety of high-risk intellectual and financial bets.',
        6: 'One of Rahu\'s best placements: the native defeats enemies through cunning, unconventional strategy, and an ability to play outside the rules that competitors cannot match. Psychologically, the native thrives in adversarial environments because they instinctively see angles that rule-followers miss: where others see a problem, this person sees an exploit, and where others play defense, this person changes the game entirely. In real life, this creates trial lawyers who use unprecedented legal strategies, doctors using alternative or cutting-edge treatments, competitors who win through innovation rather than superiority, and healers who combine traditional and unconventional methods. The competitive advantage strengthens after age 24 and peaks between 30-48. Watch out for crossing ethical boundaries in the pursuit of victory, health issues that defy conventional diagnosis (requiring alternative medicine), making enemies of people who later prove more powerful than expected, and chronic anxiety or immune disorders triggered by constant combat-readiness.',
        7: 'Foreign spouse or unconventional marriage that defies family expectations, business partnerships with foreigners, and an obsessive quality to partnerships that can be both intensely bonding and ultimately suffocating. Psychologically, the native projects enormous desire onto the partner: the spouse is expected to fill a void that no single person can fill, leading to cycles of idealization and disappointment that characterize the relationship dynamic. In real life, this creates cross-cultural marriages, business with foreign partners, marriages that shock the family, and relationships that begin with intense mutual fascination. The partnership dynamic is most volatile between ages 24-38, with greater stability and acceptance arriving after 42. Watch out for marrying someone to rebel against family expectations rather than out of genuine love, partnership obsessions that override rational assessment, business dealings with foreign partners that involve hidden agendas, and reproductive or lower-back health issues tied to the intensity of partnership dynamics.',
        8: 'Deep immersion in occult sciences, tantra, and hidden knowledge, with sudden life events that arrive without warning, foreign inheritance, and transformation through unconventional or taboo means. Psychologically, the native is drawn to the forbidden with an intensity that can be either profoundly transformative or utterly destructive: they cannot resist looking behind the curtain, opening the locked door, or exploring the cave that others fear to enter. In real life, this creates tantric practitioners, forensic specialists, intelligence operatives, hackers (ethical or otherwise), and researchers in fields that most people find disturbing or incomprehensible. The most intense transformative periods are between ages 28-42, with the native either emerging as deeply wise or deeply damaged by their encounters with the hidden world. Watch out for paranormal experiences that destabilize mental health, sudden catastrophes that arrive with no logical precursor, obsessive pursuit of occult power that isolates from normal relationships, and mysterious health conditions that defy medical explanation.',
        9: 'Questioning, iconoclastic approach to traditional beliefs, foreign gurus, unconventional philosophies, and pilgrimages to unusual or foreign sacred sites. Psychologically, the native cannot accept inherited religious or philosophical frameworks without testing them to destruction: they must break the old temple before they can build a new one, which creates both visionary reformers and rootless spiritual vagrants. In real life, this creates converts to foreign religions, students of unconventional philosophies, foreign university experiences that fundamentally alter worldview, and teachers who challenge orthodox dogma. The questioning period is most intense between ages 24-40, with the native often finding their own unique synthesis of wisdom after 42. Watch out for rejecting wisdom simply because it is traditional, falling under the influence of charismatic but exploitative foreign gurus, spiritual tourism that substitutes novelty for depth, and hip or lower-back issues during extended foreign travel.',
        10: 'Career in technology, foreign companies, politics, or mass media, with an unconventional rise to power that bypasses traditional hierarchies and an ability to command public attention through sheer magnetic presence. Psychologically, the native is driven by an almost predatory ambition: they do not merely want success but need to succeed on a scale and in a manner that conventional pathways cannot accommodate, leading them to create new categories rather than compete within existing ones. In real life, this creates tech CEOs, political outsiders who win through populist appeal, media moguls, foreign multinational executives, and professionals whose career trajectory has no conventional template. The career ascent is most dramatic between ages 28-48, with Rahu dasha being a pivotal period. Watch out for career scandals from shortcuts taken during the rise, enemies created by an unconventional path who wait for vulnerability, public reputation volatility that mirrors Rahu\'s inherent instability, and neurological or chronic stress conditions caused by the relentless pursuit of power.',
        11: 'One of Rahu\'s absolute best placements: massive gains through technology, foreign networks, mass-market strategies, and influential friends from diverse backgrounds. Psychologically, the native has an uncanny ability to sense where mass desire is heading next: they are early adopters, trend-setters, and network builders whose social circle is a source of wealth rather than mere companionship. In real life, this creates technology entrepreneurs, network marketers, political fundraisers, foreign trade magnates, and anyone who profits from connecting diverse groups of people around emerging opportunities. The gains accelerate dramatically during Rahu dasha and between ages 28-48, with the most spectacular financial successes often arriving suddenly and seemingly from nowhere. Watch out for ethical shortcuts in the pursuit of massive gains, friendships that are purely transactional despite appearing warm, gains that come so easily they create complacency about due diligence, and chronic anxiety or sleep disorders from maintaining too many complex social and financial networks simultaneously.',
        12: 'Foreign settlement, vivid dreams, psychic visions, hidden or clandestine activities, and a spiritual journey marked by confusion, breakthrough, and confusion again in recurring cycles. Psychologically, the native experiences a profound pull toward dissolution: the boundaries between self and other, real and imagined, waking and dreaming are unusually thin, which can produce genuine mystical experience or destabilizing dissociation depending on psychological groundedness. In real life, this creates foreign settlers, spiritual seekers in remote ashrams, professionals in overseas institutions, people involved in hidden or classified work, and individuals whose most significant life experiences occur in places far from their birthplace. The foreign and spiritual dimensions intensify between ages 28-42, with the most significant breakthroughs or crises occurring during Rahu dasha. Watch out for mental health issues triggered by spiritual practices undertaken without proper guidance, hidden expenses that create serious financial damage, substance abuse as a shortcut to spiritual experience, and foot, eye, or sleep disorders that manifest during periods of intense spiritual or foreign-land activity.',
    },
    'Ketu': {
        1: 'Spiritual, detached personality with a mysterious aura that simultaneously attracts and unsettles others, past-life skills that surface without formal training, and health issues concentrated in the head region. Psychologically, the native experiences selfhood as an illusion they have already seen through: where Rahu in the 1st house obsessively builds identity, Ketu in the 1st house instinctively dismantles it, creating a person who is eerily calm in situations that would destabilize others but who may struggle with basic self-assertion. In real life, this creates spiritual healers, mystics, diagnosticians with uncanny intuition, and professionals whose expertise seems to come from nowhere; the person often dresses simply, avoids mirrors, and seems indifferent to personal appearance. The detachment deepens throughout life, with the most significant spiritual realizations occurring after age 33-36. Watch out for passivity mistaken for spirituality, headaches or neurological conditions that recur throughout life, difficulty motivating yourself for material tasks that seem pointless, and a tendency to drift through life without practical anchors that provide stability.',
        2: 'Detachment from family wealth and material accumulation, with speech that carries spiritual depth but lacks commercial persuasiveness, and knowledge that seems to come from past lifetimes rather than current study. Psychologically, the native does not value money in the way their family and culture expect: they may earn well but fail to save, or possess knowledge worth monetizing but lack the desire to do so, creating frustration among family members who cannot understand the indifference. In real life, this creates spiritual counselors who work for donations, scholars of ancient knowledge, professionals who leave lucrative careers for meaningful work, and individuals whose family wealth dwindles or transforms in their generation. The detachment from material wealth intensifies through the 30s and typically consolidates into a clear philosophical position by the mid-40s. Watch out for financial vulnerability from genuine disinterest in money management, family conflicts rooted in the native\'s refusal to pursue wealth, speech that is so abstract or mystical that it fails to communicate practical needs, and dental or throat issues that manifest periodically throughout life.',
        3: 'Courage that comes from spiritual certainty rather than physical bravery, distant or spiritually oriented siblings, and communication that is mystical rather than practical. Psychologically, the native has already mastered the art of courage in past lives: they do not need to prove their bravery and may even find conventional courage pointless, preferring to face challenges through acceptance and surrender rather than resistance. In real life, this creates spiritual writers, practitioners of healing touch, people who influence through silence rather than speech, and professionals whose communication carries an otherworldly quality that either captivates or confuses. The spiritual dimension of communication deepens through life, with the most powerful expression emerging after age 30-36. Watch out for siblings feeling disconnected from the native\'s spiritual orientation, communication so abstract that practical messages fail to land, missed business opportunities from inability to market oneself, and arm, shoulder, or hearing issues that manifest as the native withdraws further from conventional communication.',
        4: 'Detachment from home comforts and conventional domestic happiness, a mother who is spiritually inclined or psychologically distant, and a tendency to leave the birthplace in search of something that cannot be found in any physical location. Psychologically, the native has a deep sense that they do not belong here: "here" meaning their home, their hometown, their country, or even the physical world itself, creating a perpetual inner homesickness for a place they have never been in this lifetime. In real life, this creates monks who leave home permanently, spiritual seekers who live in ashrams, professionals who relocate to remote areas, and individuals who renounce property ownership on principle or through disinterest. The pull away from conventional home life strengthens through the 20s and often results in a definitive departure by the late 30s or early 40s. Watch out for abandoning family responsibilities under the guise of spiritual seeking, children who feel emotionally abandoned by the native\'s detachment, chest or heart-related conditions linked to ungrounded emotional life, and a pattern of moving homes frequently without ever feeling settled.',
        5: 'Past-life intelligence surfaces without formal training, children may be spiritually inclined or unusually perceptive, intuitive learning bypasses conventional education, and mantra siddhi (mastery through repetition) is achievable. Psychologically, the native does not need to be taught what they already know: knowledge arrives as recognition rather than discovery, and the person may perform poorly in structured education while demonstrating inexplicable mastery in unrelated fields. In real life, this creates prodigies, intuitive healers, meditation teachers, astrologers whose readings are uncannily accurate, and parents whose children display spiritual maturity beyond their years. The past-life abilities become more accessible after age 28-33, with the most significant spiritual or intuitive breakthroughs occurring between 33-48. Watch out for children who are so spiritually oriented that they struggle with worldly demands, neglecting formal education because intuition seems sufficient, speculative losses from trusting gut feeling over analytical evidence, and stomach or digestive conditions that correlate with periods of intense spiritual practice.',
        6: 'Victory over enemies through spiritual power, karmic protection, and an ability to dissolve conflict without engaging in it, making this an excellent placement for healers and alternative medicine practitioners. Psychologically, the native does not fight enemies so much as render them irrelevant: conflicts seem to resolve themselves or enemies self-destruct without the native taking any visible action, which can be genuinely mystical or simply the result of an energy that disarms aggression. In real life, this creates Ayurvedic practitioners, energy healers, spiritual therapists, alternative medicine doctors, and professionals who heal through presence rather than intervention; mysterious illnesses that defy conventional diagnosis respond well to alternative treatments. The healing and protective abilities strengthen after age 27-30. Watch out for neglecting conventional medical treatment in favor of exclusively spiritual approaches, mysterious health conditions that recur cyclically without clear cause, underestimating enemies because past conflicts resolved easily, and immune or digestive issues that require both conventional and alternative care.',
        7: 'Detachment from conventional marriage, a spouse who is spiritually inclined or emotionally elusive, and past-life partner karma that creates either immediate deep recognition or persistent disconnection. Psychologically, the native has already completed the lessons of partnership in previous lives: marriage does not hold the same fascination or urgency that it does for others, and the person may marry out of social pressure rather than genuine desire, leading to a relationship that is correct but uninspired. In real life, this creates late marriages, marriages to spiritual practitioners, relationships where physical presence coexists with emotional distance, and individuals who find more fulfillment in solitary spiritual practice than in partnership. The detachment from conventional partnership dynamics intensifies through the 30s, with the native often reaching a point of genuine acceptance (rather than frustrated resignation) by their mid-40s. Watch out for making the spouse feel emotionally starved through spiritual indifference, avoiding necessary relationship work by labeling marital desire as attachment, reproductive health issues linked to energetic withdrawal from physical intimacy, and the risk of losing a good partner because you could not communicate your unconventional needs.',
        8: 'One of Ketu\'s most powerful placements: deep occult mastery, genuine moksha potential, past-life spiritual attainments surfacing as present-life abilities, and potential for kundalini awakening. Psychologically, the native has an intimate, fearless relationship with death, transformation, and the hidden dimensions of existence that would terrify most people; they walk through crises with the calm of someone who has died and been reborn many times before. In real life, this creates powerful mystics, past-life regression therapists, practitioners of kundalini yoga, mediums whose abilities are genuine rather than performed, and researchers in parapsychology or esoteric science. The occult abilities deepen significantly after age 28-33, with the most transformative spiritual experiences occurring between 33-48. Watch out for kundalini experiences that overwhelm an unprepared nervous system, becoming so absorbed in esoteric pursuits that worldly functionality deteriorates, mysterious health conditions in the reproductive or eliminative systems, and the danger of spiritual pride that comes from genuine occult attainment.',
        9: 'The dharma path has already been walked in past lives, creating a natural philosopher who does not need to seek wisdom because it already lives within them. Psychologically, the native has a relationship with truth that is direct and non-intellectual: they know things without knowing how they know, and formal religious or philosophical education may feel redundant and frustrating. In real life, this creates sages who teach without credentials, individuals whose presence conveys wisdom without words, healers whose guidance comes from an unknown source, and people who are sought out for counsel despite having no formal training. The father may be physically or emotionally absent, spiritually inclined, or from a lineage that carries inherited wisdom. The sage-like qualities strengthen throughout life, becoming most visible after age 33-40. Watch out for father being absent or the relationship being marked by spiritual disconnection rather than warmth, using past-life wisdom as an excuse to avoid current-life learning, becoming an armchair philosopher who dispenses wisdom but does not act, and hip or lower-back issues that manifest during the 40s.',
        10: 'Detachment from conventional career ambition, with success arriving without the intense striving that others require, and past-life professional skills surfacing in the current incarnation. Psychologically, the native does not define themselves through their career: work is something that happens to them rather than something they pursue, and the most significant professional contributions may occur almost accidentally, without strategic planning or political maneuvering. In real life, this creates spiritual leaders who did not seek leadership, professionals whose reputation is built on quality others recognize before they do, healers and counselors whose practice grows through word of mouth rather than marketing, and individuals who seem underemployed relative to their actual abilities. The career path clarifies after age 30-33, with the most meaningful professional contributions arriving between 36-50. Watch out for wasting genuine professional talents through spiritual indifference, colleagues and competitors taking credit for work the native is too detached to claim, chronic underearning relative to ability, and knee or back issues that develop from the physical neglect that accompanies career detachment.',
        11: 'Gains arrive without active desire or pursuit, spiritual friendships that nourish the soul rather than the bank account, detachment from material desires, and unexpected fulfillments that confirm karmic merit. Psychologically, the native has a paradoxical relationship with desire: the things they want least are the things that arrive most easily, while the rare things they do pursue seem to slip away, teaching a lesson about surrender that eventually becomes the native\'s greatest source of peace. In real life, this creates individuals who receive inheritance, gifts, or opportunities without seeking them, friendships with monks, healers, and spiritual practitioners, and a social circle that outsiders may view as impractical but which provides genuine soul nourishment. The pattern of effortless receipt strengthens after age 30 and becomes most consistent between 36-50. Watch out for difficulty setting financial goals because desire feels spiritually inappropriate, friendships so oriented toward spirit that practical mutual support is absent, elder sibling relationships marked by disconnection or spiritual divergence, and circulatory or leg issues that correlate with periods of extreme material detachment.',
        12: 'The best moksha placement in the entire chart: liberation-oriented consciousness, past-life spiritual mastery carrying forward, ashram or monastery connections, and a soul that is completing its final worldly lessons. Psychologically, the native experiences the material world as a dream from which they are slowly awakening: nothing worldly holds permanent fascination, and there is a gravitational pull toward dissolution that can manifest as sublime spiritual attainment or, if resisted, as depression and existential emptiness. In real life, this creates monks, nuns, spiritual hermits, meditation masters, past-life healers whose abilities are self-evident, and individuals who naturally gravitate toward ashrams, pilgrimage, and the service of the dying. The spiritual pull strengthens throughout life, with the most powerful liberating experiences occurring after age 33 and often culminating in a definitive spiritual commitment between 40-55. Watch out for using spiritual transcendence to avoid dealing with unresolved worldly responsibilities, foot or left-eye issues that manifest throughout life, insomnia or unusual sleep patterns as consciousness shifts between planes, and the risk of spiritual isolation becoming clinical depression when the native has not found genuine practice or community.',
    },
}

# Nakshatra effects on planets
_NAKSHATRA_EFFECTS = {
    'Ashwini': 'Quick results, healing ability, pioneer energy',
    'Bharani': 'Intense transformation, creative power, bearing heavy responsibilities',
    'Krittika': 'Sharp intellect, cutting through illusion, purifying fire',
    'Rohini': 'Material abundance, beauty, fertility, creative expression',
    'Mrigashira': 'Searching nature, curiosity, gentle but restless energy',
    'Ardra': 'Storms before calm, destruction leading to renewal, emotional depth',
    'Punarvasu': 'Return to goodness, renewal, wisdom regained after loss',
    'Pushya': 'Nourishing, spiritual growth, best nakshatra for general prosperity',
    'Ashlesha': 'Cunning intelligence, mystical power, serpent wisdom, hidden strength',
    'Magha': 'Royal lineage energy, ancestral blessings, authority and throne',
    'Purva Phalguni': 'Creativity, romance, luxury, artistic celebration of life',
    'Uttara Phalguni': 'Patronage, helping others, steady prosperity, reliable character',
    'Hasta': 'Skilled hands, craftsmanship, practical intelligence, healing touch',
    'Chitra': 'Architectural brilliance, beauty creation, gem-like multi-faceted talent',
    'Swati': 'Independence, flexibility, diplomatic skill, wind-like adaptability',
    'Vishakha': 'Determined goal-pursuit, one-pointed focus, triumph after long effort',
    'Anuradha': 'Devotion, friendship, success in foreign lands, organizational skill',
    'Jyeshtha': 'Seniority, protective nature, occult power, chief among peers',
    'Mula': 'Root destruction for new growth, research, getting to the bottom of things',
    'Purva Ashadha': 'Invincibility, purifying waters, unstoppable forward momentum',
    'Uttara Ashadha': 'Final victory, universal leadership, unchallengeable authority',
    'Shravana': 'Listening, learning, connecting, knowledge through hearing sacred texts',
    'Dhanishtha': 'Wealth, musical talent, group leadership, Mars-like courage',
    'Shatabhisha': 'Healing hundred diseases, secretive nature, electrical/tech energy',
    'Purva Bhadrapada': 'Burning intensity, funeral pyre energy, spiritual warrior',
    'Uttara Bhadrapada': 'Deep ocean wisdom, Saturn-like discipline, serpent of the depths',
    'Revati': 'Safe travel, nourishing, final journey, compassionate shepherd energy',
}


def analyze_planets(chart):
    """Generate detailed analysis for each of the 9 planets with deep cross-referencing."""
    analyses = []

    for planet in PLANETS:
        p = chart['planets'][planet]
        house = p['house']
        sign = p['sign']
        dignity = p['dignity']
        nakshatra = p['nakshatra']
        nak_lord = p['nakshatra_lord']
        is_retro = p['is_retrograde']
        is_combust = p.get('is_combust', False)
        degree = p['degree']

        placement = _PLANET_IN_HOUSE.get(planet, {}).get(house, f'{planet} in house {house}.')

        house_sig = HOUSE_SIGNIFICATIONS.get(house, '').split(',')[0].strip().lower()
        karaka_theme = KARAKAS.get(planet, '').split(',')[0].strip().lower()
        sign_lord = SIGN_LORDS.get(sign, '')

        # ── Dignity effect (deep) ──
        dignity_effects = {
            'Exalted': (
                f'{planet} is exalted in {sign}, its strongest possible placement. '
                f'Your {karaka_theme} and house {house} matters ({house_sig}) are naturally strong and produce results without excessive effort. '
                f'During {planet}\'s dasha period, expect recognition and tangible gains in these areas. '
                f'This placement protects house {house} matters throughout life.'
            ),
            'Moolatrikona': (
                f'{planet} is in moolatrikona in {sign}, nearly as strong as exaltation with a sharper focus on productive output. '
                f'{planet} actively drives results in house {house} ({house_sig}) matters and {karaka_theme} themes. '
                f'During {planet}\'s dasha, expect significant accomplishments in these areas. '
                f'This is a dependable, high-performing placement.'
            ),
            'Own Sign': (
                f'{planet} sits in its own sign ({sign}), making it stable and self-sufficient. '
                f'House {house} matters ({house_sig}) are well-protected and run smoothly throughout life. '
                f'During {planet}\'s dasha, these areas function reliably without major disruptions. '
                f'{karaka_theme.capitalize()} themes carry a quiet, lasting strength.'
            ),
            'Friendly': (
                f'{planet} is in {sign}, ruled by its friend {sign_lord}, giving it solid support. '
                f'House {house} ({house_sig}) matters progress well with moderate effort. '
                f'Results are good, and the dasha periods of both {planet} and {sign_lord} tend to be cooperative. '
                f'Not the strongest placement, but dependably positive.'
            ),
            'Neutral': (
                f'{planet} is in {sign}, a neutral sign, so house {house} ({house_sig}) results depend heavily on aspects and the running dasha. '
                f'A benefic aspect can elevate this planet significantly; a malefic aspect can drag it down. '
                f'Your actions and remedies have the most impact on a neutral-dignity planet. '
                f'{karaka_theme.capitalize()} themes are workable but need conscious attention.'
            ),
            'Enemy': (
                f'{planet} is in {sign}, ruled by its enemy {sign_lord}, so house {house} ({house_sig}) matters require double the effort. '
                f'{karaka_theme.capitalize()} themes face persistent resistance, especially before age 32-35. '
                f'After that age, the sustained effort builds a resilience that others lack. '
                f'Remedies for {planet} are recommended to ease the friction.'
            ),
            'Debilitated': (
                f'{planet} is debilitated in {sign}, its weakest placement. '
                f'House {house} ({house_sig}) matters and {karaka_theme} themes struggle in the first half of life. '
                f'A turning point comes between ages 30-36 when accumulated experience begins converting struggle into hard-won competence. '
                f'Check for Neecha Bhanga (debilitation cancellation) and prioritize remedies for this planet.'
            ),
        }
        dignity_text = dignity_effects.get(dignity, f'{planet} is {dignity} in {sign}.')

        # ── Nakshatra (deep — includes nak lord analysis) ──
        nak_effect = _NAKSHATRA_EFFECTS.get(nakshatra, 'Standard nakshatra influence.')
        nak_lord_house = _house(chart, nak_lord) if nak_lord in chart['planets'] else None
        nak_lord_dignity = _dignity(chart, nak_lord) if nak_lord in chart['planets'] else None
        nak_text = (
            f'{planet} in {nakshatra} nakshatra (lord: {nak_lord}, pada {p["pada"]}). '
            f'This adds the quality of {nak_effect.lower()} to {planet}\'s expression. '
        )
        if nak_lord_house:
            nak_lord_sig = HOUSE_SIGNIFICATIONS.get(nak_lord_house, '').split(',')[0].strip().lower()
            nak_text += (
                f'The nakshatra lord {nak_lord} sits in house {nak_lord_house} ({nak_lord_dignity}), '
                f'meaning the deeper impulse behind {planet}\'s actions connects to {nak_lord_sig} matters. '
            )
            if nak_lord_dignity in ('Exalted', 'Own Sign'):
                nak_text += f'Since {nak_lord} is strong, the nakshatra energy supports {planet} well — deeper motivations are healthy.'
            elif nak_lord_dignity in ('Debilitated', 'Enemy'):
                nak_text += f'Since {nak_lord} is weak, the underlying motivation driving {planet} may be conflicted until awareness develops.'

        # ── Retrograde (deep) ──
        retro_text = ''
        if is_retro and planet not in ('Sun', 'Moon', 'Rahu', 'Ketu'):
            retro_text = (
                f'Retrograde {planet} delays {karaka_theme}-related results and house {house} ({house_sig}) matters until the early-to-mid 30s. '
                f'The energy turns inward first, so you develop deep internal understanding of these themes before external results show up. '
                f'After age 30-35, a breakthrough often arrives as the accumulated internal work converts into visible progress. '
                f'Expect second chances and revised decisions around house {house} matters throughout life.'
            )

        # ── Combustion (deep) ──
        combust_text = ''
        if is_combust:
            dist = p.get('sun_distance', 0)
            severity_note = 'strong' if dist < 5 else ('moderate' if dist < 10 else 'mild')
            combust_text = (
                f'{planet} is combust ({dist:.1f} degrees from the Sun, {severity_note} effect). '
                f'Your {karaka_theme}-related abilities are real but stay hidden or get overshadowed. '
                f'In daily life, this shows up as others taking credit for your work or circumstances preventing you from showcasing these strengths. '
                f'Remedies for both {planet} and Sun help bring these suppressed qualities to the surface.'
            )

        # ── Aspects (deep with dignity context) ──
        aspects_received = []
        for other in PLANETS:
            if other == planet:
                continue
            if _aspects_planet(chart, other, planet):
                other_d = chart['planets'][other]
                nature = 'benefic' if other in NATURAL_BENEFICS else 'malefic'
                aspects_received.append({
                    'planet': other, 'nature': nature,
                    'from_sign': other_d['sign'], 'from_house': other_d['house'],
                    'dignity': other_d['dignity'],
                })

        aspects_text = ''
        if aspects_received:
            parts = []
            for a in aspects_received:
                if a['nature'] == 'benefic':
                    q = 'powerfully supports and blesses' if a['dignity'] in ('Exalted', 'Own Sign') else 'supports with constructive energy'
                else:
                    if a['dignity'] in ('Exalted', 'Own Sign'):
                        q = 'puts intense pressure that builds character'
                    elif a['dignity'] in ('Debilitated', 'Enemy'):
                        q = 'creates friction, though the weak malefic\'s damage is limited'
                    else:
                        q = 'challenges with moderate pressure demanding growth'
                parts.append(f'{a["planet"]} ({a["dignity"]}) from {a["from_sign"]} (H{a["from_house"]}) {q}')
            benefic_count = sum(1 for a in aspects_received if a['nature'] == 'benefic')
            malefic_count = len(aspects_received) - benefic_count
            tail = ''
            if benefic_count > malefic_count:
                tail = f' Overall, {planet} receives more support than pressure — its results are enhanced.'
            elif malefic_count > benefic_count:
                tail = f' Overall, {planet} faces more pressure than support — resilience and remedies are needed.'
            aspects_text = '. '.join(parts) + '.' + tail

        # ── House lord (deep) ──
        house_lord = _house_lord(chart, house)
        lord_text = ''
        if house_lord != planet:
            lord_dignity = _dignity(chart, house_lord)
            lord_house = _house(chart, house_lord)
            lord_sign = _sign(chart, house_lord)
            lord_house_sig = HOUSE_SIGNIFICATIONS.get(lord_house, '').split(',')[0].strip().lower()
            if lord_dignity in ('Exalted', 'Own Sign', 'Moolatrikona'):
                lord_text = (
                    f'Your house {house} ({house_sig}) is ruled by {house_lord}, who sits strongly in {lord_sign} '
                    f'({lord_dignity}) in house {lord_house}. This means {house_sig} and {lord_house_sig} '
                    f'matters reinforce each other, and {house_lord} gives {planet} a solid foundation to deliver results.'
                )
            elif lord_dignity in ('Debilitated', 'Enemy'):
                lord_text = (
                    f'Your house {house} ({house_sig}) is ruled by {house_lord}, who is weak in {lord_sign} '
                    f'({lord_dignity}, house {lord_house}). This undercuts {planet}\'s ability to deliver fully. '
                    f'Strengthening {house_lord} through remedies would indirectly improve {planet}\'s results too.'
                )
            else:
                lord_text = (
                    f'Your house {house} ({house_sig}) is ruled by {house_lord} in {lord_sign} '
                    f'({lord_dignity}, house {lord_house}). Adequate support, linking {house_sig} to '
                    f'{lord_house_sig} matters. This connection activates during either planet\'s dasha.'
                )

        # ── Conjunctions ──
        conjuncts = [n for n in PLANETS if n != planet and _house(chart, n) == house]
        conjunction_text = ''
        if conjuncts:
            conj_parts = []
            for c in conjuncts:
                if c in NATURAL_FRIENDS.get(planet, []):
                    conj_parts.append(f'{c} (friend) amplifies {planet}\'s positive results')
                elif c in NATURAL_ENEMIES.get(planet, []):
                    conj_parts.append(f'{c} (enemy) creates tension — both planets compromise each other')
                else:
                    conj_parts.append(f'{c} (neutral) adds {KARAKAS.get(c, "").split(",")[0].strip().lower()} themes alongside')
            conjunction_text = (
                f'{planet} shares house {house} with {", ".join(conjuncts)}. '
                f'Conjunctions blend energies — the planets must cooperate in expressing through the same house. '
                f'{". ".join(conj_parts)}. '
                f'During the dasha of any conjunct planet, {planet}\'s themes also activate simultaneously.'
            )

        # ── Dasha activation ──
        dasha_note = ''
        for d in chart['dashas']['dashas']:
            if d['lord'] == planet and d.get('is_current'):
                dasha_note = (
                    f'{planet}\'s Mahadasha is currently active ({d["start"].strftime("%b %Y")} to {d["end"].strftime("%b %Y")}). '
                    f'House {house} matters ({house_sig}) are in full focus right now. What you are experiencing in '
                    f'this area is directly driven by {planet}\'s placement and condition described above. '
                    f'Pay close attention — these are not theoretical predictions, they are active.'
                )
                break

        # ── Synthesized narrative ──
        strength_parts = []
        if dignity in ('Exalted', 'Own Sign', 'Moolatrikona'):
            strength_parts.append(f'{dignity.lower()} dignity')
        if sum(1 for a in aspects_received if a['nature'] == 'benefic') > 0:
            strength_parts.append('benefic aspects')
        weakness_parts = []
        if dignity in ('Debilitated', 'Enemy'):
            weakness_parts.append(f'{dignity.lower()} dignity')
        if is_retro and planet not in ('Sun', 'Moon', 'Rahu', 'Ketu'):
            weakness_parts.append('retrograde status (delays results until 30s)')
        if is_combust:
            weakness_parts.append('combustion (hidden talents)')

        narrative = f'{planet} in house {house} shapes your {karaka_theme} and {house_sig} matters. '
        if strength_parts:
            narrative += f'With {" and ".join(strength_parts)}, this is one of the stronger planets in your chart. '
        if weakness_parts:
            narrative += f'Challenges here include {" and ".join(weakness_parts)}, so remedies and patience help. '
        if conjuncts:
            narrative += f'Conjunction with {", ".join(conjuncts)} adds complexity to house {house}. '

        analyses.append({
            'planet': planet, 'sign': sign, 'house': house, 'degree': degree,
            'dignity': dignity, 'nakshatra': nakshatra, 'pada': p['pada'],
            'is_retrograde': is_retro, 'is_combust': is_combust,
            'placement': placement, 'dignity_effect': dignity_text,
            'nakshatra_effect': nak_text, 'retrograde_effect': retro_text,
            'combustion_effect': combust_text, 'aspects_received': aspects_received,
            'aspects_text': aspects_text, 'house_lord_text': lord_text,
            'conjunction_text': conjunction_text, 'dasha_note': dasha_note,
            'narrative': narrative,
        })

    return analyses


# ════════════════════════════════════════════════════════════════
# SECTION 3: LAL KITAB PREDICTIONS
# ════════════════════════════════════════════════════════════════

_LAL_KITAB = {
    'Sun': {
        1: {
            'prediction': 'Government favors, authority in workplace. Father is supportive. Health remains strong till 45. Copper and wheat bring luck.',
            'remedy': 'Throw a copper coin in flowing water every Sunday. Keep solid silver ball in pocket.',
        },
        2: {
            'prediction': 'Family wealth increases through government or authority. Eye-related issues possible. Speech carries power but can create enemies.',
            'remedy': 'Keep a solid piece of jaggery (gur) at home. Serve your father and elderly men.',
        },
        3: {
            'prediction': 'Brave and adventurous. Brothers prosper. Good for media and publishing. Travels bring gains.',
            'remedy': 'Offer water mixed with jaggery to the Sun at sunrise. Donate saffron or turmeric.',
        },
        4: {
            'prediction': 'Government property possible but domestic peace disturbed. Mother faces health issues. Happiness comes through discipline.',
            'remedy': 'Do not accept free items. Offer wheat and jaggery in a temple. Keep the kitchen clean.',
        },
        5: {
            'prediction': 'Intelligent children, gains through speculation. Government recognition. Romance with influential person.',
            'remedy': 'Offer almonds in a temple on Sunday. Apply saffron tilak on forehead.',
        },
        6: {
            'prediction': 'Victory in legal matters. Maternal uncle\'s support. Health recovers quickly. Enemies are weak.',
            'remedy': 'Feed jaggery to monkeys. Keep a dark room in the house closed.',
        },
        7: {
            'prediction': 'Late marriage but spouse from good family. Government partnerships. Father-in-law is influential.',
            'remedy': 'Do not accept donations. Offer wheat flour balls to fish. Marry after 24.',
        },
        8: {
            'prediction': 'Government troubles, father\'s health issues. Inheritance disputes. Sudden falls from position.',
            'remedy': 'Throw raw coal (koyla) in flowing water. Never live in a house facing south. Keep a square piece of silver.',
        },
        9: {
            'prediction': 'Pilgrimage brings fortune. Father is religious. Government honors after 33. Teaching or preaching profession.',
            'remedy': 'Offer water to Sun every morning. Do not eat non-veg on Sundays. Serve your father.',
        },
        10: {
            'prediction': 'King-like status at work. Government job guaranteed. Night shifts harmful. Fame after 22.',
            'remedy': 'Offer jaggery and wheat to temple. Never accept free items. Keep a pet cow or serve one.',
        },
        11: {
            'prediction': 'Gains from government. Elder brother prospers. Social circle is powerful. Wealth increases steadily.',
            'remedy': 'Donate wheat or jaggery on Sundays. Keep copper utensils at home.',
        },
        12: {
            'prediction': 'Government posting abroad. Eyes weaken. Sleep on a wooden bed. Father lives far away.',
            'remedy': 'Throw jaggery in flowing water. Do not accept dowry. Offer water to Peepal tree.',
        },
    },
    'Moon': {
        1: {
            'prediction': 'Popular personality, emotional nature. Mother is influential. Wealth from public dealings. Face is attractive.',
            'remedy': 'Keep a silver glass of water near bed at night. Wear white clothes on Mondays. Serve your mother.',
        },
        2: {
            'prediction': 'Sweet speech, family prosperity. Wealthy through nurturing businesses. Mother\'s blessings bring fortune.',
            'remedy': 'Donate white rice on Mondays. Keep silver items at home. Never speak lies.',
        },
        3: {
            'prediction': 'Creative writing ability. Sisters/daughters bring luck. Short travels near water bodies bring peace.',
            'remedy': 'Offer milk to Shivling on Mondays. Keep a silver ball in pocket.',
        },
        4: {
            'prediction': 'Best placement. Very close to mother. Beautiful home near water. Happiness and peace from 24 onwards.',
            'remedy': 'Install a hand pump or arrange drinking water facility. Serve your mother daily.',
        },
        5: {
            'prediction': 'Romantic, dreamy nature. Children bring emotional fulfillment. Gains through women-related businesses.',
            'remedy': 'Offer milk and rice to a religious place on Mondays. Donate silver to a girl child.',
        },
        6: {
            'prediction': 'Mental stress from enemies. Stomach issues. Mother\'s health fluctuates. Serve in hospitals for relief.',
            'remedy': 'Donate milk to temple. Do not keep rainwater stored at home. Wear a silver chain.',
        },
        7: {
            'prediction': 'Caring spouse. Public dealings successful. Multiple partnerships. Business of dairy or liquids.',
            'remedy': 'Bury a silver square piece in foundation of your home. Drink water from silver glass.',
        },
        8: {
            'prediction': 'Inheritance through mother. Deep intuition. Eye/mental health issues. Mother needs care after 45.',
            'remedy': 'Do not sell milk or water. Keep silver ball at home. Offer rice to birds.',
        },
        9: {
            'prediction': 'Fortune through mother\'s side. Pilgrimage to river temples. Spiritual through devotion. Good character.',
            'remedy': 'Offer water to roots of a Banyan tree. Serve old women. Donate white cloth.',
        },
        10: {
            'prediction': 'Fame through public work. Changing career but always connected to masses. Dairy/water/shipping business.',
            'remedy': 'Keep a container of water or milk on your rooftop. Use silver utensils.',
        },
        11: {
            'prediction': 'Gains from women, mother, and public. Many daughters. Desires fulfilled through emotional intelligence.',
            'remedy': 'Donate milk on Mondays. Pour milk on Shivling. Wear pearl or moonstone.',
        },
        12: {
            'prediction': 'Disturbed sleep, vivid dreams. Mother may be far away. Eye problems. Psychic abilities develop.',
            'remedy': 'Keep a pot of water near your head while sleeping. Donate white items on Mondays.',
        },
    },
    'Mars': {
        1: {
            'prediction': 'Strong personality, scars on body. Hot temper but brave. Land/property owner. Blood-related issues possible.',
            'remedy': 'Throw a red masoor dal into flowing water on Tuesdays. Keep a pet deer or serve animals.',
        },
        2: {
            'prediction': 'Arguments about money. Family fights. Harsh speech. Wealth through property, metal, or engineering.',
            'remedy': 'Feed sweet bread (meethi roti) to dogs. Keep a solid silver square in your safe. Avoid red meat.',
        },
        3: {
            'prediction': 'Very courageous. Dominates siblings. Good in military, police. Writes with fire and passion.',
            'remedy': 'Donate sweet food to temple. Carry a red handkerchief. Offer sindoor to Hanuman.',
        },
        4: {
            'prediction': 'Property through effort. Blood pressure issues. Mother\'s health concerns. Fire hazard at home — install safety.',
            'remedy': 'Keep a square piece of silver in your home foundation. Apply honey on navel at night. Serve your brother.',
        },
        5: {
            'prediction': 'Smart but impulsive children. Speculation losses through haste. Love marriage with conflict.',
            'remedy': 'Feed birds with tandoori roti. Keep an ivory/bone item at home. Donate blood on Tuesdays.',
        },
        6: {
            'prediction': 'Destroys all enemies. Excellent health. Wins every competition. Police/military career flourishes.',
            'remedy': 'Donate jaggery and gram (chana) on Tuesdays. Feed sweet chapati to dogs.',
        },
        7: {
            'prediction': 'Manglik effects on marriage. Passionate but argumentative spouse. Surgery of spouse possible. Late marriage advised.',
            'remedy': 'Kumbh Vivah before marriage. Feed sweet chapati to dogs. Wear Red Coral on ring finger.',
        },
        8: {
            'prediction': 'Accident risk before 28. Surgery likely. Inheritance from in-laws. Keep away from fire and weapons.',
            'remedy': 'Bury a square piece of sindoor in an isolated place. Donate blood. Feed sweet food to crows.',
        },
        9: {
            'prediction': 'Father is a fighter or in uniform. Religious through action not prayer. Property away from birthplace.',
            'remedy': 'Feed sweet food in temple. Carry a silver brick. Do not lie about anything.',
        },
        10: {
            'prediction': 'Commanding career. Police, military, surgery, engineering. Authority through action. Fame after 28.',
            'remedy': 'Keep a pet with brown/red fur. Offer sindoor to Hanuman. Never eat non-veg on Tuesdays.',
        },
        11: {
            'prediction': 'Gains through property, metal, engineering. Elder brother is aggressive. Friends in uniform.',
            'remedy': 'Donate sweet food in temple on Tuesdays. Keep a solid silver piece in safe.',
        },
        12: {
            'prediction': 'Hidden anger. Expenses on property. Surgery/hospitalization. Spouse may be from far away.',
            'remedy': 'Throw red masoor dal in flowing water. Sleep on a deer skin. Offer sindoor to Hanuman.',
        },
    },
    'Mercury': {
        1: {
            'prediction': 'Intelligent, youthful look. Business mind. Green color suits you. Education brings success.',
            'remedy': 'Wear a copper coin with hole in green thread around neck. Donate green moong dal on Wednesdays.',
        },
        2: {
            'prediction': 'Excellent speech. Banking success. Multiple languages. Daughters bring luck. Teeth stay strong.',
            'remedy': 'Get your nose pierced (for women) or keep a nose ring at home. Float green moong in water.',
        },
        3: {
            'prediction': 'Writer, journalist, media person. Siblings in business. Communication career guaranteed. Quick traveler.',
            'remedy': 'Donate green cloth in temple. Wear an emerald pendant. Feed green grass to cows.',
        },
        4: {
            'prediction': 'Educated household. Mother is intelligent. Academic property. Multiple homes through smart dealings.',
            'remedy': 'Bury a bronze vessel with honey in foundation of home. Feed green fodder to cows.',
        },
        5: {
            'prediction': 'Genius children. Stock market analyst. Education in elite institutions. Witty romancer.',
            'remedy': 'Donate educational material to poor students. Keep a green parrot (or image) at home.',
        },
        6: {
            'prediction': 'Analytical victory over enemies. Skin issues. Good doctor or lawyer. Maternal uncle is wealthy.',
            'remedy': 'Float green items in water on Wednesdays. Keep goats or serve them. Donate green vegetables.',
        },
        7: {
            'prediction': 'Business partnerships thrive. Spouse is educated and communicative. Marriage through friendship.',
            'remedy': 'Fill an earthen pot with honey and bury it in a deserted place. Wear green on Wednesdays.',
        },
        8: {
            'prediction': 'Research and investigation career. Insurance/audit/taxation. Hidden knowledge. Inheritance through intelligence.',
            'remedy': 'Donate green moong and green cloth on Wednesdays. Do not live in a south-facing home.',
        },
        9: {
            'prediction': 'Higher education guaranteed. Teaching career. Father is intellectual. Foreign education likely.',
            'remedy': 'Donate green items in a religious school (madrasa/gurukul). Serve intellectuals and teachers.',
        },
        10: {
            'prediction': 'Career in IT, media, communication, accounting. Multiple career changes. Versatile professional.',
            'remedy': 'Keep a bronze pot of water on your work desk. Wear a green thread. Feed birds.',
        },
        11: {
            'prediction': 'Gains through intellect and networks. Multiple income streams. Friends in media/business world.',
            'remedy': 'Donate green vegetables on Wednesdays. Keep an emerald or green glass at home.',
        },
        12: {
            'prediction': 'Expenses on education. Foreign education. Research in isolation. Dreams carry messages.',
            'remedy': 'Float green moong in flowing water. Do not keep birds in cage. Donate to libraries.',
        },
    },
    'Jupiter': {
        1: {
            'prediction': 'Respected personality. Guru-like aura. Weight gain after 30. Wise advisor. Gold brings luck.',
            'remedy': 'Wear a yellow thread. Apply saffron tilak. Visit temple on Thursdays. Serve your guru/teacher.',
        },
        2: {
            'prediction': 'Wealthy family. Excellent speaker. Banking/finance career. Gold accumulation. Family traditions strong.',
            'remedy': 'Donate yellow items (turmeric, chana dal) on Thursdays. Keep gold in your safe. Serve Brahmins.',
        },
        3: {
            'prediction': 'Philosophical writer. Siblings respect you. Religious journalism. Brave through wisdom not force.',
            'remedy': 'Donate saffron in temple. Wear yellow on Thursdays. Serve at educational institutions.',
        },
        4: {
            'prediction': 'Grand home. Learned mother. Higher education. Happiness through knowledge. Temple at home beneficial.',
            'remedy': 'Apply saffron on your forehead daily. Keep sacred texts at home. Donate to temples.',
        },
        5: {
            'prediction': 'Brilliant children. Past-life merit. Academic honors. Speculation gains. Spiritual wisdom.',
            'remedy': 'Offer saffron rice to temple deity. Wear yellow sapphire. Teach underprivileged children.',
        },
        6: {
            'prediction': 'Wins through righteousness. Good doctor/healer. Enemies become friends. Charity defeats obstacles.',
            'remedy': 'Feed yellow laddu in temple. Donate gold coin. Serve at charitable hospitals.',
        },
        7: {
            'prediction': 'Wise spouse (excellent for women — indicates good husband). Happy marriage. Business through ethics.',
            'remedy': 'Donate turmeric on Thursdays. Wear yellow sapphire on index finger. Respect your spouse.',
        },
        8: {
            'prediction': 'Long life. Occult knowledge. Ancestral property inheritance. Deep philosophy. Transforms through wisdom.',
            'remedy': 'Throw yellow turmeric in flowing water on Thursdays. Visit Vishnu temple. Donate yellow cloth.',
        },
        9: {
            'prediction': 'The luckiest placement. Father is noble. Foreign fortune. Guru blesses. Dharma flows naturally.',
            'remedy': 'Serve your father and guru. Donate to temples. Apply saffron tilak daily. Visit pilgrimage sites.',
        },
        10: {
            'prediction': 'Career in teaching, law, finance, advisory. Government recognition. Ethical authority. Fame through wisdom.',
            'remedy': 'Offer yellow flowers at workplace. Donate chana dal on Thursdays. Wear yellow sapphire.',
        },
        11: {
            'prediction': 'Abundant gains. Wealthy friends. Elder siblings prosper. All desires fulfilled through righteousness.',
            'remedy': 'Donate to educational trusts. Offer saffron in temple. Feed Brahmins on Thursdays.',
        },
        12: {
            'prediction': 'Moksha path. Spiritual guru. Foreign residence near temple. Charity brings peace. Hospital philanthropy.',
            'remedy': 'Donate to old-age homes. Visit Vishnu temple on Thursdays. Wear yellow. Serve sadhus.',
        },
    },
    'Venus': {
        1: {
            'prediction': 'Beautiful face, magnetic personality. Artistic talent. Women bring luck. Luxury lover. Skin glows.',
            'remedy': 'Donate white items on Fridays. Keep a silver diamond-shaped piece at home. Serve women.',
        },
        2: {
            'prediction': 'Sweet speaker. Family wealth through beauty/arts. Good food lover. Beautiful teeth and face.',
            'remedy': 'Donate rice and white sugar on Fridays. Keep silver and diamond at home. Respect women.',
        },
        3: {
            'prediction': 'Artistic communication. Creative siblings. Fashion/media career. Travels for art and pleasure.',
            'remedy': 'Donate perfume or white cloth on Fridays. Wear white or cream colors. Gift flowers to women.',
        },
        4: {
            'prediction': 'Beautiful home. Luxury vehicles. Mother is beautiful. Happiness through comfort. Interior design talent.',
            'remedy': 'Bury a diamond-shaped silver piece in home foundation. Keep flowers at home. Serve your wife.',
        },
        5: {
            'prediction': 'Romantic life. Beautiful children. Cinema/entertainment gains. Artistic genius. Love affairs successful.',
            'remedy': 'Donate silver star to temple. Offer white flowers to Lakshmi. Feed rice to Brahmins.',
        },
        6: {
            'prediction': 'Enemies through love. Kidney/sugar problems. Spouse faces health issues. Avoid extramarital affairs.',
            'remedy': 'Donate white items in temple on Fridays. Keep camphor at home. Feed cows.',
        },
        7: {
            'prediction': 'Beautiful spouse. Happy marriage. Business of beauty/luxury. Partnership of equals. Married bliss.',
            'remedy': 'Give wife white gifts on Fridays. Donate sweets to girls. Keep home fragrant with flowers.',
        },
        8: {
            'prediction': 'Secret wealth through spouse. Tantric knowledge. Sudden marriage events. In-law\'s property gains.',
            'remedy': 'Throw rice in flowing water on Fridays. Keep a diamond or opal. Serve widows.',
        },
        9: {
            'prediction': 'Fortune through arts, women, beauty business. Wife is from good family. Foreign travel for pleasure.',
            'remedy': 'Donate white clothes to women on Fridays. Offer white flowers in temple. Respect women elders.',
        },
        10: {
            'prediction': 'Career in fashion, beauty, cinema, hospitality. Fame through creative work. Luxury lifestyle.',
            'remedy': 'Keep fresh flowers on work desk. Donate to women welfare on Fridays. Wear white/cream at work.',
        },
        11: {
            'prediction': 'Gains through women and arts. Wealthy female friends. Luxury gains. All material desires fulfilled.',
            'remedy': 'Donate white sweets on Fridays. Gift perfume to wife. Serve cows.',
        },
        12: {
            'prediction': 'Bed pleasures. Foreign luxury. Expenses on beauty. Secret love affairs. Spiritual through devotion.',
            'remedy': 'Donate white clothes and silver on Fridays. Visit Lakshmi temple. Keep bedroom beautiful.',
        },
    },
    'Saturn': {
        1: {
            'prediction': 'Hard life in youth, success after 36. Dark complexion or serious look. Disciplined. Knee/joint issues.',
            'remedy': 'Donate mustard oil on Saturdays. Serve the handicapped. Keep an iron ring. Feed crows.',
        },
        2: {
            'prediction': 'Restricted family wealth initially. Says less, means more. Teeth problems. Wealth after patience.',
            'remedy': 'Donate black urad dal on Saturdays. Keep iron safe. Do not drink milk at night.',
        },
        3: {
            'prediction': 'Hardworking siblings. Serious communicator. Courage through persistence. Late success in writing.',
            'remedy': 'Donate iron items on Saturdays. Feed stray dogs. Carry a horseshoe for protection.',
        },
        4: {
            'prediction': 'Old-style home. Mother works very hard. Happiness comes after 40. Property through patience.',
            'remedy': 'Pour milk on Peepal tree roots. Keep iron nails buried in home\'s four corners. Serve your mother.',
        },
        5: {
            'prediction': 'Children come late. Serious student. Speculation losses. Romance with older person. Past-life debts.',
            'remedy': 'Donate almonds in temple. Offer milk and water at Peepal tree. Serve old teachers.',
        },
        6: {
            'prediction': 'Defeats enemies through persistence. Chronic but manageable health. Good lawyer/judge. Service career.',
            'remedy': 'Feed black dogs. Donate iron or dark blue cloth on Saturdays. Serve at hospitals.',
        },
        7: {
            'prediction': 'Late or second marriage. Older/mature spouse. Marriage improves with years. Business partnerships after 32.',
            'remedy': 'Gift iron items to wife. Donate oil on Saturdays. Build patience in marriage.',
        },
        8: {
            'prediction': 'Long life but chronic issues. Slow transformation. In-laws have old money. Research career.',
            'remedy': 'Donate iron and mustard oil on Saturdays. Keep Shani yantra at home. Feed crows and dogs.',
        },
        9: {
            'prediction': 'Strict father. Fortune delayed till 36. Dharma through hard work not luck. Traditional beliefs.',
            'remedy': 'Serve your father. Donate black items on Saturdays. Visit Shani temple. Feed Brahmins.',
        },
        10: {
            'prediction': 'Government career after 30. Manufacturing or mining. Authority through discipline. Fame through hard work.',
            'remedy': 'Offer mustard oil at Shani temple on Saturdays. Keep iron items at workplace. Serve workers.',
        },
        11: {
            'prediction': 'Gains after 36. Income grows slowly but surely. Older friends. Conservative financial growth.',
            'remedy': 'Donate black sesame (til) on Saturdays. Feed stray animals. Carry iron.',
        },
        12: {
            'prediction': 'Foreign land karma. Isolation or imprisonment risk. Spiritual discipline. Hospital/asylum connections.',
            'remedy': 'Donate mustard oil and blankets on Saturdays. Visit Shani temple. Serve beggars and disabled.',
        },
    },
    'Rahu': {
        1: {
            'prediction': 'Magnetic personality but confusing to others. Foreign connections strong. Obsessive about image. Head issues.',
            'remedy': 'Keep a solid silver ball. Donate radish (mooli) on Wednesdays. Do not keep dogs or electrical items in bedroom.',
        },
        2: {
            'prediction': 'Family wealth through unconventional means. Speech can deceive. In-laws bring luck. Teeth problems.',
            'remedy': 'Keep a solid silver brick. Donate coconut in temple. Never speak against family.',
        },
        3: {
            'prediction': 'Tech media success. Bold communicator. Siblings unconventional. Foreign short trips profitable.',
            'remedy': 'Keep a silver square piece. Donate mustard seeds on Wednesdays. Use electronics for good.',
        },
        4: {
            'prediction': 'Foreign property. Electronic items in home. Mother has unique background. Restless domestic life.',
            'remedy': 'Keep silver in home foundation. Donate coal. Do not keep electrical items in south-west corner.',
        },
        5: {
            'prediction': 'Tech-savvy children. Speculation through technology. Unusual romance or love from different community.',
            'remedy': 'Donate 5 radishes in temple. Keep a silver elephant at home. Serve your children.',
        },
        6: {
            'prediction': 'Wins over enemies through cunning. Unusual healing. Tech used for problem-solving. Maternal uncle abroad.',
            'remedy': 'Keep a black dog or feed stray dogs. Donate coal on Saturdays. Use tech for charity.',
        },
        7: {
            'prediction': 'Foreign spouse or from different background. Unconventional marriage. Business with foreigners.',
            'remedy': 'Keep a silver brick at home. Donate coconut in flowing water. Delay marriage if possible.',
        },
        8: {
            'prediction': 'Sudden events, occult interest. Foreign inheritance. Deep research into taboo subjects.',
            'remedy': 'Keep a silver ball in dark place. Donate sesame and coconut. Do not visit graves at night.',
        },
        9: {
            'prediction': 'Unconventional guru or philosophy. Fortune from foreign land. Father may be abroad or unconventional.',
            'remedy': 'Donate coconut in river. Keep silver square at home. Respect your father despite differences.',
        },
        10: {
            'prediction': 'Career in tech, foreign companies, politics. Unconventional rise. Fame through mass appeal.',
            'remedy': 'Keep a silver plate on work desk. Donate electronic items for education. Offer coconut in temple.',
        },
        11: {
            'prediction': 'Gains through technology, foreign contacts. Network marketing. Influential diverse friend circle.',
            'remedy': 'Donate radish and coconut. Keep silver items. Use social media for good causes.',
        },
        12: {
            'prediction': 'Foreign settlement likely. Dreams vivid and prophetic. Hidden activities. Spiritual confusion.',
            'remedy': 'Keep a silver brick under pillow. Donate blankets. Pour milk on Shivling. Avoid alcohol.',
        },
    },
    'Ketu': {
        1: {
            'prediction': 'Mysterious personality. Past-life spiritual skills. Head injuries or marks. Detached from self-image.',
            'remedy': 'Wear a silver cap or keep a silver piece on top of head area. Donate a grey blanket. Feed dogs.',
        },
        2: {
            'prediction': 'Not interested in wealth accumulation. Family may not understand you. Spiritual speech. Eye issues.',
            'remedy': 'Donate a white and grey blanket. Feed stray dogs. Keep sacred ash (vibhuti) at home.',
        },
        3: {
            'prediction': 'Courage through spiritual strength. Siblings distant. Mystical writing. Past-life communication skills.',
            'remedy': 'Donate grey items. Keep a black and white dog. Offer sesame in temple.',
        },
        4: {
            'prediction': 'Detached from home. Mother is spiritual. May leave birthplace. Vehicles cause trouble.',
            'remedy': 'Keep a dog at home. Donate grey/brown blankets. Apply saffron on forehead.',
        },
        5: {
            'prediction': 'Past-life intelligence. Children may be spiritual. Mantra siddhi possible. Intuitive learning.',
            'remedy': 'Donate a blanket to a sadhu. Keep a dog. Worship Lord Ganesha. Recite Ganesh mantra.',
        },
        6: {
            'prediction': 'Defeats enemies spiritually. Good healer. Alternative medicine works. Mysterious illnesses resolve.',
            'remedy': 'Feed dogs and donate grey items. Keep sacred ash. Serve at animal shelters.',
        },
        7: {
            'prediction': 'Detached from marriage. Spiritual partner. Past-life partner karma. Marriage for dharma not desire.',
            'remedy': 'Keep a dog at home. Donate two-toned blanket. Wear cat\'s eye stone after consultation.',
        },
        8: {
            'prediction': 'Deep occult knowledge. Past-life spiritual attainments. Kundalini experiences. Moksha potential.',
            'remedy': 'Donate blankets in temple. Keep a dog. Recite Maha Mrityunjaya mantra. Wear cat\'s eye.',
        },
        9: {
            'prediction': 'Already walked dharma path in past life. Natural philosopher. Father absent or spiritual.',
            'remedy': 'Donate to monasteries. Feed fish. Keep a grey dog. Apply saffron tilak.',
        },
        10: {
            'prediction': 'Success without trying. Past-life professional skills emerge. Detached from career ambition.',
            'remedy': 'Keep a dog at home. Donate blankets on Tuesdays. Offer sesame seeds in temple.',
        },
        11: {
            'prediction': 'Gains without desire. Spiritual friends. Unexpected wealth. Detached from material ambitions.',
            'remedy': 'Feed stray dogs. Donate grey blankets. Keep cat\'s eye stone at home.',
        },
        12: {
            'prediction': 'Best moksha placement. Liberation-oriented soul. Ashram connections. Past-life spiritual master.',
            'remedy': 'Donate to ashrams. Worship Lord Ganesha. Keep a dog. Meditate daily. Wear cat\'s eye.',
        },
    },
}


def get_lal_kitab_predictions(chart):
    """Get Lal Kitab predictions and remedies for each planet based on house placement."""
    predictions = []
    for planet in PLANETS:
        house = _house(chart, planet)
        entry = _LAL_KITAB.get(planet, {}).get(house, {})
        predictions.append({
            'planet': planet,
            'house': house,
            'sign': _sign(chart, planet),
            'prediction': entry.get('prediction', f'{planet} in house {house} — standard placement.'),
            'remedy': entry.get('remedy', f'Worship the deity associated with {planet}.'),
        })
    return predictions


# ════════════════════════════════════════════════════════════════
# SECTION 4: LIFE PREDICTIONS (SCENARIO-BASED)
# ════════════════════════════════════════════════════════════════

# Body parts ruled by each sign (for health predictions)
_SIGN_BODY_PARTS = {
    'Aries': 'head, brain, face, blood pressure',
    'Taurus': 'throat, thyroid, neck, jaw, vocal cords',
    'Gemini': 'lungs, arms, shoulders, nervous system, hands',
    'Cancer': 'stomach, chest, breasts, digestion, uterus',
    'Leo': 'heart, spine, upper back, circulation, eyes',
    'Virgo': 'intestines, lower abdomen, nervous digestion, skin',
    'Libra': 'kidneys, lower back, adrenal glands, skin',
    'Scorpio': 'reproductive organs, bladder, chronic conditions',
    'Sagittarius': 'hips, thighs, liver, sciatic nerve',
    'Capricorn': 'knees, bones, joints, teeth, skeletal system',
    'Aquarius': 'ankles, calves, circulation, nervous disorders',
    'Pisces': 'feet, lymphatic system, immunity, sleep disorders',
}

# Career indications by 10th house sign
_CAREER_BY_SIGN = {
    'Aries': ['military', 'police', 'sports', 'surgery', 'engineering', 'entrepreneurship', 'firefighting'],
    'Taurus': ['banking', 'agriculture', 'hospitality', 'luxury goods', 'real estate', 'food industry', 'jewelry'],
    'Gemini': ['media', 'journalism', 'writing', 'IT', 'trading', 'teaching', 'public relations', 'telecom'],
    'Cancer': ['hospitality', 'nursing', 'real estate', 'shipping', 'dairy', 'catering', 'childcare'],
    'Leo': ['government', 'politics', 'entertainment', 'management', 'gold trading', 'administration'],
    'Virgo': ['healthcare', 'accounting', 'editing', 'analysis', 'pharmacy', 'dietetics', 'quality control'],
    'Libra': ['law', 'diplomacy', 'fashion', 'beauty', 'interior design', 'counseling', 'partnerships'],
    'Scorpio': ['research', 'investigation', 'medicine', 'insurance', 'occult', 'psychology', 'mining'],
    'Sagittarius': ['education', 'law', 'philosophy', 'foreign trade', 'publishing', 'travel industry', 'religion'],
    'Capricorn': ['government', 'manufacturing', 'mining', 'construction', 'administration', 'traditional business'],
    'Aquarius': ['technology', 'science', 'social work', 'innovation', 'NGOs', 'electronics', 'networking'],
    'Pisces': ['healing', 'arts', 'cinema', 'photography', 'spirituality', 'fishing', 'oil industry', 'charity'],
}


def predict_career(chart):
    """Career predictions tied to 10th house, D10, and dasha periods."""
    h10 = chart['houses'][10]
    l10 = h10['lord']
    l10_d = chart['planets'][l10]
    sign_10 = h10['sign']
    occ_10 = h10['occupants']

    # D10 analysis
    d10 = chart['divisional']['D10']
    d10_asc = d10['ascendant']['sign']

    # Career fields
    fields = _CAREER_BY_SIGN.get(sign_10, ['various fields'])

    # Strength assessment
    strength_factors = []
    weakness_factors = []

    if l10_d['dignity'] in ('Exalted', 'Own Sign', 'Moolatrikona'):
        strength_factors.append(f'10th lord {l10} is {l10_d["dignity"]} — career potential is excellent')
    elif l10_d['dignity'] in ('Debilitated', 'Enemy'):
        weakness_factors.append(f'10th lord {l10} is {l10_d["dignity"]} — career requires more effort')

    if _is_kendra(l10_d['house']):
        strength_factors.append(f'10th lord in kendra (H{l10_d["house"]}) — strong professional foundation')
    if _is_dusthana(l10_d['house']):
        weakness_factors.append(f'10th lord in dusthana (H{l10_d["house"]}) — career faces obstacles')

    for p in occ_10:
        if p in NATURAL_BENEFICS:
            strength_factors.append(f'{p} in 10th house enhances career with grace and opportunity')
        elif p in NATURAL_MALEFICS:
            if p == 'Saturn':
                strength_factors.append('Saturn in 10th — hard work brings lasting authority (best placement for Saturn)')
            elif p == 'Mars':
                strength_factors.append('Mars in 10th — commanding, action-oriented career')
            else:
                weakness_factors.append(f'{p} in 10th — career faces {p}-related challenges')

    # Best career periods (dashas activating 10th house or its lord)
    best_periods = []
    challenging_periods = []
    for d in chart['dashas']['dashas']:
        lord = d['lord']
        lord_h = _house(chart, lord)
        # Planet in 10th, or planet IS 10th lord, or planet aspects 10th
        relevant = (lord_h == 10 or lord == l10 or
                    _aspects_planet(chart, lord, l10))
        if relevant:
            if chart['planets'][lord]['dignity'] in ('Exalted', 'Own Sign', 'Friendly'):
                best_periods.append({
                    'period': f'{lord} Mahadasha',
                    'start': d['start'].strftime('%b %Y'),
                    'end': d['end'].strftime('%b %Y'),
                    'reason': f'{lord} activates career house — growth, promotion, recognition',
                })
            elif chart['planets'][lord]['dignity'] in ('Debilitated', 'Enemy'):
                challenging_periods.append({
                    'period': f'{lord} Mahadasha',
                    'start': d['start'].strftime('%b %Y'),
                    'end': d['end'].strftime('%b %Y'),
                    'reason': f'{lord} activates career house but is weak — obstacles, career change needed',
                })

    # Build narrative summary
    occ_text = ''
    if occ_10:
        occ_names = ', '.join(occ_10)
        occ_text = (
            f' The presence of {occ_names} in the 10th house adds '
            f'{"a powerful drive and visible energy" if any(p in NATURAL_MALEFICS for p in occ_10) else "grace and opportunity"} '
            f'to your professional life, shaping the way colleagues and superiors perceive you.'
        )

    strength_narrative = ''
    if strength_factors:
        strength_narrative = (
            ' The underlying structure of your professional chart is solid, meaning that consistent effort '
            'will compound over time and lead to positions of genuine authority.'
        )
    weakness_narrative = ''
    if weakness_factors:
        weakness_narrative = (
            ' There are areas where the professional path demands extra patience and strategic thinking, '
            'particularly during periods when the 10th lord is under transit pressure.'
        )

    _lord_quality = ("operates from a position of strength and can deliver results with relative ease"
                     if l10_d['dignity'] in ('Exalted', 'Own Sign', 'Moolatrikona')
                     else "needs conscious cultivation and patience to deliver its full potential")
    summary = (
        f'Your 10th house falls in {sign_10}, giving your career a natural orientation toward '
        f'{", ".join(fields[:3])} and related fields where {sign_10} qualities find professional expression. '
        f'The lord of the 10th, {l10}, sits in {l10_d["sign"]} in the {l10_d["house"]}th house in a state of '
        f'{l10_d["dignity"]}, which means the driving force behind your career {_lord_quality}.{occ_text}'
        f'{strength_narrative}{weakness_narrative}'
        f' The D10 divisional chart, which specifically maps your professional destiny, rises in {d10_asc}, '
        f'reinforcing the themes of your main chart and adding a layer of professional identity that becomes '
        f'more visible as your career matures.'
    )

    # Build detailed multi-paragraph reading
    # Paragraph 1: 10th house sign and career archetype
    detail_p1 = (
        f'The 10th house in {sign_10} establishes the fundamental archetype of your professional identity. '
        f'{sign_10} energy in the house of karma and public action means you are naturally drawn to environments '
        f'that require {sign_10.lower()}-like qualities: '
        f'{"initiative, leadership, and the courage to pioneer" if sign_10 == "Aries" else ""}'
        f'{"stability, patience, and the ability to build lasting value" if sign_10 == "Taurus" else ""}'
        f'{"communication, versatility, and intellectual agility" if sign_10 == "Gemini" else ""}'
        f'{"emotional intelligence, nurturing, and protective leadership" if sign_10 == "Cancer" else ""}'
        f'{"authority, creative vision, and the confidence to command" if sign_10 == "Leo" else ""}'
        f'{"analytical precision, service orientation, and attention to detail" if sign_10 == "Virgo" else ""}'
        f'{"diplomacy, aesthetic judgment, and partnership management" if sign_10 == "Libra" else ""}'
        f'{"investigative depth, psychological insight, and transformative power" if sign_10 == "Scorpio" else ""}'
        f'{"philosophical breadth, teaching ability, and cross-cultural reach" if sign_10 == "Sagittarius" else ""}'
        f'{"structural discipline, administrative skill, and long-term strategic thinking" if sign_10 == "Capricorn" else ""}'
        f'{"innovation, humanitarian vision, and the ability to work with networks and technology" if sign_10 == "Aquarius" else ""}'
        f'{"creative imagination, healing instinct, and the capacity to work behind the scenes" if sign_10 == "Pisces" else ""}. '
        f'Career fields that align with this energy include {", ".join(fields[:4])}, though the exact expression '
        f'depends heavily on where the 10th lord sits and what planets occupy or aspect this house.'
    )

    # Paragraph 2: 10th lord placement
    lord_house_theme = HOUSE_SIGNIFICATIONS.get(l10_d['house'], 'this domain')
    detail_p2 = (
        f'The lord of your 10th house, {l10}, has landed in the {l10_d["house"]}th house in {l10_d["sign"]} '
        f'({l10_d["dignity"]}). This placement channels your career energy through the themes of house '
        f'{l10_d["house"]}, which governs {lord_house_theme.lower()}. '
        f'{"Because the 10th lord is in a kendra (angular house), your career has a strong and visible foundation, " if _is_kendra(l10_d["house"]) else ""}'
        f'{"Because the 10th lord is in a trikona (trinal house), there is a fortunate alignment between your professional efforts and your life purpose, " if _is_trikona(l10_d["house"]) else ""}'
        f'{"Because the 10th lord is in a dusthana (challenging house), career growth requires navigating obstacles that ultimately build resilience, " if _is_dusthana(l10_d["house"]) else ""}'
        f'and the {l10_d["dignity"].lower()} dignity of {l10} in {l10_d["sign"]} '
        f'{"provides excellent support for professional ambitions" if l10_d["dignity"] in ("Exalted", "Own Sign", "Moolatrikona") else "means you will need to work more consciously to extract the best professional results"}. '
        f'Pay close attention to the dasha periods of {l10}, as these will be the years when career shifts, '
        f'promotions, or redirections are most likely.'
    )

    # Paragraph 3: Occupants and aspects
    detail_p3 = ''
    if occ_10:
        occ_details = []
        for p in occ_10:
            pd = chart['planets'][p]
            occ_details.append(
                f'{p} ({pd["dignity"]} in {pd["sign"]})'
            )
        detail_p3 = (
            f'The 10th house is occupied by {", ".join(occ_details)}, which directly colors your professional '
            f'persona and the way authority figures perceive you. '
            + ' '.join(
                f'{p} in the 10th brings {"aggressive ambition, technical skill, or a commanding presence" if p == "Mars" else ""}'
                f'{"slow but lasting authority, government connections, or work in traditional industries" if p == "Saturn" else ""}'
                f'{"wisdom, ethics, and growth through teaching, law, or advisory roles" if p == "Jupiter" else ""}'
                f'{"creative appeal, diplomacy, and success in beauty, arts, or hospitality" if p == "Venus" else ""}'
                f'{"intellectual versatility, media connections, and frequent career pivots" if p == "Mercury" else ""}'
                f'{"public visibility, authority, and connection to government or leadership" if p == "Sun" else ""}'
                f'{"public popularity, emotional connection with masses, and career fluctuation" if p == "Moon" else ""}'
                f'{"unconventional career path, foreign connections, and sudden rise through technology or politics" if p == "Rahu" else ""}'
                f'{"detachment from career ambition, spiritual vocation, or past-life professional skills surfacing" if p == "Ketu" else ""}.'
                for p in occ_10
            )
        )
    else:
        detail_p3 = (
            'No planets occupy your 10th house directly, which means the career story is told primarily through '
            f'the placement and condition of the 10th lord {l10}. An empty 10th house is not a weakness; it often '
            'indicates a career path that unfolds through the lord\'s house themes rather than through dramatic '
            'events in the career house itself.'
        )

    # Paragraph 4: D10 and timing
    detail_p4 = (
        f'The D10 (Dashamsha) chart, which is the divisional chart specifically dedicated to career and professional '
        f'destiny, rises in {d10_asc}. This adds a secondary layer to your career reading: while the D1 chart shows '
        f'your overall life orientation toward work, the D10 reveals the specific professional environment where you '
        f'thrive. {d10_asc} rising in the D10 suggests that your professional self '
        f'{"leads with courage and initiative" if d10_asc == "Aries" else ""}'
        f'{"values stability and tangible output" if d10_asc == "Taurus" else ""}'
        f'{"excels in communication-driven roles" if d10_asc == "Gemini" else ""}'
        f'{"nurtures teams and builds emotionally safe workplaces" if d10_asc == "Cancer" else ""}'
        f'{"commands attention and gravitates toward leadership" if d10_asc == "Leo" else ""}'
        f'{"thrives on precision, analysis, and service" if d10_asc == "Virgo" else ""}'
        f'{"builds through partnerships and aesthetic judgment" if d10_asc == "Libra" else ""}'
        f'{"investigates, transforms, and wields hidden influence" if d10_asc == "Scorpio" else ""}'
        f'{"teaches, publishes, and expands across borders" if d10_asc == "Sagittarius" else ""}'
        f'{"administers, structures, and builds institutional legacy" if d10_asc == "Capricorn" else ""}'
        f'{"innovates, networks, and disrupts established systems" if d10_asc == "Aquarius" else ""}'
        f'{"heals, creates, and works in behind-the-scenes capacities" if d10_asc == "Pisces" else ""}. '
        f'The best career periods identified in this analysis should be used as windows for major professional '
        f'decisions such as job changes, business launches, or negotiations for authority and compensation.'
    )

    detailed_reading = f'{detail_p1}\n\n{detail_p2}\n\n{detail_p3}\n\n{detail_p4}'

    return {
        'title': 'Career & Profession',
        'tenth_house_sign': sign_10,
        'tenth_lord': l10,
        'tenth_lord_house': l10_d['house'],
        'tenth_lord_dignity': l10_d['dignity'],
        'occupants': occ_10,
        'd10_ascendant': d10_asc,
        'suggested_fields': fields,
        'strength_factors': strength_factors,
        'weakness_factors': weakness_factors,
        'best_periods': best_periods[:3],
        'challenging_periods': challenging_periods[:2],
        'summary': summary,
        'detailed_reading': detailed_reading,
    }


def predict_marriage(chart):
    """Marriage predictions from 7th house, Venus, D9, and dasha timing."""
    h7 = chart['houses'][7]
    l7 = h7['lord']
    l7_d = chart['planets'][l7]
    venus = chart['planets']['Venus']
    occ_7 = h7['occupants']

    # D9 analysis
    d9 = chart['divisional']['D9']
    d9_asc = d9['ascendant']['sign']
    d9_venus = d9.get('Venus', {})

    # Spouse characteristics from 7th sign
    spouse_traits = {
        'Aries': 'Independent, dynamic, possibly short-tempered. Active and adventurous partner.',
        'Taurus': 'Beautiful, sensual, family-oriented. Loves comfort and stability.',
        'Gemini': 'Intellectual, communicative, witty. May be younger or youthful-looking.',
        'Cancer': 'Caring, emotional, nurturing. Home-loving and family-focused.',
        'Leo': 'Dignified, proud, generous. From a well-known or influential family.',
        'Virgo': 'Practical, analytical, health-conscious. Detail-oriented partner.',
        'Libra': 'Beautiful, balanced, diplomatic. Artistic sensibility.',
        'Scorpio': 'Intense, passionate, mysterious. Deep emotional connection.',
        'Sagittarius': 'Philosophical, freedom-loving, adventurous. May be from different background.',
        'Capricorn': 'Mature, responsible, ambitious. Older or serious-minded partner.',
        'Aquarius': 'Unconventional, intellectual, humanitarian. Unique personality.',
        'Pisces': 'Dreamy, spiritual, compassionate. Artistic or healing nature.',
    }

    # Marriage timing analysis
    timing_factors = []
    if l7_d['dignity'] in ('Exalted', 'Own Sign'):
        timing_factors.append('Early to on-time marriage likely (7th lord strong)')
    elif l7_d['dignity'] in ('Debilitated', 'Enemy'):
        timing_factors.append('Marriage may be delayed (7th lord weak)')

    if 'Saturn' in occ_7:
        timing_factors.append('Saturn in 7th delays marriage but gives lasting bond')
    if 'Rahu' in occ_7:
        timing_factors.append('Rahu in 7th — unconventional marriage or foreign spouse')
    if 'Ketu' in occ_7:
        timing_factors.append('Ketu in 7th — detachment from marriage, spiritual partner')

    # Marriage quality
    quality_factors = []
    if venus['dignity'] in ('Exalted', 'Own Sign'):
        quality_factors.append('Venus strong — love, beauty, and harmony in marriage')
    elif venus['dignity'] == 'Debilitated':
        quality_factors.append('Venus debilitated — needs effort to maintain romance and appreciation')
    if venus.get('is_combust'):
        quality_factors.append('Venus combust — love life overshadowed by ego or career')

    # Best marriage periods
    marriage_periods = []
    for d in chart['dashas']['dashas']:
        lord = d['lord']
        lord_h = _house(chart, lord)
        if lord_h == 7 or lord == l7 or lord == 'Venus':
            marriage_periods.append({
                'period': f'{lord} Mahadasha',
                'start': d['start'].strftime('%b %Y'),
                'end': d['end'].strftime('%b %Y'),
            })

    # Build narrative summary
    occ_text = ''
    if occ_7:
        occ_names = ', '.join(occ_7)
        occ_text = (
            f' The presence of {occ_names} in the 7th house directly shapes the texture of your partnerships, '
            f'bringing {"intensity and karmic weight" if any(p in NATURAL_MALEFICS for p in occ_7) else "harmony and grace"} '
            f'to the marriage experience.'
        )

    venus_quality = ''
    if venus['dignity'] in ('Exalted', 'Own Sign'):
        venus_quality = (
            ' Venus, the natural significator of love and marriage, is strong in your chart, which blesses '
            'your romantic life with genuine capacity for affection, beauty appreciation, and sensual fulfillment.'
        )
    elif venus['dignity'] in ('Debilitated', 'Enemy'):
        venus_quality = (
            ' Venus, the planet of love and romance, is under stress in your chart, which means the expression '
            'of affection and the experience of marital harmony require conscious effort and communication.'
        )

    summary = (
        f'Your 7th house falls in {h7["sign"]}, which shapes the fundamental nature of your partnerships and '
        f'the qualities you are drawn to in a spouse: {spouse_traits.get(h7["sign"], "balanced and complementary characteristics")}. '
        f'The lord of the 7th, {l7}, sits in {l7_d["sign"]} in the {l7_d["house"]}th house ({l7_d["dignity"]}), '
        f'revealing that your marriage journey is {"supported by planetary strength and likely to unfold with relative ease" if l7_d["dignity"] in ("Exalted", "Own Sign", "Moolatrikona") else "a karmic growth area that deepens through patience and mutual commitment"}.{occ_text}{venus_quality}'
        f' The Navamsha (D9) chart, which is the soul-map of your married life, rises in {d9_asc}, adding a '
        f'deeper dimension to how your partnership evolves over the decades.'
    )

    # Build detailed multi-paragraph reading
    # Paragraph 1: 7th house sign and spouse archetype
    detail_p1 = (
        f'The 7th house in {h7["sign"]} establishes the archetype of your ideal partner and the emotional tone of '
        f'your married life. {h7["sign"]} energy in the house of partnerships means you are drawn to people who '
        f'embody {h7["sign"].lower()} qualities, and the marriage itself takes on the rhythm of this sign. '
        f'{spouse_traits.get(h7["sign"], "")} This does not mean every relationship will match this description '
        f'perfectly, but it represents the energetic template your soul is seeking in a committed bond. '
        f'The direction from which a spouse may come, their family background, and the circumstances of '
        f'meeting are all colored by this sign placement.'
    )

    # Paragraph 2: 7th lord placement
    lord_house_theme = HOUSE_SIGNIFICATIONS.get(l7_d['house'], 'this domain')
    detail_p2 = (
        f'The lord of your 7th house, {l7}, sits in the {l7_d["house"]}th house in {l7_d["sign"]} ({l7_d["dignity"]}). '
        f'This channels the energy of your partnerships through the themes of house {l7_d["house"]}, which governs '
        f'{lord_house_theme.lower()}. In practical terms, this means that your marriage or primary partnership is '
        f'deeply connected to these life areas: '
        f'{"you may meet your spouse through work or your partner significantly impacts your career" if l7_d["house"] == 10 else ""}'
        f'{"the partner comes through or deeply affects family and financial matters" if l7_d["house"] == 2 else ""}'
        f'{"friendship transforms into love, or the partner enters through social networks" if l7_d["house"] == 11 else ""}'
        f'{"the partner has a spiritual, foreign, or research-oriented connection" if l7_d["house"] in (8, 12) else ""}'
        f'{"the partner is connected to education, children, or creative pursuits" if l7_d["house"] == 5 else ""}'
        f'{"the partnership is central to your identity and highly visible" if l7_d["house"] == 1 else ""}'
        f'{"the partner comes through travel, higher education, or family dharma" if l7_d["house"] == 9 else ""}'
        f'{"the partner relates to communication, siblings, or a nearby community" if l7_d["house"] == 3 else ""}'
        f'{"the partner connects to home, property, or the mother" if l7_d["house"] == 4 else ""}'
        f'{"the partner relates to health, service, or overcoming shared challenges" if l7_d["house"] == 6 else ""}'
        f'{"the relationship is intensely self-referential, both partners mirror each other" if l7_d["house"] == 7 else ""}. '
        f'The {l7_d["dignity"].lower()} state of {l7} '
        f'{"supports a harmonious and timely marriage" if l7_d["dignity"] in ("Exalted", "Own Sign") else "asks for extra patience and maturity in partnerships"}.'
    )

    # Paragraph 3: Venus analysis
    detail_p3 = (
        f'Venus, the karaka (significator) of marriage, love, and beauty, sits in {venus["sign"]} in the '
        f'{venus["house"]}th house ({venus["dignity"]}). Venus\'s condition reveals the quality of romantic '
        f'expression available to you: '
        f'{"strong Venus gives a natural ability to attract love, appreciate beauty, and maintain harmony in intimate relationships" if venus["dignity"] in ("Exalted", "Own Sign") else ""}'
        f'{"Venus in a friendly sign provides decent romantic capacity with room for growth" if venus["dignity"] == "Friendly" else ""}'
        f'{"Venus in a neutral position means romantic fulfillment depends heavily on effort and the partner\'s chart" if venus["dignity"] == "Neutral" else ""}'
        f'{"Venus under stress means love is experienced through challenges that ultimately deepen appreciation for genuine connection" if venus["dignity"] in ("Debilitated", "Enemy") else ""}. '
        f'Venus in house {venus["house"]} colors your love life with the themes of that house, and '
        f'{"combustion weakens Venus\'s ability to express love openly, sometimes hiding romantic feelings behind ambition or ego" if venus.get("is_combust") else "Venus is free to express its natural significations without major obstruction"}.'
    )

    # Paragraph 4: D9 and timing
    detail_p4 = (
        f'The Navamsha (D9) chart is arguably the most important divisional chart for marriage analysis, revealing '
        f'the deeper karmic dimension of your partnerships. Your D9 ascendant in {d9_asc} indicates that the soul-level '
        f'experience of your marriage '
        f'{"is one of mutual growth, adventure, and shared ambition" if d9_asc in ("Aries", "Sagittarius", "Leo") else ""}'
        f'{"is grounded in comfort, loyalty, and sensory enjoyment" if d9_asc in ("Taurus", "Cancer", "Pisces") else ""}'
        f'{"is intellectual, communicative, and built on shared ideas" if d9_asc in ("Gemini", "Virgo", "Aquarius") else ""}'
        f'{"is intense, transformative, and karmically charged" if d9_asc in ("Scorpio", "Capricorn") else ""}'
        f'{"is balanced, aesthetic, and oriented toward harmony" if d9_asc == "Libra" else ""}. '
        f'The dasha periods identified as favorable for marriage should be treated as windows of opportunity: '
        f'if marriage is being considered, these periods offer the strongest planetary support for a lasting bond. '
        f'{"Timing factors suggest patience may be needed, but delayed marriages under these configurations often prove more durable." if timing_factors else ""}'
    )

    detailed_reading = f'{detail_p1}\n\n{detail_p2}\n\n{detail_p3}\n\n{detail_p4}'

    return {
        'title': 'Marriage & Relationships',
        'seventh_house_sign': h7['sign'],
        'seventh_lord': l7,
        'seventh_lord_house': l7_d['house'],
        'seventh_lord_dignity': l7_d['dignity'],
        'venus_sign': venus['sign'],
        'venus_house': venus['house'],
        'venus_dignity': venus['dignity'],
        'occupants': occ_7,
        'd9_ascendant': d9_asc,
        'spouse_traits': spouse_traits.get(h7['sign'], 'Standard traits.'),
        'timing_factors': timing_factors,
        'quality_factors': quality_factors,
        'marriage_periods': marriage_periods[:3],
        'summary': summary,
        'detailed_reading': detailed_reading,
    }


def predict_wealth(chart):
    """Wealth predictions from 2nd, 11th houses, Dhana yogas, and dasha timing."""
    h2 = chart['houses'][2]
    h11 = chart['houses'][11]
    l2 = h2['lord']
    l11 = h11['lord']
    l2_d = chart['planets'][l2]
    l11_d = chart['planets'][l11]

    # Wealth strength
    factors = []
    if l2_d['dignity'] in ('Exalted', 'Own Sign'):
        factors.append(f'2nd lord {l2} strong ({l2_d["dignity"]}) — solid wealth foundation')
    if l11_d['dignity'] in ('Exalted', 'Own Sign'):
        factors.append(f'11th lord {l11} strong ({l11_d["dignity"]}) — consistent income gains')
    if l2_d['dignity'] in ('Debilitated', 'Enemy'):
        factors.append(f'2nd lord {l2} weak ({l2_d["dignity"]}) — wealth accumulation needs effort')
    if l11_d['dignity'] in ('Debilitated', 'Enemy'):
        factors.append(f'11th lord {l11} weak ({l11_d["dignity"]}) — income growth faces blocks')

    # Jupiter's influence on wealth houses
    jup = chart['planets']['Jupiter']
    if jup['house'] in (2, 5, 9, 11):
        factors.append(f'Jupiter in house {jup["house"]} — natural wealth protector and multiplier')
    if _aspects_planet(chart, 'Jupiter', l2):
        factors.append(f'Jupiter aspects 2nd lord — wealth protected by divine grace')

    # Best wealth periods
    wealth_periods = []
    for d in chart['dashas']['dashas']:
        lord = d['lord']
        lord_h = _house(chart, lord)
        if lord_h in (2, 11) or lord == l2 or lord == l11 or lord == 'Jupiter':
            quality = 'growth'
            if chart['planets'][lord]['dignity'] in ('Debilitated', 'Enemy'):
                quality = 'challenging'
            wealth_periods.append({
                'period': f'{lord} Mahadasha',
                'start': d['start'].strftime('%b %Y'),
                'end': d['end'].strftime('%b %Y'),
                'quality': quality,
            })

    # Build narrative summary
    jup_text = ''
    if jup['house'] in (2, 5, 9, 11):
        jup_text = (
            f' Jupiter, the great benefic and natural wealth-multiplier, sits in house {jup["house"]}, '
            f'providing a layer of divine protection over your financial life that often manifests as '
            f'unexpected opportunities arriving precisely when needed.'
        )

    strength_text = ''
    if any('strong' in f.lower() for f in factors):
        strength_text = (
            ' The structural indicators for wealth in your chart are solid, suggesting that consistent effort '
            'and smart financial planning will yield compounding returns over time.'
        )
    challenge_text = ''
    if any('weak' in f.lower() for f in factors):
        challenge_text = (
            ' Some financial indicators require extra attention: wealth accumulation may be slower in early '
            'years, but the chart suggests that persistence and disciplined saving will overcome initial obstacles.'
        )

    summary = (
        f'Your financial story is told through two key houses: the 2nd house in {h2["sign"]} (lord {l2} in '
        f'house {l2_d["house"]}, {l2_d["dignity"]}), which governs accumulated wealth, family assets, and your '
        f'relationship with money as stored value, and the 11th house in {h11["sign"]} (lord {l11} in house '
        f'{l11_d["house"]}, {l11_d["dignity"]}), which governs income flow, gains from profession, and the '
        f'fulfillment of material desires. The interplay between these two lords determines whether money '
        f'comes easily and stays, comes and leaves, or arrives late but in abundance.{jup_text}'
        f'{strength_text}{challenge_text}'
    )

    # Build detailed multi-paragraph reading
    # Paragraph 1: 2nd house - stored wealth
    detail_p1 = (
        f'The 2nd house in {h2["sign"]} with its lord {l2} placed in house {l2_d["house"]} ({l2_d["dignity"]}) '
        f'reveals the nature of your accumulated wealth and your instinctive relationship with money. '
        f'{h2["sign"]} energy in the 2nd house means your approach to savings and assets carries the qualities '
        f'of this sign: '
        f'{"aggressive accumulation and entrepreneurial risk-taking" if h2["sign"] in ("Aries", "Scorpio") else ""}'
        f'{"patient building, sensory investment, and preference for tangible assets like property and gold" if h2["sign"] in ("Taurus", "Cancer") else ""}'
        f'{"multiple income streams, intellectual property, and money through communication" if h2["sign"] in ("Gemini", "Virgo") else ""}'
        f'{"generous spending, investment in status symbols, and wealth through authority" if h2["sign"] in ("Leo", "Sagittarius") else ""}'
        f'{"balanced budgeting, partnership-based wealth, and money through beauty or diplomacy" if h2["sign"] in ("Libra", "Pisces") else ""}'
        f'{"structured savings, long-term investments, and wealth through discipline and institutions" if h2["sign"] in ("Capricorn", "Aquarius") else ""}. '
        f'The {l2_d["dignity"].lower()} dignity of {l2} '
        f'{"strongly supports wealth accumulation" if l2_d["dignity"] in ("Exalted", "Own Sign") else "requires deliberate financial discipline to maximize returns"}. '
        f'Family wealth and inherited financial patterns are also indicated by this house, and your '
        f'relationship with money was likely shaped significantly by family attitudes in early childhood.'
    )

    # Paragraph 2: 11th house - income and gains
    detail_p2 = (
        f'The 11th house in {h11["sign"]} with lord {l11} in house {l11_d["house"]} ({l11_d["dignity"]}) reveals '
        f'the nature of your income flow and the channels through which gains enter your life. This is the house '
        f'of fulfilled desires, professional earnings, and the network of people who contribute to your financial '
        f'growth. {h11["sign"]} in the 11th suggests that your income comes through channels related to this sign\'s '
        f'energy, and the {l11_d["dignity"].lower()} state of {l11} determines how freely those channels flow. '
        f'{"The 11th lord in a kendra provides a stable income foundation that supports long-term financial planning." if _is_kendra(l11_d["house"]) else ""}'
        f'{"The 11th lord in a trikona connects your income to your life purpose and past-life merit, often bringing gains through ethical or dharmic work." if _is_trikona(l11_d["house"]) else ""}'
        f'{"The 11th lord in a dusthana means income may come through challenging circumstances such as debt management, insurance, foreign sources, or service industries." if _is_dusthana(l11_d["house"]) else ""}'
        f' The relationship between the 2nd and 11th lords is critical: when both are well-placed, wealth not '
        f'only arrives but is retained and grows. When one is strong and the other weak, either income is strong '
        f'but savings leak, or savings accumulate but income flow is restricted.'
    )

    # Paragraph 3: Jupiter and Dhana yoga potential
    detail_p3 = (
        f'Jupiter\'s placement in house {jup["house"]} in {jup["sign"]} ({jup["dignity"]}) has a direct bearing '
        f'on your wealth potential, because Jupiter is the natural significator of prosperity, expansion, and '
        f'divine grace in financial matters. '
        f'{"Jupiter in a wealth house (2, 5, 9, or 11) is one of the strongest indicators of financial abundance in Vedic astrology, often protecting the native from severe poverty even during difficult periods." if jup["house"] in (2, 5, 9, 11) else ""}'
        f'{"Jupiter aspecting wealth houses brings indirect financial protection and ensures that opportunities for growth appear at critical moments." if _aspects_planet(chart, "Jupiter", l2) or _aspects_planet(chart, "Jupiter", l11) else ""}'
        f' Additionally, the presence of Dhana (wealth) yogas in the chart, formed when lords of wealth houses '
        f'connect with lords of income houses through conjunction, aspect, or exchange, amplifies the overall '
        f'wealth potential. The dasha periods of planets connected to the 2nd and 11th houses are the windows '
        f'during which major financial events, both gains and restructurings, are most likely to occur.'
    )

    # Paragraph 4: Timing and advice
    detail_p4 = (
        f'Financial timing in Vedic astrology is primarily governed by the Vimshottari dasha system. The periods '
        f'flagged as wealth-relevant in this analysis activate the 2nd house, 11th house, or their lords, creating '
        f'windows for salary increases, business expansion, inheritance, investments, or property acquisition. '
        f'Periods marked as challenging are not necessarily periods of loss, but periods where financial decisions '
        f'carry higher stakes and require more careful analysis. The general principle for this chart is: '
        f'{"build during strong periods and consolidate during weak ones, trusting that the overall wealth trajectory is upward" if any("strong" in f.lower() for f in factors) else "maintain strict financial discipline during all periods, use challenging windows for debt reduction and skill-building, and trust that wealth will arrive with time"}. '
        f'Real estate, gold, and fixed deposits tend to work better for charts where the 2nd lord is in earth '
        f'or water signs, while equities and intellectual property suit charts where the 2nd lord is in air '
        f'or fire signs.'
    )

    detailed_reading = f'{detail_p1}\n\n{detail_p2}\n\n{detail_p3}\n\n{detail_p4}'

    return {
        'title': 'Wealth & Finances',
        'second_house_sign': h2['sign'],
        'second_lord': l2,
        'eleventh_house_sign': h11['sign'],
        'eleventh_lord': l11,
        'factors': factors,
        'wealth_periods': wealth_periods[:4],
        'summary': summary,
        'detailed_reading': detailed_reading,
    }


def predict_health(chart):
    """Health predictions from ascendant, 6th house, weak planets, and dasha vulnerabilities."""
    asc_sign = chart['ascendant']['sign']
    h6 = chart['houses'][6]
    l6 = h6['lord']
    l6_d = chart['planets'][l6]

    # Body areas from ascendant
    primary_areas = _SIGN_BODY_PARTS.get(asc_sign, 'general health')

    # 6th house indicates disease type
    disease_areas = _SIGN_BODY_PARTS.get(h6['sign'], 'general')

    # Weak planets create health vulnerabilities
    vulnerabilities = []
    planet_body = {
        'Sun': 'heart, eyes, bones, vitality',
        'Moon': 'mind, fluids, stomach, breasts, sleep',
        'Mars': 'blood, muscles, accidents, surgery, inflammation',
        'Mercury': 'skin, nervous system, speech, lungs',
        'Jupiter': 'liver, fat, diabetes, ears, growth',
        'Venus': 'kidneys, reproductive system, diabetes, hormones',
        'Saturn': 'joints, knees, chronic pain, teeth, aging',
        'Rahu': 'mysterious diseases, allergies, phobias, addictions',
        'Ketu': 'accidents, surgeries, spiritual crises, unexplained ailments',
    }

    for p in PLANETS:
        pd = chart['planets'][p]
        if pd['dignity'] in ('Debilitated', 'Enemy') or pd.get('is_combust', False):
            vulnerabilities.append({
                'planet': p,
                'issue': f'{p} weak ({pd["dignity"]}{"" if not pd.get("is_combust") else ", combust"}) — watch {planet_body.get(p, "related areas")}',
            })

    # Planets in 6th house
    occ_6 = h6['occupants']
    health_notes = []
    for p in occ_6:
        if p in NATURAL_MALEFICS:
            health_notes.append(f'{p} in 6th — good for defeating disease (malefic in upachaya)')
        elif p in NATURAL_BENEFICS:
            health_notes.append(f'{p} in 6th — health challenges related to {planet_body.get(p, "this planet")}')

    # Vulnerable dasha periods
    vulnerable_periods = []
    for d in chart['dashas']['dashas']:
        lord = d['lord']
        lord_d = chart['planets'][lord]
        if lord_d['dignity'] in ('Debilitated', 'Enemy') or _house(chart, lord) in (6, 8, 12):
            vulnerable_periods.append({
                'period': f'{lord} Mahadasha',
                'start': d['start'].strftime('%b %Y'),
                'end': d['end'].strftime('%b %Y'),
                'concern': f'{lord} activates health sensitivity — regular check-ups advised',
            })

    # Build narrative summary
    vuln_text = ''
    if vulnerabilities:
        vuln_planets = ', '.join(v['planet'] for v in vulnerabilities)
        vuln_text = (
            f' The planets {vuln_planets} are under stress in this chart, creating specific health '
            f'vulnerabilities that benefit from proactive attention rather than reactive treatment.'
        )

    notes_text = ''
    if health_notes:
        notes_text = ' ' + ' '.join(health_notes) + '.'

    summary = (
        f'Your ascendant in {asc_sign} establishes the foundational constitution of your body, linking your '
        f'primary health identity to {primary_areas}. The 6th house in {h6["sign"]} with its lord {l6} in house '
        f'{l6_d["house"]} ({l6_d["dignity"]}) reveals the nature of diseases and health challenges most likely '
        f'to manifest over your lifetime, particularly in areas related to {disease_areas}. '
        f'{"The 6th lord in a strong position provides good disease-fighting ability and recovery power." if l6_d["dignity"] in ("Exalted", "Own Sign") else ""}'
        f'{"The 6th lord under stress means health management requires consistent daily attention." if l6_d["dignity"] in ("Debilitated", "Enemy") else ""}'
        f'{vuln_text}{notes_text}'
        f' Understanding these patterns allows you to take preventive measures during vulnerable dasha periods '
        f'rather than waiting for symptoms to appear.'
    )

    # Build detailed multi-paragraph reading
    # Paragraph 1: Constitution from ascendant
    detail_p1 = (
        f'Your ascendant in {asc_sign} is the single most important factor in determining your overall physical '
        f'constitution, vitality, and the body\'s natural strengths and weaknesses. {asc_sign} rising gives a '
        f'constitution that is particularly connected to {primary_areas}, meaning these areas are both your '
        f'strength zones (when the ascendant lord is well-placed) and your vulnerability zones (when under '
        f'transit or dasha pressure). The general health approach that works best for {asc_sign} ascendant is: '
        f'{"high-intensity exercise, martial arts, and heat-reducing diet to manage the fire element" if asc_sign in ("Aries", "Leo", "Sagittarius") else ""}'
        f'{"grounding routines, consistent meal timing, oil massage, and activities that build rather than deplete" if asc_sign in ("Taurus", "Virgo", "Capricorn") else ""}'
        f'{"breathing exercises, nervous system regulation, adequate sleep, and mental health maintenance" if asc_sign in ("Gemini", "Libra", "Aquarius") else ""}'
        f'{"water-based therapies, emotional processing, digestive care, and protection from damp or cold environments" if asc_sign in ("Cancer", "Scorpio", "Pisces") else ""}. '
        f'The ascendant lord\'s condition in the chart determines the overall vitality level: a strong ascendant '
        f'lord provides robust recovery even from serious illness, while a weak one requires more preventive care.'
    )

    # Paragraph 2: 6th house disease patterns
    detail_p2 = (
        f'The 6th house in {h6["sign"]} with lord {l6} in house {l6_d["house"]} ({l6_d["dignity"]}) reveals the '
        f'specific disease patterns most likely to affect you. The 6th house is the house of disease, enemies, '
        f'and obstacles, and its sign indicates the body systems that are most susceptible under stress. '
        f'{h6["sign"]} in the 6th points to vulnerabilities in {disease_areas}. '
        f'{"The 6th lord in a kendra means health challenges are visible and manageable through conventional medicine." if _is_kendra(l6_d["house"]) else ""}'
        f'{"The 6th lord in a trikona suggests that health challenges ultimately serve spiritual or personal growth." if _is_trikona(l6_d["house"]) else ""}'
        f'{"The 6th lord in a dusthana (6, 8, or 12) is actually favorable for health, as the lord of disease in a difficult house creates a Viparita Raja Yoga that neutralizes health enemies." if _is_dusthana(l6_d["house"]) else ""}'
        f' Planets occupying the 6th house also shape the health narrative: '
        f'{"malefics here actually strengthen disease-fighting ability (upachaya house principle)" if any(p in NATURAL_MALEFICS for p in occ_6) else ""}'
        f'{"benefics here can make you vulnerable to the diseases they signify, though they also provide healing ability" if any(p in NATURAL_BENEFICS for p in occ_6) else ""}'
        f'{"an empty 6th house means health is primarily determined by the lord\'s placement rather than direct occupation" if not occ_6 else ""}.'
    )

    # Paragraph 3: Planetary vulnerabilities
    vuln_details = []
    for v in vulnerabilities:
        p = v['planet']
        pd = chart['planets'][p]
        body_area = planet_body.get(p, 'related areas')
        vuln_details.append(
            f'{p} in {pd["sign"]} ({pd["dignity"]}{"" if not pd.get("is_combust") else ", combust"}) creates '
            f'sensitivity in {body_area}'
        )
    detail_p3 = ''
    if vuln_details:
        detail_p3 = (
            f'Specific planetary vulnerabilities in this chart point to health areas that require ongoing attention. '
            + '. '.join(vuln_details) + '. '
            f'These vulnerabilities are not predictions of inevitable disease but rather indicators of where the '
            f'body is most likely to express stress. Ayurvedic principles suggest strengthening these planets '
            f'through their associated colors, mantras, gemstones (with proper consultation), and dietary '
            f'adjustments. The goal is to support weak planets before symptoms appear, turning potential '
            f'vulnerabilities into awareness-driven prevention.'
        )
    else:
        detail_p3 = (
            'No planets are in significantly weakened states in this chart, which is a positive indicator for '
            'overall vitality and disease resistance. This does not mean health can be taken for granted, but it '
            'does mean the body has strong innate recovery mechanisms. Maintain these through consistent daily '
            'routines, seasonal adjustments, and attention to the health indicators during vulnerable dasha periods.'
        )

    # Paragraph 4: Timing and prevention
    detail_p4 = (
        f'Health timing in Vedic astrology follows dasha activations. Periods ruled by debilitated planets, '
        f'planets in dusthana houses (6, 8, 12), or planets that signify the vulnerable body areas identified '
        f'above are the windows when preventive action is most valuable. The vulnerable periods flagged in this '
        f'analysis are not predictions of illness but rather periods when the body\'s resistance is lower and '
        f'pre-existing tendencies are more likely to manifest. During these periods, increase rest, simplify diet, '
        f'reduce stress, and schedule medical check-ups proactively. Between vulnerable periods, focus on building '
        f'health reserves through exercise, proper nutrition, and mental wellness practices. The overall trajectory '
        f'of health in this chart is '
        f'{"strong, with good recovery power and natural vitality that supports an active lifestyle well into old age" if len(vulnerabilities) <= 1 else "manageable with attention, where the key is consistency in daily health routines rather than dramatic interventions"}.'
    )

    detailed_reading = f'{detail_p1}\n\n{detail_p2}\n\n{detail_p3}\n\n{detail_p4}'

    return {
        'title': 'Health & Wellness',
        'ascendant_sign': asc_sign,
        'primary_body_areas': primary_areas,
        'sixth_house_sign': h6['sign'],
        'disease_areas': disease_areas,
        'vulnerabilities': vulnerabilities,
        'health_notes': health_notes,
        'vulnerable_periods': vulnerable_periods[:3],
        'summary': summary,
        'detailed_reading': detailed_reading,
    }


def predict_spiritual(chart):
    """Spiritual growth predictions from Ketu, 12th house, 5th house, and Jupiter."""
    ketu = chart['planets']['Ketu']
    h12 = chart['houses'][12]
    h5 = chart['houses'][5]
    jupiter = chart['planets']['Jupiter']

    # Ketu placement — spiritual direction
    ketu_spiritual = {
        1: 'Natural spiritual seeker. Past-life spiritual identity. Meditation comes naturally.',
        2: 'Detachment from material accumulation. Spiritual growth through fasting and speech control.',
        3: 'Spiritual courage. Writing or speaking about mystical topics. Communication as sadhana.',
        4: 'Inner peace through renunciation of comfort. Ashram life resonates. Mother\'s spiritual influence.',
        5: 'Mantra siddhi potential. Past-life spiritual merit activates. Children may guide you spiritually.',
        6: 'Healing through spiritual practice. Defeats inner enemies through meditation. Service as devotion.',
        7: 'Spiritual partnerships. Marriage as karmic laboratory. Partner aids spiritual growth.',
        8: 'Deep occult/tantric abilities. Kundalini awakening potential. Transformation through meditation.',
        9: 'Already walked the dharma path. Natural guru potential. Philosophy internalized from past lives.',
        10: 'Karma yoga — spiritual growth through work. Detached professional. Public spiritual role.',
        11: 'Gains through spiritual network. Satsang groups. Desires dissolve into spiritual fulfillment.',
        12: 'Highest moksha potential. Liberation-oriented soul. Meditation, dreams, and isolation as path.',
    }

    # Best sadhana periods
    sadhana_periods = []
    for d in chart['dashas']['dashas']:
        lord = d['lord']
        if lord in ('Jupiter', 'Ketu') or _house(chart, lord) in (5, 9, 12):
            sadhana_periods.append({
                'period': f'{lord} Mahadasha',
                'start': d['start'].strftime('%b %Y'),
                'end': d['end'].strftime('%b %Y'),
                'theme': f'{lord} activates spiritual houses — deepening of practice',
            })

    # Build narrative summary
    l12 = h12['lord']
    l12_d = chart['planets'][l12]
    l5 = h5['lord']

    jup_quality = ''
    if jupiter['dignity'] in ('Exalted', 'Own Sign'):
        jup_quality = (
            ' Jupiter, the guru planet, is strong in your chart, blessing you with natural wisdom, '
            'an instinct for dharma, and the ability to attract genuine spiritual teachers when the time is right.'
        )
    elif jupiter['dignity'] in ('Debilitated', 'Enemy'):
        jup_quality = (
            ' Jupiter, the planet of wisdom and dharma, is under pressure in your chart, which means spiritual '
            'understanding comes through questioning, doubt, and personal experience rather than through inherited '
            'tradition or easy faith.'
        )

    summary = (
        f'Your spiritual direction is primarily guided by Ketu in {ketu["sign"]} (house {ketu["house"]}), the '
        f'planet of liberation and past-life spiritual attainment: {ketu_spiritual.get(ketu["house"], "")} '
        f'The 12th house in {h12["sign"]} with lord {l12} governs the domain of moksha, surrender, and the '
        f'dissolution of ego, revealing the conditions under which you naturally let go of worldly attachment. '
        f'The 5th house in {h5["sign"]} (lord {l5}) adds the dimension of mantra, meditation practice, and '
        f'past-life spiritual merit that activates in this lifetime.{jup_quality}'
        f' The sadhana periods identified below are windows when spiritual practice yields the deepest results '
        f'and inner transformation accelerates.'
    )

    # Build detailed multi-paragraph reading
    # Paragraph 1: Ketu - spiritual direction
    detail_p1 = (
        f'Ketu in {ketu["sign"]} in the {ketu["house"]}th house is the primary indicator of your spiritual '
        f'orientation and the gifts you carry from past-life spiritual practice. Unlike other planets that '
        f'push you toward worldly achievement, Ketu pulls you inward, toward what you have already mastered '
        f'at the soul level. {ketu_spiritual.get(ketu["house"], "")} The sign of Ketu, {ketu["sign"]}, adds a '
        f'specific flavor to this spiritual imprint: '
        f'{"fiery, action-oriented spirituality that expresses through service and courage" if ketu["sign"] in ("Aries", "Leo", "Sagittarius") else ""}'
        f'{"grounded, embodied spirituality that expresses through nature, ritual, and physical discipline" if ketu["sign"] in ("Taurus", "Virgo", "Capricorn") else ""}'
        f'{"intellectual, inquiry-based spirituality that expresses through study, dialogue, and philosophical exploration" if ketu["sign"] in ("Gemini", "Libra", "Aquarius") else ""}'
        f'{"intuitive, mystical spirituality that expresses through dreams, devotion, meditation, and emotional surrender" if ketu["sign"] in ("Cancer", "Scorpio", "Pisces") else ""}. '
        f'In practical terms, this placement suggests that your most natural form of spiritual practice involves '
        f'the themes of house {ketu["house"]}, and that the spiritual breakthroughs in your life will come through '
        f'situations connected to this house\'s significations.'
    )

    # Paragraph 2: 12th house - moksha and surrender
    detail_p2 = (
        f'The 12th house in {h12["sign"]} with its lord {l12} in house {l12_d["house"]} ({l12_d["dignity"]}) '
        f'governs the final stage of spiritual development: the dissolution of the ego and the capacity for '
        f'genuine surrender. This house reveals how you let go, what you must release to achieve liberation, '
        f'and the circumstances through which transcendence naturally occurs in your life. {h12["sign"]} in the '
        f'12th colors your moksha path with the qualities of this sign: '
        f'{"fire signs here suggest liberation through passionate devotion, pilgrimage, or selfless action" if h12["sign"] in ("Aries", "Leo", "Sagittarius") else ""}'
        f'{"earth signs here suggest liberation through service, discipline, and the sanctification of daily work" if h12["sign"] in ("Taurus", "Virgo", "Capricorn") else ""}'
        f'{"air signs here suggest liberation through knowledge, breath work, and the dissolution of intellectual pride" if h12["sign"] in ("Gemini", "Libra", "Aquarius") else ""}'
        f'{"water signs here suggest liberation through bhakti (devotion), meditation near water, dreams, and emotional surrender" if h12["sign"] in ("Cancer", "Scorpio", "Pisces") else ""}. '
        f'The condition of {l12} ({l12_d["dignity"]}) determines how accessible the 12th house experience is: '
        f'{"strong 12th lord makes spiritual withdrawal and foreign spiritual experiences come naturally" if l12_d["dignity"] in ("Exalted", "Own Sign") else "the 12th lord under stress means liberation must be earned through sustained effort and the conscious processing of loss"}.'
    )

    # Paragraph 3: Jupiter and 5th house - wisdom and practice
    detail_p3 = (
        f'Jupiter in {jupiter["sign"]} in the {jupiter["house"]}th house ({jupiter["dignity"]}) is your wisdom '
        f'guide, the planet that connects you to teachers, sacred texts, and the living tradition of dharma. '
        f'{"Jupiter in a strong dignity provides a natural moral compass and the ability to recognize truth when you encounter it." if jupiter["dignity"] in ("Exalted", "Own Sign", "Moolatrikona") else ""}'
        f'{"Jupiter in a weakened state means wisdom comes through personal struggle and the hard-won realization that prescribed paths do not always fit." if jupiter["dignity"] in ("Debilitated", "Enemy") else ""}'
        f' The 5th house in {h5["sign"]} adds the dimension of purva punya (past-life merit) and the capacity '
        f'for mantra siddhi, the power that comes from sustained repetition of sacred sounds. '
        f'{"Benefics connected to the 5th house amplify past-life spiritual credit that activates in this lifetime." if any(p in NATURAL_BENEFICS for p in h5["occupants"]) else ""}'
        f' Together, Jupiter and the 5th house reveal your natural aptitude for formal spiritual practice: '
        f'meditation, mantra, puja, study of sacred texts, and the development of intuitive wisdom that '
        f'goes beyond intellectual understanding.'
    )

    # Paragraph 4: Timing and practice recommendations
    detail_p4 = (
        f'Spiritual growth follows its own timing in Vedic astrology, governed by the dasha periods of Jupiter, '
        f'Ketu, and planets connected to the 5th, 9th, and 12th houses. The sadhana periods identified in this '
        f'analysis are windows when the inner landscape becomes unusually receptive to spiritual input: meditation '
        f'goes deeper, teachers appear, and life circumstances naturally turn your attention inward. During these '
        f'periods, increase your practice, seek guidance from qualified teachers, and allow yourself to withdraw '
        f'from worldly ambition without guilt. Outside these windows, maintain a baseline daily practice that keeps '
        f'the channel open. For this particular chart configuration, the most effective spiritual practices are '
        f'likely to involve '
        f'{"silent meditation and renunciation-based disciplines" if ketu["house"] in (8, 12) else ""}'
        f'{"devotional singing, temple worship, and community-based spirituality" if ketu["house"] in (1, 4, 7) else ""}'
        f'{"mantra repetition, study of scripture, and teaching as a path to realization" if ketu["house"] in (2, 5, 9) else ""}'
        f'{"karma yoga and selfless service as the primary vehicle for spiritual progress" if ketu["house"] in (3, 6, 10, 11) else ""}. '
        f'The ultimate spiritual message of this chart is that liberation is not a destination but a quality of '
        f'attention that you bring to every area of life touched by these planetary configurations.'
    )

    detailed_reading = f'{detail_p1}\n\n{detail_p2}\n\n{detail_p3}\n\n{detail_p4}'

    return {
        'title': 'Spiritual Growth',
        'ketu_sign': ketu['sign'],
        'ketu_house': ketu['house'],
        'ketu_reading': ketu_spiritual.get(ketu['house'], 'Standard spiritual path.'),
        'twelfth_house_sign': h12['sign'],
        'twelfth_lord': h12['lord'],
        'jupiter_sign': jupiter['sign'],
        'jupiter_house': jupiter['house'],
        'jupiter_dignity': jupiter['dignity'],
        'sadhana_periods': sadhana_periods[:3],
        'summary': summary,
        'detailed_reading': detailed_reading,
    }


def get_life_predictions(chart):
    """Master function for all life area predictions."""
    return {
        'career': predict_career(chart),
        'marriage': predict_marriage(chart),
        'wealth': predict_wealth(chart),
        'health': predict_health(chart),
        'spiritual': predict_spiritual(chart),
    }


# ════════════════════════════════════════════════════════════════
# SECTION 5: YEAR-BY-YEAR FORECAST (NEXT 10 YEARS)
# ════════════════════════════════════════════════════════════════

def get_yearly_forecast(chart, num_years=10):
    """Generate year-by-year forecast based on dasha/antardasha activations."""
    dashas = chart['dashas']
    planets = chart['planets']
    now = datetime.now(dashas['dashas'][0]['start'].tzinfo)
    forecasts = []

    for year_offset in range(num_years):
        year_start = now.replace(year=now.year + year_offset, month=1, day=1,
                                 hour=0, minute=0, second=0, microsecond=0)
        year_end = now.replace(year=now.year + year_offset, month=12, day=31,
                               hour=23, minute=59, second=59, microsecond=0)
        year_mid = now.replace(year=now.year + year_offset, month=7, day=1)

        # Find active dasha/antardasha at mid-year
        active_maha = None
        active_antar = None
        for d in dashas['dashas']:
            if d['start'] <= year_mid < d['end']:
                active_maha = d
                for ad in d['antardashas']:
                    if ad['start'] <= year_mid < ad['end']:
                        active_antar = ad
                        break
                break

        if not active_maha:
            continue

        maha_lord = active_maha['lord']
        antar_lord = active_antar['lord'] if active_antar else maha_lord

        mp = planets[maha_lord]
        ap = planets[antar_lord]

        # Determine themes from activated houses
        active_houses = sorted(set([mp['house'], ap['house']]))
        themes = []
        for h in active_houses:
            sig = HOUSE_SIGNIFICATIONS.get(h, '')
            if sig:
                themes.append(sig.split(',')[0].strip())

        # Quality assessment
        is_friend = antar_lord in NATURAL_FRIENDS.get(maha_lord, [])
        is_enemy = antar_lord in NATURAL_ENEMIES.get(maha_lord, [])

        if is_friend:
            quality = 'favorable'
            quality_text = f'{maha_lord} and {antar_lord} are natural friends — harmonious energy, doors open.'
        elif is_enemy:
            quality = 'challenging'
            quality_text = f'{maha_lord} and {antar_lord} are natural enemies — tension drives growth through difficulty.'
        else:
            quality = 'mixed'
            quality_text = f'{maha_lord} and {antar_lord} have neutral relationship — results depend on effort.'

        # Dignity-based nuance
        caution_areas = []
        if ap['dignity'] in ('Debilitated', 'Enemy'):
            caution_areas.append(f'{antar_lord} is weak ({ap["dignity"]}) — avoid overcommitting in {KARAKAS.get(antar_lord, "").split(",")[0].strip().lower()} matters')
        if mp['dignity'] in ('Debilitated', 'Enemy'):
            caution_areas.append(f'{maha_lord} is weak — overall period requires patience')
        if ap.get('is_combust'):
            caution_areas.append(f'{antar_lord} combust — talents may go unrecognized this year')

        # All antardashas active during this year
        year_antardashas = []
        for d in dashas['dashas']:
            for ad in d['antardashas']:
                if ad['end'] >= year_start and ad['start'] <= year_end:
                    year_antardashas.append({
                        'maha': d['lord'],
                        'antar': ad['lord'],
                        'start': max(ad['start'], year_start).strftime('%b'),
                        'end': min(ad['end'], year_end).strftime('%b'),
                    })

        # Build richer yearly summary
        # Determine life areas from house significations
        life_areas = []
        for h in active_houses:
            sig = HOUSE_SIGNIFICATIONS.get(h, '')
            if sig:
                # Take first two significations for richer description
                parts = [s.strip() for s in sig.split(',')]
                life_areas.extend(parts[:2])

        # Energy quality description
        energy_desc = ''
        if quality == 'favorable':
            energy_desc = (
                f'The energy quality of this year feels expansive and cooperative. Doors that were previously '
                f'closed begin to open, and efforts you put in during earlier years start yielding visible results. '
                f'Relationships with authority figures and mentors tend to be supportive.'
            )
        elif quality == 'challenging':
            energy_desc = (
                f'The energy quality of this year feels like friction that drives growth. Expect tension between '
                f'competing priorities, and be prepared for situations where patience and strategy matter more '
                f'than force. The challenges are not random; they are precisely calibrated to strengthen the areas '
                f'where you have been avoiding discipline.'
            )
        else:
            energy_desc = (
                f'The energy quality of this year is mixed and depends heavily on your conscious effort. '
                f'There are windows of opportunity and windows of caution, and the difference between a '
                f'productive year and a frustrating one lies in your ability to read the timing and act '
                f'accordingly rather than forcing outcomes.'
            )

        # Specific advice
        advice = ''
        if any('weak' in c.lower() for c in caution_areas):
            advice = (
                f'Prioritize consolidation over expansion. Avoid major financial commitments or life-changing '
                f'decisions during the months when the weaker antardasha is active. Focus instead on skill-building, '
                f'health maintenance, and strengthening existing relationships.'
            )
        elif quality == 'favorable':
            advice = (
                f'This is a year to advance. Push for promotions, launch projects, initiate important conversations, '
                f'and make decisions you have been postponing. The planetary support is aligned with forward movement, '
                f'and delay would waste favorable conditions.'
            )
        else:
            advice = (
                f'Balance ambition with caution. Take calculated risks in the areas activated by houses '
                f'{", ".join(str(h) for h in active_houses)}, but maintain reserves for unexpected developments. '
                f'The most productive approach is sustained effort without overextension.'
            )

        # Priority areas
        priority = ', '.join(life_areas[:3]).lower() if life_areas else ', '.join(themes[:3]).lower()

        yearly_summary = (
            f'The {maha_lord}-{antar_lord} period governs this year, activating houses '
            f'{", ".join(str(h) for h in active_houses)} and bringing the themes of '
            f'{priority} into sharp focus. '
            f'{energy_desc} '
            f'{advice} '
            f'The top priority for this year is {priority.split(",")[0].strip()}, '
            f'as this is where the planetary energy is most concentrated and where your actions will have the '
            f'greatest long-term impact.'
        )

        forecasts.append({
            'year': now.year + year_offset,
            'maha_lord': maha_lord,
            'antar_lord': antar_lord,
            'maha_house': mp['house'],
            'antar_house': ap['house'],
            'quality': quality,
            'quality_text': quality_text,
            'themes': themes,
            'caution_areas': caution_areas,
            'antardashas_in_year': year_antardashas,
            'summary': yearly_summary,
        })

    return forecasts


# ════════════════════════════════════════════════════════════════
# SECTION 6: REMEDIES & PRECAUTIONS
# ════════════════════════════════════════════════════════════════

_PLANET_REMEDIES = {
    'Sun': {
        'gemstone': 'Ruby (Manik)',
        'metal': 'Gold or Copper',
        'color': 'Red, Orange, Saffron',
        'deity': 'Lord Surya (Sun God), Lord Ram',
        'mantra': 'Om Hraam Hreem Hraum Sah Suryaya Namah',
        'mantra_count': '7000 times in 40 days',
        'charity': 'Wheat, jaggery, copper, red cloth on Sundays',
        'fasting': 'Sunday (eat once, before sunset)',
        'direction': 'East',
        'day': 'Sunday',
        'food_favor': 'Wheat, jaggery, saffron, oranges',
        'food_avoid': 'Non-veg on Sundays',
    },
    'Moon': {
        'gemstone': 'Pearl (Moti)',
        'metal': 'Silver',
        'color': 'White, Cream, Silver',
        'deity': 'Lord Shiva, Goddess Parvati',
        'mantra': 'Om Shraam Shreem Shraum Sah Chandraya Namah',
        'mantra_count': '11000 times in 40 days',
        'charity': 'White rice, milk, white cloth, silver on Mondays',
        'fasting': 'Monday (milk and fruits only)',
        'direction': 'North-West',
        'day': 'Monday',
        'food_favor': 'Rice, milk, curd, coconut, white foods',
        'food_avoid': 'Stale food, leftover food on Mondays',
    },
    'Mars': {
        'gemstone': 'Red Coral (Moonga)',
        'metal': 'Copper',
        'color': 'Red, Scarlet, Maroon',
        'deity': 'Lord Hanuman, Lord Kartikeya',
        'mantra': 'Om Kraam Kreem Kraum Sah Bhaumaya Namah',
        'mantra_count': '10000 times in 40 days',
        'charity': 'Red lentils (masoor dal), jaggery, red cloth on Tuesdays',
        'fasting': 'Tuesday (avoid salt)',
        'direction': 'South',
        'day': 'Tuesday',
        'food_favor': 'Red lentils, jaggery, honey, beets',
        'food_avoid': 'Non-veg on Tuesdays, overly spicy food',
    },
    'Mercury': {
        'gemstone': 'Emerald (Panna)',
        'metal': 'Bronze',
        'color': 'Green',
        'deity': 'Lord Vishnu, Lord Ganesha',
        'mantra': 'Om Braam Breem Braum Sah Budhaya Namah',
        'mantra_count': '9000 times in 40 days',
        'charity': 'Green moong dal, green cloth, emerald on Wednesdays',
        'fasting': 'Wednesday (green vegetables only)',
        'direction': 'North',
        'day': 'Wednesday',
        'food_favor': 'Green vegetables, moong dal, green herbs',
        'food_avoid': 'Alcohol on Wednesdays',
    },
    'Jupiter': {
        'gemstone': 'Yellow Sapphire (Pukhraj)',
        'metal': 'Gold',
        'color': 'Yellow, Saffron',
        'deity': 'Lord Vishnu, Lord Brihaspati, Lord Dakshinamurthy',
        'mantra': 'Om Graam Greem Graum Sah Gurave Namah',
        'mantra_count': '19000 times in 40 days',
        'charity': 'Yellow items (turmeric, chana dal, banana), gold, yellow cloth on Thursdays',
        'fasting': 'Thursday (banana, chana dal, yellow foods)',
        'direction': 'North-East',
        'day': 'Thursday',
        'food_favor': 'Banana, turmeric, chana dal, ghee, saffron',
        'food_avoid': 'Non-veg on Thursdays, alcohol',
    },
    'Venus': {
        'gemstone': 'Diamond (Heera) or White Sapphire',
        'metal': 'Silver or Platinum',
        'color': 'White, Pink, Pastel shades',
        'deity': 'Goddess Lakshmi, Goddess Saraswati',
        'mantra': 'Om Draam Dreem Draum Sah Shukraya Namah',
        'mantra_count': '16000 times in 40 days',
        'charity': 'White rice, sugar, white cloth, perfume on Fridays',
        'fasting': 'Friday (white foods, sweets)',
        'direction': 'South-East',
        'day': 'Friday',
        'food_favor': 'Rice, sugar, milk, white foods, sweet dishes',
        'food_avoid': 'Sour foods on Fridays',
    },
    'Saturn': {
        'gemstone': 'Blue Sapphire (Neelam) — wear ONLY after trial period',
        'metal': 'Iron',
        'color': 'Black, Dark Blue, Navy',
        'deity': 'Lord Shani Dev, Lord Hanuman, Lord Bhairav',
        'mantra': 'Om Praam Preem Praum Sah Shanaischaraya Namah',
        'mantra_count': '23000 times in 40 days',
        'charity': 'Mustard oil, black sesame, iron, dark blue cloth, blankets on Saturdays',
        'fasting': 'Saturday (black urad dal, sesame)',
        'direction': 'West',
        'day': 'Saturday',
        'food_favor': 'Black urad dal, sesame, mustard oil',
        'food_avoid': 'Alcohol on Saturdays, non-veg',
    },
    'Rahu': {
        'gemstone': 'Hessonite Garnet (Gomed)',
        'metal': 'Lead or Mixed metals (Ashtadhatu)',
        'color': 'Smoky, Dark Brown, Denim Blue',
        'deity': 'Goddess Durga, Lord Bhairav',
        'mantra': 'Om Bhram Bhreem Bhraum Sah Rahave Namah',
        'mantra_count': '18000 times in 40 days',
        'charity': 'Coconut, mustard seeds, blankets, radish on Saturdays',
        'fasting': 'Saturday (same as Saturn)',
        'direction': 'South-West',
        'day': 'Saturday',
        'food_favor': 'Coconut, radish, mustard',
        'food_avoid': 'Alcohol, non-veg on Saturdays',
    },
    'Ketu': {
        'gemstone': 'Cat\'s Eye (Lehsunia)',
        'metal': 'Iron or mixed metals',
        'color': 'Grey, Brown, Earthy tones',
        'deity': 'Lord Ganesha, Lord Chitragupta',
        'mantra': 'Om Sraam Sreem Sraum Sah Ketave Namah',
        'mantra_count': '17000 times in 40 days',
        'charity': 'Blankets (grey/brown), sesame, seven grains mix on Tuesdays',
        'fasting': 'Tuesday (same as Mars)',
        'direction': 'Flag direction (wherever the flag of nearby temple points)',
        'day': 'Tuesday',
        'food_favor': 'Seven grain mix, sesame, root vegetables',
        'food_avoid': 'Non-veg on Tuesdays',
    },
}


def get_remedies(chart):
    """Get remedies only for planets that need strengthening."""
    remedies = []

    for planet in PLANETS:
        p = chart['planets'][planet]
        needs_remedy = False
        reasons = []

        if p['dignity'] in ('Debilitated', 'Enemy'):
            needs_remedy = True
            reasons.append(f'{p["dignity"]} in {p["sign"]}')
        if p.get('is_combust', False):
            needs_remedy = True
            reasons.append('combust (too close to Sun)')
        if _is_dusthana(p['house']) and planet in NATURAL_BENEFICS:
            needs_remedy = True
            reasons.append(f'benefic planet in dusthana house {p["house"]}')
        if p['dignity'] == 'Neutral' and _is_dusthana(p['house']):
            needs_remedy = True
            reasons.append(f'neutral dignity in difficult house {p["house"]}')

        if not needs_remedy:
            continue

        remedy_data = _PLANET_REMEDIES.get(planet, {})

        remedies.append({
            'planet': planet,
            'sign': p['sign'],
            'house': p['house'],
            'dignity': p['dignity'],
            'reasons': reasons,
            'gemstone': remedy_data.get('gemstone', ''),
            'metal': remedy_data.get('metal', ''),
            'color': remedy_data.get('color', ''),
            'deity': remedy_data.get('deity', ''),
            'mantra': remedy_data.get('mantra', ''),
            'mantra_count': remedy_data.get('mantra_count', ''),
            'charity': remedy_data.get('charity', ''),
            'fasting': remedy_data.get('fasting', ''),
        })

    return remedies


# ════════════════════════════════════════════════════════════════
# SECTION 7: HOUSE STRENGTHENING
# ════════════════════════════════════════════════════════════════

_HOUSE_REMEDIAL = {
    1: {
        'area': 'Self, Health, Personality',
        'strong_when': 'Lagna lord in kendra/trikona, benefics aspecting lagna, strong dignity',
        'remedies': [
            'Recite lagna lord\'s beej mantra daily at sunrise',
            'Wear gemstone of lagna lord (after consultation)',
            'Keep the body active — physical exercise strengthens 1st house',
            'Apply tilak on forehead every morning',
        ],
    },
    2: {
        'area': 'Wealth, Family, Speech',
        'strong_when': '2nd lord in own/exalted sign, benefics in 2nd, Jupiter aspect',
        'remedies': [
            'Recite Lakshmi mantra on Fridays',
            'Keep a money plant at home',
            'Practice truthful and sweet speech',
            'Donate food to the poor regularly',
            'Keep your safe/locker clean and organized',
        ],
    },
    3: {
        'area': 'Courage, Siblings, Communication',
        'strong_when': '3rd lord strong, Mars well-placed, benefics in 3rd',
        'remedies': [
            'Recite Hanuman Chalisa for courage',
            'Maintain good relations with siblings',
            'Practice writing or public speaking regularly',
            'Take short trips to refresh energy',
        ],
    },
    4: {
        'area': 'Mother, Home, Happiness, Vehicles',
        'strong_when': '4th lord strong, Moon well-placed, benefics in 4th',
        'remedies': [
            'Serve your mother with devotion',
            'Keep home clean and worship area maintained',
            'Plant a Tulsi (holy basil) at home',
            'Recite "Om Chandraya Namah" for inner peace',
            'Do not sell or give away ancestral property hastily',
        ],
    },
    5: {
        'area': 'Children, Intelligence, Past Merit',
        'strong_when': '5th lord strong, Jupiter well-placed, benefics in 5th',
        'remedies': [
            'Recite Santan Gopal mantra for children',
            'Worship Lord Ganesha on Wednesdays',
            'Teach or mentor children',
            'Engage in creative activities regularly',
            'Study sacred texts or philosophy',
        ],
    },
    6: {
        'area': 'Enemies, Disease, Debt',
        'strong_when': 'Malefics in 6th (good), 6th lord in dusthana, Mars strong',
        'remedies': [
            'Recite Durga Chalisa for enemy protection',
            'Maintain regular health check-ups',
            'Avoid taking unnecessary loans',
            'Serve animals, especially stray dogs',
            'Practice yoga and pranayama for disease prevention',
        ],
    },
    7: {
        'area': 'Marriage, Partnerships, Public',
        'strong_when': '7th lord strong, Venus well-placed, benefics in 7th',
        'remedies': [
            'Recite Parvati mantra for marital harmony',
            'Respect and appreciate your spouse daily',
            'Keep bedroom clean and well-decorated',
            'Offer white flowers at home temple on Fridays',
            'Avoid arguments after sunset',
        ],
    },
    8: {
        'area': 'Longevity, Transformation, Occult',
        'strong_when': '8th lord in own sign, Saturn strong, Jupiter aspect on 8th',
        'remedies': [
            'Recite Maha Mrityunjaya mantra for longevity',
            'Keep a Shiva Yantra at home',
            'Avoid risky adventures during weak dasha periods',
            'Practice meditation for psychological resilience',
            'Get health insurance and plan finances for emergencies',
        ],
    },
    9: {
        'area': 'Fortune, Father, Dharma, Guru',
        'strong_when': '9th lord strong, Jupiter well-placed, Sun strong',
        'remedies': [
            'Serve your father and guru with respect',
            'Visit pilgrimage sites regularly',
            'Donate to temples and educational institutions',
            'Recite Vishnu Sahasranama on Thursdays',
            'Practice daily gratitude for blessings received',
        ],
    },
    10: {
        'area': 'Career, Status, Authority',
        'strong_when': '10th lord in kendra, Saturn well-placed, Sun in 10th',
        'remedies': [
            'Recite Gayatri mantra before starting work',
            'Maintain integrity in profession — no shortcuts',
            'Serve seniors and authorities with respect',
            'Donate to charities related to your profession',
            'Work hard during favorable dasha periods',
        ],
    },
    11: {
        'area': 'Gains, Income, Desires, Networks',
        'strong_when': '11th lord strong, benefics in 11th, Jupiter aspect',
        'remedies': [
            'Recite Kubera mantra for wealth gains',
            'Maintain a wide social network',
            'Help elder siblings when they need support',
            'Donate a portion of gains to charity',
            'Invest during favorable dasha periods',
        ],
    },
    12: {
        'area': 'Losses, Foreign, Moksha, Expenses',
        'strong_when': '12th lord in 12th (Viparita), benefics in 12th, Jupiter aspect',
        'remedies': [
            'Recite "Om Namah Shivaya" before sleep',
            'Donate to hospitals, orphanages, ashrams',
            'Practice meditation before bed for better sleep',
            'Keep expenses in check — maintain a budget',
            'Visit a temple or do seva for spiritual merit',
        ],
    },
}


def get_house_strengthening(chart):
    """Assess each house's strength and provide remedial actions."""
    house_reports = []

    for h in range(1, 13):
        hd = chart['houses'][h]
        lord = hd['lord']
        lord_d = chart['planets'][lord] if lord not in ('Rahu', 'Ketu') else None
        occupants = hd['occupants']

        # Strength assessment
        strength_score = 50  # baseline
        strength_factors = []
        weakness_factors = []

        if lord_d:
            if lord_d['dignity'] in ('Exalted', 'Moolatrikona'):
                strength_score += 25
                strength_factors.append(f'Lord {lord} is {lord_d["dignity"]} — excellent')
            elif lord_d['dignity'] == 'Own Sign':
                strength_score += 20
                strength_factors.append(f'Lord {lord} in own sign — strong')
            elif lord_d['dignity'] == 'Friendly':
                strength_score += 10
                strength_factors.append(f'Lord {lord} in friendly sign — supportive')
            elif lord_d['dignity'] == 'Enemy':
                strength_score -= 15
                weakness_factors.append(f'Lord {lord} in enemy sign — weakened')
            elif lord_d['dignity'] == 'Debilitated':
                strength_score -= 25
                weakness_factors.append(f'Lord {lord} debilitated — significantly weak')

            if _is_kendra(lord_d['house']):
                strength_score += 10
                strength_factors.append(f'Lord in kendra (H{lord_d["house"]})')
            elif _is_dusthana(lord_d['house']):
                strength_score -= 10
                weakness_factors.append(f'Lord in dusthana (H{lord_d["house"]})')

        # Occupant effects
        for occ in occupants:
            occ_d = chart['planets'][occ]
            if occ in NATURAL_BENEFICS:
                strength_score += 10
                strength_factors.append(f'Benefic {occ} occupies this house')
            elif occ in NATURAL_MALEFICS and h not in (3, 6, 10, 11):
                strength_score -= 10
                weakness_factors.append(f'Malefic {occ} occupies this house')
            elif occ in NATURAL_MALEFICS and h in (3, 6, 10, 11):
                strength_score += 5
                strength_factors.append(f'Malefic {occ} in upachaya — grows stronger with time')

        # Aspects from benefics/malefics
        for p in PLANETS:
            if p in occupants:
                continue
            if _aspects_planet(chart, p, lord) if lord_d else False:
                pass  # already covered in planetary analysis

        strength_score = max(0, min(100, strength_score))

        if strength_score >= 70:
            assessment = 'Strong'
        elif strength_score >= 50:
            assessment = 'Moderate'
        elif strength_score >= 30:
            assessment = 'Weak'
        else:
            assessment = 'Very Weak'

        remedial_info = _HOUSE_REMEDIAL.get(h, {})

        house_reports.append({
            'house': h,
            'sign': hd['sign'],
            'lord': lord,
            'lord_house': hd['lord_house'],
            'occupants': occupants,
            'strength_score': strength_score,
            'assessment': assessment,
            'area': remedial_info.get('area', HOUSE_SIGNIFICATIONS.get(h, '')),
            'strength_factors': strength_factors,
            'weakness_factors': weakness_factors,
            'remedies': remedial_info.get('remedies', []),
        })

    return house_reports


# ════════════════════════════════════════════════════════════════
# SECTION 8: KARMIC LESSONS
# ════════════════════════════════════════════════════════════════

_RAHU_SIGN_KARMA = {
    'Aries': {
        'this_life': (
            'Learn independence and self-assertion. Life will repeatedly force you to stand alone, start things, '
            'and fight for what you believe. The pattern holding you back is people-pleasing, especially in partnerships. '
            'Ages 28-32 mark a turning point where a major event forces you to choose yourself.'
        ),
        'past_life': (
            'Ketu in Libra points to a past life invested in partnerships and diplomacy. You carry strong relationship '
            'skills but also a habit of losing yourself inside another person\'s needs.'
        ),
        'lesson': (
            'Build an individual identity from the ground up. When you feel the pull to compromise just to keep the peace, '
            'recognize the old pattern. Physical activities, competitive sports, or martial arts accelerate your progress.'
        ),
    },
    'Taurus': {
        'this_life': (
            'Build real material security and learn to enjoy stability without guilt. You are here to plant roots '
            'and create something lasting. Ages 30-35 bring a defining moment around money or property that anchors your values.'
        ),
        'past_life': (
            'Ketu in Scorpio points to a past life of intensity, crisis, and psychological power games. '
            'You carry deep resilience but also a pull toward drama even when life is calm.'
        ),
        'lesson': (
            'Choose stability over drama. Build rather than destroy. Financial literacy and hands-on creative work '
            'are your strongest tools for growth.'
        ),
    },
    'Gemini': {
        'this_life': (
            'Develop communication skills and genuine curiosity. Life will place you in environments requiring writing, '
            'speaking, or teaching. Sibling relationships are a key growth area. Ages 25-30 bring a pivotal experience '
            'that forces you to listen as much as you speak.'
        ),
        'past_life': (
            'Ketu in Sagittarius reveals a past life as a preacher or philosopher. You carry an assumption that you '
            'already know the answer, which can make you dismissive of everyday perspectives.'
        ),
        'lesson': (
            'Be a student again. Explore many viewpoints before committing to one. Journaling, debate, and language '
            'learning reward the intellectual humility this placement demands.'
        ),
    },
    'Cancer': {
        'this_life': (
            'Develop emotional intelligence and learn to nurture others genuinely. Life will place you in caregiving roles. '
            'Your challenge is emotional detachment disguised as professionalism. Ages 27-33 bring a major emotional '
            'opening, often through parenthood or a family health event.'
        ),
        'past_life': (
            'Ketu in Capricorn shows a past life dedicated to career and public status. You carry professional competence '
            'but are emotionally underdeveloped in ways you may not recognize.'
        ),
        'lesson': (
            'Prioritize family and emotional bonds over career achievements. The professional skills are already built in. '
            'Cooking, nurturing plants, and unhurried family time accelerate your growth.'
        ),
    },
    'Leo': {
        'this_life': (
            'Step into the spotlight and express your creative gifts boldly. Life will create stages for you in performance, '
            'management, or parenthood. Your trap is hiding behind group causes to avoid personal vulnerability. '
            'Ages 29-34 bring a creative or romantic breakthrough.'
        ),
        'past_life': (
            'Ketu in Aquarius reveals a past life serving groups and humanitarian causes. You carry big-picture thinking '
            'but also a pattern of suppressing individual desires for the collective.'
        ),
        'lesson': (
            'Shine individually without guilt. Take credit for your work and let romantic love be joyful. '
            'Creative writing, theater, and working with children accelerate your growth.'
        ),
    },
    'Virgo': {
        'this_life': (
            'Develop practical competence and serve others through tangible skill. Life will ask you to diagnose problems '
            'and improve systems. Your challenge is a pull toward vagueness and avoiding concrete commitments. '
            'Ages 26-31 bring a health or work crisis that forces you to get organized.'
        ),
        'past_life': (
            'Ketu in Pisces points to a past life of spiritual dissolution or artistic dreaming. You carry compassion '
            'and intuition but also weakened boundaries and difficulty functioning in practical reality.'
        ),
        'lesson': (
            'Ground your spiritual sensitivity in practical service. Learn a trade, develop a health routine, manage '
            'your finances. Do the work in front of you and deeper insights will follow.'
        ),
    },
    'Libra': {
        'this_life': (
            'Learn genuine partnership and diplomacy. Life will bring partners who challenge you to negotiate rather '
            'than dominate. Your trap is reflexive independence. Ages 28-33 bring a defining relationship that shows '
            'shared decisions can be stronger than solo ones.'
        ),
        'past_life': (
            'Ketu in Aries shows a past life as a warrior or fiercely independent individual. You carry deep self-reliance '
            'and an unconscious belief that needing someone is dangerous.'
        ),
        'lesson': (
            'Learn to cooperate without losing yourself. Develop active listening and fair negotiation skills. '
            'Art, music, and legal studies are powerful tools for this placement.'
        ),
    },
    'Scorpio': {
        'this_life': (
            'Embrace transformation and develop psychological courage. Joint finances, inheritance, and intimate trust '
            'are your growth arenas. Your pattern to watch is avoiding intensity and clinging to comfort. '
            'Ages 30-36 bring a transformative event that shifts your understanding of power.'
        ),
        'past_life': (
            'Ketu in Taurus reveals a past life of material comfort and stable accumulation. You carry an attachment '
            'to predictability and a resistance to change that this life is designed to dissolve.'
        ),
        'lesson': (
            'Let go of attachment to comfort and allow transformation to work. Learn psychology, deep finance, '
            'or energy healing. Every time you choose depth over safety, you fulfill your karmic contract.'
        ),
    },
    'Sagittarius': {
        'this_life': (
            'Develop a personal philosophy and expand your vision through higher learning and foreign perspectives. '
            'Life will send you abroad, physically or intellectually. Your trap is staying in the safe world of '
            'local networking. Ages 27-33 bring a journey that permanently expands your worldview.'
        ),
        'past_life': (
            'Ketu in Gemini points to a past life as a writer or information broker who knew a little about everything. '
            'You carry quick thinking but also a tendency to skim the surface without building facts into wisdom.'
        ),
        'lesson': (
            'Choose wisdom over information. Engage with a philosophical tradition seriously enough to be changed by it. '
            'University education, long-distance travel, and publishing are powerful vehicles for growth.'
        ),
    },
    'Capricorn': {
        'this_life': (
            'Build tangible structure in the public world and earn authority through real accomplishment. Career and '
            'your relationship with authority figures are the primary growth arenas. Your pattern to watch is retreating '
            'into family comfort when the world demands you step up. Ages 29-36 bring the defining career moment.'
        ),
        'past_life': (
            'Ketu in Cancer reveals a past life rooted in home and family. You carry nurturing ability but also '
            'a dependency on personal relationships for validation and a fear of the public world.'
        ),
        'lesson': (
            'Step out of the emotional comfort zone and build your public legacy. Make decisions based on long-term '
            'strategy rather than emotional impulse. Business management and architecture serve your evolution.'
        ),
    },
    'Aquarius': {
        'this_life': (
            'Serve humanity at scale through innovation and community networks. Your role is to facilitate change '
            'for many, not to seek personal applause. Friendships carry more karmic weight than romance here. '
            'Ages 30-36 bring a cause or community event that redirects your ambition toward service.'
        ),
        'past_life': (
            'Ketu in Leo reveals a past life of individual glory or creative authority. You carry charisma and confidence '
            'but also a deep attachment to being recognized and admired.'
        ),
        'lesson': (
            'Channel your creativity into innovation that serves many. Let go of the need to be the star. '
            'Technology, social justice, and humanitarian work are the strongest accelerators for this placement.'
        ),
    },
    'Pisces': {
        'this_life': (
            'Develop spiritual surrender and compassion. Life will bring experiences that logic cannot explain: '
            'mystical encounters, creative visions, acts of grace. Your trap is over-analysis and a need to control. '
            'Ages 28-34 bring a spiritual awakening that arrives through letting go, not effort.'
        ),
        'past_life': (
            'Ketu in Virgo shows a past life of analysis, practical service, and pursuit of perfection. You carry '
            'competence and discrimination but also an obsession with getting things right that blocks grace.'
        ),
        'lesson': (
            'Trust the current of life and let go of the need to control everything. Art, music, meditation, '
            'and devotion to something you cannot fully understand are your growth tools.'
        ),
    },
}

_SATURN_HOUSE_KARMA = {
    1: (
        'Saturn demands you earn respect through proven competence, not charisma. Build a consistent health routine '
        'and a dependable public image. When you do, people trust your presence without you needing to prove anything.'
    ),
    2: (
        'Saturn requires that wealth come through honest, steady labor and that your speech be measured and truthful. '
        'Budget carefully and earn your place in the family rather than assuming it. '
        'When you comply, financial stability and family trust grow decade by decade.'
    ),
    3: (
        'Saturn insists every word carry weight and that courage show through persistence, not impulsiveness. '
        'Support siblings even when it feels thankless, and refine how you communicate. '
        'When you comply, your words carry authority and sibling bonds mature into real alliances.'
    ),
    4: (
        'Saturn demands you build domestic peace through sustained effort rather than expecting it. '
        'Take responsibility for the household and provide for your mother even if the relationship is strained. '
        'When you comply, home becomes a genuine sanctuary built on your own dedication.'
    ),
    5: (
        'Saturn requires creative discipline and serious commitment to parenthood. '
        'Hone your craft through repetition, avoid risky speculation, and be a structured, present parent. '
        'When you comply, creative work lasts and your children respect your steady presence.'
    ),
    6: (
        'Saturn demands a disciplined health routine and strategic patience with competitors. '
        'Regular check-ups, structured diet, and treating service work as a duty are non-negotiable. '
        'When you comply, you outlast opponents and chronic health issues come under control.'
    ),
    7: (
        'Saturn treats marriage as a long-term contract requiring loyalty and unglamorous daily effort. '
        'Choose a partner for character over chemistry and commit fully. '
        'When you comply, the marriage deepens with every decade into genuine mutual trust.'
    ),
    8: (
        'Saturn demands you prepare for life\'s upheavals through insurance, estate planning, and psychological resilience. '
        'Face crises head-on rather than avoiding them. '
        'When you comply, you emerge from each crisis with composure and deeper understanding.'
    ),
    9: (
        'Saturn refuses to grant fortune through luck and insists belief be earned through lived experience. '
        'Study philosophy seriously and earn your father\'s respect through merit. '
        'When you comply, you develop hard-won wisdom that no setback can shake.'
    ),
    10: (
        'Saturn demands career authority be earned through decades of persistent, often thankless work. '
        'Accept hierarchy, build your reputation one project at a time, and avoid shortcuts. '
        'When you comply, your professional authority becomes unquestionable because everyone watched you earn it.'
    ),
    11: (
        'Saturn teaches that gains come with proportional responsibility and not every desire deserves fulfillment. '
        'Build your network through genuine service rather than convenience. '
        'When you comply, steady income and a small but reliable circle of friends arrive after middle age.'
    ),
    12: (
        'Saturn demands you treat solitude as preparation, not punishment, and manage expenses with awareness. '
        'Develop a consistent contemplative practice and approach foreign travel with patience. '
        'When you comply, you find genuine peace in your own company and can let go of attachments gracefully.'
    ),
}


def get_karmic_lessons(chart):
    """Karmic analysis from Rahu-Ketu axis, Saturn, and 12th house."""
    rahu = chart['planets']['Rahu']
    ketu = chart['planets']['Ketu']
    saturn = chart['planets']['Saturn']
    h12 = chart['houses'][12]

    # Rahu-Ketu axis
    rahu_karma = _RAHU_SIGN_KARMA.get(rahu['sign'], {
        'this_life': f'Growth through {rahu["sign"]} qualities.',
        'past_life': f'Ketu in {ketu["sign"]} — past-life mastery in these themes.',
        'lesson': 'Move toward Rahu\'s sign qualities, away from Ketu\'s comfort zone.',
    })

    # Saturn's karmic lesson
    saturn_lesson = _SATURN_HOUSE_KARMA.get(saturn['house'],
        f'Saturn in house {saturn["house"]} teaches discipline in {HOUSE_SIGNIFICATIONS.get(saturn["house"], "this area")}.')

    # 12th house — what to let go
    twelfth_sign = h12['sign']
    letting_go = {
        'Aries': 'Let go of aggression and the need to always be first.',
        'Taurus': 'Let go of attachment to material possessions and comfort.',
        'Gemini': 'Let go of overthinking and restless mental activity.',
        'Cancer': 'Let go of emotional clinginess and past memories.',
        'Leo': 'Let go of ego, pride, and the need for recognition.',
        'Virgo': 'Let go of perfectionism and over-analysis.',
        'Libra': 'Let go of people-pleasing and indecisiveness.',
        'Scorpio': 'Let go of control, jealousy, and desire for power over others.',
        'Sagittarius': 'Let go of rigid beliefs and the need to always be right.',
        'Capricorn': 'Let go of over-ambition and workaholism.',
        'Aquarius': 'Let go of detachment and intellectual superiority.',
        'Pisces': 'Let go of escapism, victimhood, and boundary dissolution.',
    }

    # Nodes in houses — additional karmic axis
    rahu_house_karma = {
        1: 'Karmic focus on developing individuality and self-reliance.',
        2: 'Karmic focus on building wealth and family through unconventional means.',
        3: 'Karmic focus on developing courage and communication skills.',
        4: 'Karmic focus on creating a home and emotional foundation.',
        5: 'Karmic focus on creativity, children, and self-expression.',
        6: 'Karmic focus on service, health, and overcoming obstacles.',
        7: 'Karmic focus on partnerships and learning to cooperate.',
        8: 'Karmic focus on transformation and dealing with shared resources.',
        9: 'Karmic focus on developing personal philosophy and higher wisdom.',
        10: 'Karmic focus on career, public role, and earning authority.',
        11: 'Karmic focus on community, networks, and fulfilling aspirations.',
        12: 'Karmic focus on spiritual liberation and transcendence.',
    }

    return {
        'rahu_sign': rahu['sign'],
        'rahu_house': rahu['house'],
        'ketu_sign': ketu['sign'],
        'ketu_house': ketu['house'],
        'rahu_karma': rahu_karma,
        'rahu_house_karma': rahu_house_karma.get(rahu['house'], ''),
        'saturn_sign': saturn['sign'],
        'saturn_house': saturn['house'],
        'saturn_lesson': saturn_lesson,
        'twelfth_sign': twelfth_sign,
        'letting_go': letting_go.get(twelfth_sign, 'Let go of attachments related to this sign.'),
        'summary': (
            f'Your soul\'s journey: Rahu in {rahu["sign"]} (H{rahu["house"]}) pulls you toward '
            f'{rahu_karma.get("this_life", "growth")}. Ketu in {ketu["sign"]} (H{ketu["house"]}) '
            f'shows past-life mastery you already carry. Saturn in {saturn["sign"]} (H{saturn["house"]}) '
            f'demands discipline: {saturn_lesson}'
        ),
    }


# ════════════════════════════════════════════════════════════════
# SECTION 9: DAILY RITUALS & PRACTICES
# ════════════════════════════════════════════════════════════════

_DEITY_FOR_ASC = {
    'Aries': {'deity': 'Lord Hanuman / Lord Kartikeya', 'mantra': 'Om Hanumate Namah'},
    'Taurus': {'deity': 'Goddess Lakshmi / Lord Krishna', 'mantra': 'Om Shreem Mahalakshmiyei Namah'},
    'Gemini': {'deity': 'Lord Vishnu / Lord Ganesha', 'mantra': 'Om Gan Ganapataye Namah'},
    'Cancer': {'deity': 'Goddess Parvati / Lord Shiva', 'mantra': 'Om Namah Shivaya'},
    'Leo': {'deity': 'Lord Surya / Lord Ram', 'mantra': 'Om Suryaya Namah'},
    'Virgo': {'deity': 'Lord Vishnu / Goddess Saraswati', 'mantra': 'Om Namo Narayanaya'},
    'Libra': {'deity': 'Goddess Lakshmi / Lord Venkateshwara', 'mantra': 'Om Shreem Hreem Kleem'},
    'Scorpio': {'deity': 'Lord Hanuman / Lord Bhairav', 'mantra': 'Om Hanumate Namah'},
    'Sagittarius': {'deity': 'Lord Dakshinamurthy / Lord Vishnu', 'mantra': 'Om Namo Bhagavate Vasudevaya'},
    'Capricorn': {'deity': 'Lord Shani Dev / Lord Hanuman', 'mantra': 'Om Sham Shanaischaraya Namah'},
    'Aquarius': {'deity': 'Lord Shani Dev / Lord Ganesh', 'mantra': 'Om Sham Shanaischaraya Namah'},
    'Pisces': {'deity': 'Lord Vishnu / Lord Dakshinamurthy', 'mantra': 'Om Namo Narayanaya'},
}

_MEDITATION_DIRECTION = {
    'Aries': 'East', 'Taurus': 'South-East', 'Gemini': 'North',
    'Cancer': 'North-West', 'Leo': 'East', 'Virgo': 'North',
    'Libra': 'West', 'Scorpio': 'South', 'Sagittarius': 'North-East',
    'Capricorn': 'West', 'Aquarius': 'West', 'Pisces': 'North-East',
}

_BEST_DAY = {
    'Sun': 'Sunday', 'Moon': 'Monday', 'Mars': 'Tuesday',
    'Mercury': 'Wednesday', 'Jupiter': 'Thursday', 'Venus': 'Friday',
    'Saturn': 'Saturday', 'Rahu': 'Saturday', 'Ketu': 'Tuesday',
}


def get_daily_rituals(chart):
    """Personalized daily rituals based on chart placements."""
    asc_sign = chart['ascendant']['sign']
    asc_lord = chart['ascendant']['lord']
    moon_sign = chart['planets']['Moon']['sign']

    # Primary deity and mantra
    deity_info = _DEITY_FOR_ASC.get(asc_sign, {'deity': 'Lord Vishnu', 'mantra': 'Om Namo Narayanaya'})

    # Lagna lord mantra
    lagna_lord_remedy = _PLANET_REMEDIES.get(asc_lord, {})

    # Meditation direction
    med_direction = _MEDITATION_DIRECTION.get(asc_sign, 'East')

    # Best day of week (based on lagna lord)
    best_day = _BEST_DAY.get(asc_lord, 'Sunday')

    # Colors to wear
    asc_colors = _PLANET_REMEDIES.get(asc_lord, {}).get('color', 'White')
    moon_lord = SIGN_LORDS.get(moon_sign, 'Moon')
    moon_colors = _PLANET_REMEDIES.get(moon_lord, {}).get('color', 'White')

    # Weak planets that need daily attention
    weak_planets = []
    for p in PLANETS:
        pd = chart['planets'][p]
        if pd['dignity'] in ('Debilitated', 'Enemy') or pd.get('is_combust', False):
            wp_remedy = _PLANET_REMEDIES.get(p, {})
            weak_planets.append({
                'planet': p,
                'mantra': wp_remedy.get('mantra', ''),
                'day': wp_remedy.get('day', ''),
            })

    # Foods
    asc_foods = _PLANET_REMEDIES.get(asc_lord, {}).get('food_favor', 'Balanced diet')
    avoid_foods = _PLANET_REMEDIES.get(asc_lord, {}).get('food_avoid', 'Nothing specific')

    # Waking time based on ascendant element
    element = SIGN_ELEMENT[chart['ascendant']['sign_idx']]
    wake_times = {
        'Fire': '5:00-5:30 AM (before sunrise for maximum energy)',
        'Earth': '5:30-6:00 AM (steady morning routine)',
        'Air': '5:00-5:30 AM (early for mental clarity)',
        'Water': '5:30-6:00 AM (gentle awakening with water intake)',
    }
    wake_time = wake_times.get(element, '5:30 AM')

    return {
        'primary_deity': deity_info['deity'],
        'primary_mantra': deity_info['mantra'],
        'lagna_lord': asc_lord,
        'lagna_lord_mantra': lagna_lord_remedy.get('mantra', ''),
        'meditation_direction': med_direction,
        'best_day': best_day,
        'best_colors': asc_colors,
        'secondary_colors': moon_colors,
        'wake_time': wake_time,
        'foods_to_favor': asc_foods,
        'foods_to_avoid': avoid_foods,
        'weak_planet_mantras': weak_planets,
        'daily_routine': [
            f'Wake up at {wake_time}',
            f'Face {med_direction} and recite "{deity_info["mantra"]}" 11 times',
            f'Recite lagna lord mantra "{lagna_lord_remedy.get("mantra", "")}" 11 times',
            'Offer water to Sun (Surya Arghya) if Sun is weak or for general vitality',
            f'Wear {asc_colors.split(",")[0].strip().lower()} color when possible',
            f'Eat foods that favor your chart: {asc_foods}',
            f'On {best_day}s, do special puja for {asc_lord}',
        ] + [
            f'On {wp["day"]}s, recite "{wp["mantra"]}" for weak {wp["planet"]}'
            for wp in weak_planets if wp['mantra']
        ] + [
            'Practice 10 minutes of meditation before sleep',
            f'Worship {deity_info["deity"]} for overall chart protection',
        ],
    }


# ════════════════════════════════════════════════════════════════
# SECTION 10: LUCKY POINTS
# ════════════════════════════════════════════════════════════════

_PLANET_NUMEROLOGY = {
    'Sun': 1, 'Moon': 2, 'Mars': 9, 'Mercury': 5,
    'Jupiter': 3, 'Venus': 6, 'Saturn': 8, 'Rahu': 4, 'Ketu': 7,
}

_PLANET_DAY_MAP = {
    'Sun': 'Sunday', 'Moon': 'Monday', 'Mars': 'Tuesday',
    'Mercury': 'Wednesday', 'Jupiter': 'Thursday', 'Venus': 'Friday',
    'Saturn': 'Saturday', 'Rahu': 'Saturday', 'Ketu': 'Tuesday',
}

_PLANET_METAL = {
    'Sun': 'Gold or Copper', 'Moon': 'Silver', 'Mars': 'Copper',
    'Mercury': 'Bronze', 'Jupiter': 'Gold', 'Venus': 'Silver or Platinum',
    'Saturn': 'Iron', 'Rahu': 'Lead or Ashtadhatu', 'Ketu': 'Iron or mixed metals',
}

# Functional benefics/malefics per ascendant (kendra/trikona lords vs dusthana lords)
_FUNCTIONAL_BENEFICS = {
    'Aries': ['Sun', 'Mars', 'Jupiter'],
    'Taurus': ['Venus', 'Saturn', 'Mercury'],
    'Gemini': ['Mercury', 'Venus', 'Saturn'],
    'Cancer': ['Moon', 'Mars', 'Jupiter'],
    'Leo': ['Sun', 'Mars', 'Jupiter'],
    'Virgo': ['Mercury', 'Venus'],
    'Libra': ['Venus', 'Saturn', 'Mercury'],
    'Scorpio': ['Mars', 'Moon', 'Jupiter'],
    'Sagittarius': ['Jupiter', 'Sun', 'Mars'],
    'Capricorn': ['Saturn', 'Venus', 'Mercury'],
    'Aquarius': ['Saturn', 'Venus'],
    'Pisces': ['Jupiter', 'Moon', 'Mars'],
}

_FUNCTIONAL_MALEFICS = {
    'Aries': ['Mercury', 'Rahu', 'Ketu'],
    'Taurus': ['Mars', 'Jupiter', 'Rahu', 'Ketu'],
    'Gemini': ['Mars', 'Rahu', 'Ketu'],
    'Cancer': ['Saturn', 'Rahu', 'Ketu'],
    'Leo': ['Saturn', 'Rahu', 'Ketu'],
    'Virgo': ['Mars', 'Moon', 'Rahu', 'Ketu'],
    'Libra': ['Sun', 'Jupiter', 'Rahu', 'Ketu'],
    'Scorpio': ['Mercury', 'Venus', 'Rahu', 'Ketu'],
    'Sagittarius': ['Venus', 'Rahu', 'Ketu'],
    'Capricorn': ['Mars', 'Moon', 'Jupiter', 'Rahu', 'Ketu'],
    'Aquarius': ['Moon', 'Mars', 'Jupiter', 'Rahu', 'Ketu'],
    'Pisces': ['Sun', 'Saturn', 'Venus', 'Mercury', 'Rahu', 'Ketu'],
}


def get_lucky_points(chart):
    """Calculate lucky numbers, days, stones, metals, colors, and more."""
    asc_sign = chart['ascendant']['sign']
    asc_lord = chart['ascendant']['lord']
    moon_sign = chart['planets']['Moon']['sign']
    moon_lord = SIGN_LORDS.get(moon_sign, 'Moon')

    # Lucky number from ascendant lord
    lucky_number = _PLANET_NUMEROLOGY.get(asc_lord, 1)

    # Good numbers: ascendant lord + moon sign lord
    asc_num = _PLANET_NUMEROLOGY.get(asc_lord, 1)
    moon_num = _PLANET_NUMEROLOGY.get(moon_lord, 2)
    good_numbers = sorted(set([asc_num, moon_num]))

    # Evil numbers: enemy planets of ascendant lord
    enemies = NATURAL_ENEMIES.get(asc_lord, [])
    evil_numbers = sorted(set(_PLANET_NUMEROLOGY.get(e, 0) for e in enemies))

    # Lucky days: ascendant lord's day + friends' days
    friends = NATURAL_FRIENDS.get(asc_lord, [])
    lucky_days = [_PLANET_DAY_MAP.get(asc_lord, 'Sunday')]
    for f in friends:
        day = _PLANET_DAY_MAP.get(f, '')
        if day and day not in lucky_days:
            lucky_days.append(day)

    # Lucky stone from _PLANET_REMEDIES
    lucky_stone = _PLANET_REMEDIES.get(asc_lord, {}).get('gemstone', 'Consult astrologer')

    # Lucky metal
    lucky_metal = _PLANET_METAL.get(asc_lord, 'Mixed metals')

    # Lucky color
    lucky_color = _PLANET_REMEDIES.get(asc_lord, {}).get('color', 'White')

    # Good and bad planets (functional)
    good_planets = _FUNCTIONAL_BENEFICS.get(asc_sign, [])
    bad_planets = _FUNCTIONAL_MALEFICS.get(asc_sign, [])

    # Friendly signs: signs owned by friends of ascendant lord
    friendly_signs = []
    for f in friends:
        for s in PLANET_OWNS.get(f, []):
            if s not in friendly_signs:
                friendly_signs.append(s)

    # Good years: ages that are multiples or harmonics of lucky number
    good_years = []
    age = lucky_number
    while age <= 90:
        good_years.append(age)
        age += lucky_number
    # Add single-digit harmonics (digit sum = lucky number)
    for a in range(10, 91):
        digit_sum = sum(int(d) for d in str(a))
        while digit_sum >= 10:
            digit_sum = sum(int(d) for d in str(digit_sum))
        if digit_sum == lucky_number and a not in good_years:
            good_years.append(a)
    good_years = sorted(good_years)

    return {
        'lucky_number': lucky_number,
        'good_numbers': good_numbers,
        'evil_numbers': evil_numbers,
        'lucky_days': lucky_days,
        'lucky_stone': lucky_stone,
        'lucky_metal': lucky_metal,
        'lucky_color': lucky_color,
        'good_planets': good_planets,
        'bad_planets': bad_planets,
        'friendly_signs': friendly_signs,
        'good_years': good_years,
    }


# ════════════════════════════════════════════════════════════════
# SECTION 11: SADE SATI REPORT
# ════════════════════════════════════════════════════════════════

# Saturn sign entry dates (approximate)
_SATURN_TRANSITS = [
    ('Aquarius',     2020, 1, 2022, 4),
    ('Pisces',       2022, 4, 2025, 3),
    ('Aries',        2025, 4, 2027, 6),
    ('Taurus',       2027, 6, 2029, 8),
    ('Gemini',       2029, 8, 2031, 10),
    ('Cancer',       2031, 10, 2033, 12),
    ('Leo',          2033, 12, 2036, 2),
    ('Virgo',        2036, 2, 2038, 4),
    ('Libra',        2038, 4, 2040, 6),
    ('Scorpio',      2040, 6, 2042, 8),
    ('Sagittarius',  2042, 8, 2044, 10),
    ('Capricorn',    2044, 10, 2046, 12),
    ('Aquarius',     2046, 12, 2049, 2),
    ('Pisces',       2049, 2, 2051, 4),
]

_SADE_SATI_PHASE_DESC = {
    'Rising': (
        "Saturn transits the 12th house from your Moon, marking the beginning of Sade Sati. "
        "You may face unexpected expenses, feel isolated from your usual support network, or deal with "
        "hidden adversaries working against you. Sleep disturbances and a restless mind are common. "
        "Foreign travel or relocation possibilities increase during this phase."
    ),
    'Peak': (
        "Saturn sits directly on your natal Moon, bringing the most intense phase of Sade Sati. "
        "Mental pressure, self-doubt, and emotional heaviness dominate. Your reputation may face challenges, "
        "health issues related to stress or chronic conditions surface. Relationships with mother or "
        "maternal figures come under strain. This is the period of deepest karmic reckoning."
    ),
    'Setting': (
        "Saturn transits the 2nd house from your Moon in the final phase. "
        "Financial pressures intensify, family disputes may arise, and your speech can get you into trouble. "
        "Savings built over years may deplete. Diet-related health issues or problems with teeth, eyes, "
        "or face are possible. The silver lining: this phase also builds financial discipline that lasts decades."
    ),
}

_SMALL_PANOTI_DESC = {
    '4th_from_moon': (
        "Saturn transits the 4th house from your Moon (Small Panoti / Dhaiya). "
        "Domestic peace gets disrupted. Property matters stall or create disputes. Your mother's health "
        "may need attention. Vehicles and home comforts suffer setbacks. Mental peace is hard to find, "
        "but hard work on the career front can still produce results."
    ),
    '8th_from_moon': (
        "Saturn transits the 8th house from your Moon (Small Panoti / Dhaiya). "
        "Sudden obstacles, health scares, or accidents become possible. Hidden matters surface. "
        "Joint finances or inheritance matters create complications. This is a period of forced "
        "transformation. Spiritual practices and health precautions are essential."
    ),
}


def _build_saturn_timeline(birth_year):
    """Build a complete Saturn transit timeline covering the person's life."""
    CYCLE = 29.5  # years per Saturn cycle
    timeline = []

    # Start from the earliest provided transit data and extend backward/forward
    for sign, sy, sm, ey, em in _SATURN_TRANSITS:
        # Add this transit directly
        timeline.append((sign, sy, sm, ey, em))
        # Extend backward in ~29.5 year steps
        offset = CYCLE
        while sy - offset >= birth_year - 5:
            back_sy = round(sy - offset)
            back_sm = sm
            back_ey = round(ey - offset)
            back_em = em
            timeline.append((sign, back_sy, back_sm, back_ey, back_em))
            offset += CYCLE
        # Extend forward
        offset = CYCLE
        while sy + offset <= birth_year + 100:
            fwd_sy = round(sy + offset)
            fwd_sm = sm
            fwd_ey = round(ey + offset)
            fwd_em = em
            timeline.append((sign, fwd_sy, fwd_sm, fwd_ey, fwd_em))
            offset += CYCLE

    # Sort by start year then month
    timeline.sort(key=lambda x: (x[1], x[2]))
    return timeline


def get_sade_sati(chart):
    """Calculate all Sade Sati and Small Panoti periods for the person's lifetime."""
    moon_sign = chart['planets']['Moon']['sign']
    moon_idx = chart['planets']['Moon']['sign_idx']
    birth_year = chart['birth']['year']

    # Signs that trigger Sade Sati phases (12th, 1st, 2nd from Moon)
    rising_idx = (moon_idx - 1) % 12   # 12th from Moon
    peak_idx = moon_idx                 # Moon sign itself
    setting_idx = (moon_idx + 1) % 12   # 2nd from Moon

    # Signs that trigger Small Panoti (4th and 8th from Moon)
    fourth_idx = (moon_idx + 3) % 12
    eighth_idx = (moon_idx + 7) % 12

    rising_sign = SIGNS[rising_idx]
    peak_sign = SIGNS[peak_idx]
    setting_sign = SIGNS[setting_idx]
    fourth_sign = SIGNS[fourth_idx]
    eighth_sign = SIGNS[eighth_idx]

    timeline = _build_saturn_timeline(birth_year)
    today = datetime.now()

    periods = []
    current_status = 'Free from Sade Sati and Small Panoti'

    for sign, sy, sm, ey, em in timeline:
        start_date = f'{sy}-{sm:02d}'
        end_date = f'{ey}-{em:02d}'

        # Skip periods entirely before birth
        if ey < birth_year:
            continue
        # Cap at reasonable future
        if sy > birth_year + 100:
            continue

        entry = None

        if sign == rising_sign:
            entry = {
                'type': 'Sade Sati',
                'phase': 'Rising',
                'saturn_sign': sign,
                'start': start_date,
                'end': end_date,
                'description': _SADE_SATI_PHASE_DESC['Rising'],
            }
        elif sign == peak_sign:
            entry = {
                'type': 'Sade Sati',
                'phase': 'Peak',
                'saturn_sign': sign,
                'start': start_date,
                'end': end_date,
                'description': _SADE_SATI_PHASE_DESC['Peak'],
            }
        elif sign == setting_sign:
            entry = {
                'type': 'Sade Sati',
                'phase': 'Setting',
                'saturn_sign': sign,
                'start': start_date,
                'end': end_date,
                'description': _SADE_SATI_PHASE_DESC['Setting'],
            }
        elif sign == fourth_sign:
            entry = {
                'type': 'Small Panoti',
                'phase': '4th from Moon',
                'saturn_sign': sign,
                'start': start_date,
                'end': end_date,
                'description': _SMALL_PANOTI_DESC['4th_from_moon'],
            }
        elif sign == eighth_sign:
            entry = {
                'type': 'Small Panoti',
                'phase': '8th from Moon',
                'saturn_sign': sign,
                'start': start_date,
                'end': end_date,
                'description': _SMALL_PANOTI_DESC['8th_from_moon'],
            }

        if entry:
            periods.append(entry)
            # Check current status
            start_dt = datetime(sy, sm, 1)
            end_dt = datetime(ey, em, 1)
            if start_dt <= today <= end_dt:
                if entry['type'] == 'Sade Sati':
                    current_status = f"Currently in Sade Sati ({entry['phase']} phase) with Saturn in {sign}"
                else:
                    current_status = f"Currently in Small Panoti ({entry['phase']}) with Saturn in {sign}"

    # Check if about to enter (within next 2 years)
    if 'Currently' not in current_status:
        for p in periods:
            try:
                ps_year, ps_month = map(int, p['start'].split('-'))
                p_start = datetime(ps_year, ps_month, 1)
                if today < p_start <= today + timedelta(days=730):
                    months_away = (ps_year - today.year) * 12 + (ps_month - today.month)
                    current_status = (
                        f"Free now, but {p['type']} ({p['phase']}) begins in approximately "
                        f"{months_away} months ({p['start']})"
                    )
                    break
            except (ValueError, TypeError):
                continue

    return {
        'moon_sign': moon_sign,
        'periods': periods,
        'current_status': current_status,
        'total_sade_sati_periods': len([p for p in periods if p['type'] == 'Sade Sati']),
        'total_small_panoti_periods': len([p for p in periods if p['type'] == 'Small Panoti']),
    }


# ════════════════════════════════════════════════════════════════
# SECTION 12: AVKAHADA CHAKRA
# ════════════════════════════════════════════════════════════════

_VARNA_MAP = {
    'Cancer': 'Brahmin', 'Scorpio': 'Brahmin', 'Pisces': 'Brahmin',
    'Aries': 'Kshatriya', 'Leo': 'Kshatriya', 'Sagittarius': 'Kshatriya',
    'Taurus': 'Vaishya', 'Virgo': 'Vaishya', 'Capricorn': 'Vaishya',
    'Gemini': 'Shudra', 'Libra': 'Shudra', 'Aquarius': 'Shudra',
}

_VARNA_DESC = {
    'Brahmin': (
        "Your Moon falls in a Brahmin varna sign, indicating a soul oriented toward knowledge, "
        "teaching, and spiritual pursuits. You are naturally drawn to learning, advisory roles, and "
        "intellectual leadership. Priestly, scholarly, or counseling professions suit your inner nature."
    ),
    'Kshatriya': (
        "Your Moon falls in a Kshatriya varna sign, pointing to a warrior spirit and leadership drive. "
        "You thrive in positions of authority, protective roles, and competitive environments. "
        "Administration, defense, entrepreneurship, and governance align with your core energy."
    ),
    'Vaishya': (
        "Your Moon falls in a Vaishya varna sign, showing a strong commercial instinct and practical "
        "intelligence. You excel in trade, finance, agriculture, and business management. Building "
        "wealth through sustained effort and smart resource allocation is your natural path."
    ),
    'Shudra': (
        "Your Moon falls in a Shudra varna sign, reflecting skill with hands, service orientation, "
        "and craftsmanship. You find fulfillment in artisanal work, technical fields, healthcare, "
        "or any profession where tangible results matter more than abstract theory."
    ),
}

_YONI_MAP = {
    'Ashwini': 'Horse', 'Bharani': 'Elephant', 'Krittika': 'Sheep',
    'Rohini': 'Serpent', 'Mrigashira': 'Serpent', 'Ardra': 'Dog',
    'Punarvasu': 'Cat', 'Pushya': 'Sheep', 'Ashlesha': 'Cat',
    'Magha': 'Rat', 'Purva Phalguni': 'Rat', 'Uttara Phalguni': 'Cow',
    'Hasta': 'Buffalo', 'Chitra': 'Tiger', 'Swati': 'Buffalo',
    'Vishakha': 'Tiger', 'Anuradha': 'Deer', 'Jyeshtha': 'Deer',
    'Mula': 'Dog', 'Purva Ashadha': 'Monkey', 'Uttara Ashadha': 'Mongoose',
    'Shravana': 'Monkey', 'Dhanishtha': 'Lion', 'Shatabhisha': 'Horse',
    'Purva Bhadrapada': 'Lion', 'Uttara Bhadrapada': 'Cow', 'Revati': 'Elephant',
}

_YONI_DESC = {
    'Horse': 'Your yoni is Horse, suggesting speed, restlessness, and a love for freedom. You need space in relationships and dislike being confined to routines.',
    'Elephant': 'Your yoni is Elephant, indicating dignity, patience, and tremendous inner strength. You move slowly but your decisions carry weight and permanence.',
    'Sheep': 'Your yoni is Sheep, reflecting a gentle, community-oriented nature. You prefer harmony over conflict and do best in supportive, nurturing environments.',
    'Serpent': 'Your yoni is Serpent, pointing to deep intuition, secretive tendencies, and magnetic charm. You read people well and rarely reveal your full hand.',
    'Dog': 'Your yoni is Dog, showing fierce loyalty, protective instincts, and sharp alertness. You guard your loved ones with everything you have.',
    'Cat': 'Your yoni is Cat, indicating independence, sensuality, and quiet observation. You are selective in your associations and value personal comfort highly.',
    'Rat': 'Your yoni is Rat, reflecting resourcefulness, adaptability, and accumulative instinct. You can thrive in lean conditions and always find a way forward.',
    'Cow': 'Your yoni is Cow, suggesting nourishing energy, patience, and a giving nature. Others naturally turn to you for sustenance and support.',
    'Buffalo': 'Your yoni is Buffalo, indicating endurance, hard work, and a powerful but slow-building temperament. You outlast competitors through sheer persistence.',
    'Tiger': 'Your yoni is Tiger, pointing to raw courage, dominance, and a commanding presence. You naturally take the lead and others instinctively defer to you.',
    'Deer': 'Your yoni is Deer, reflecting grace, sensitivity, and a somewhat timid outer shell. You move through life with elegance but startle easily under pressure.',
    'Monkey': 'Your yoni is Monkey, showing cleverness, playfulness, and quick thinking. You adapt to any social situation and use humor as both shield and weapon.',
    'Mongoose': 'Your yoni is Mongoose, indicating combative intelligence and a sharp, reactive mind. You strike decisively when threatened and rarely back down from confrontation.',
    'Lion': 'Your yoni is Lion, reflecting authority, pride, and a regal bearing. You expect respect as a default and carry yourself with natural dignity.',
}

_GANA_MAP = {
    'Ashwini': 'Deva', 'Mrigashira': 'Deva', 'Punarvasu': 'Deva',
    'Pushya': 'Deva', 'Hasta': 'Deva', 'Swati': 'Deva',
    'Anuradha': 'Deva', 'Shravana': 'Deva', 'Revati': 'Deva',
    'Bharani': 'Manushya', 'Rohini': 'Manushya', 'Ardra': 'Manushya',
    'Purva Phalguni': 'Manushya', 'Uttara Phalguni': 'Manushya',
    'Purva Ashadha': 'Manushya', 'Uttara Ashadha': 'Manushya',
    'Purva Bhadrapada': 'Manushya', 'Uttara Bhadrapada': 'Manushya',
    'Krittika': 'Rakshasa', 'Ashlesha': 'Rakshasa', 'Magha': 'Rakshasa',
    'Chitra': 'Rakshasa', 'Vishakha': 'Rakshasa', 'Jyeshtha': 'Rakshasa',
    'Mula': 'Rakshasa', 'Dhanishtha': 'Rakshasa', 'Shatabhisha': 'Rakshasa',
}

_GANA_DESC = {
    'Deva': (
        "Your gana is Deva (divine temperament). You are naturally inclined toward dharma, fairness, "
        "and constructive action. Others perceive you as approachable and well-intentioned. You prefer "
        "to resolve conflicts through dialogue rather than force."
    ),
    'Manushya': (
        "Your gana is Manushya (human temperament). You operate from a balanced mix of ambition and "
        "compassion. You understand worldly affairs deeply and navigate social structures skillfully. "
        "You weigh pros and cons before acting and rarely make purely emotional decisions."
    ),
    'Rakshasa': (
        "Your gana is Rakshasa (fierce temperament). You possess intense willpower, unyielding "
        "determination, and a no-nonsense attitude. You are not cruel by nature, but you refuse to "
        "tolerate injustice or deception. Your intensity can be intimidating but is ultimately protective."
    ),
}

_VASYA_MAP = {
    'Aries': 'Quadruped', 'Taurus': 'Quadruped', 'Gemini': 'Biped',
    'Cancer': 'Insect', 'Leo': 'Quadruped', 'Virgo': 'Biped',
    'Libra': 'Biped', 'Scorpio': 'Insect', 'Sagittarius': 'Biped (front half)',
    'Capricorn': 'Quadruped (front half)', 'Aquarius': 'Biped', 'Pisces': 'Water',
}

_NADI_MAP = {
    'Ashwini': 'Aadi', 'Ardra': 'Aadi', 'Punarvasu': 'Aadi',
    'Uttara Phalguni': 'Aadi', 'Hasta': 'Aadi', 'Jyeshtha': 'Aadi',
    'Mula': 'Aadi', 'Shatabhisha': 'Aadi', 'Purva Bhadrapada': 'Aadi',
    'Bharani': 'Madhya', 'Mrigashira': 'Madhya', 'Pushya': 'Madhya',
    'Purva Phalguni': 'Madhya', 'Chitra': 'Madhya', 'Anuradha': 'Madhya',
    'Purva Ashadha': 'Madhya', 'Dhanishtha': 'Madhya', 'Uttara Bhadrapada': 'Madhya',
    'Krittika': 'Antya', 'Rohini': 'Antya', 'Ashlesha': 'Antya',
    'Magha': 'Antya', 'Swati': 'Antya', 'Vishakha': 'Antya',
    'Uttara Ashadha': 'Antya', 'Shravana': 'Antya', 'Revati': 'Antya',
}

_NADI_DESC = {
    'Aadi': (
        "Your nadi is Aadi (Vata constitution). You tend toward a lighter frame, active mind, and "
        "variable energy levels. Wind-related health issues like joint pain, gas, anxiety, and "
        "irregular digestion need attention. Regular routine and warm, grounding foods help you most."
    ),
    'Madhya': (
        "Your nadi is Madhya (Pitta constitution). You have strong digestion, sharp intellect, and "
        "a medium build. Heat-related issues like acidity, inflammation, skin rashes, and anger "
        "outbursts are your vulnerabilities. Cooling foods and avoiding excess spice serve you well."
    ),
    'Antya': (
        "Your nadi is Antya (Kapha constitution). You tend toward a sturdy frame, steady energy, and "
        "calm temperament. Water-retention, sinus issues, lethargy, and weight gain are your weak "
        "points. Regular exercise and light, warm meals keep you in balance."
    ),
}

_TATVA_MAP = {
    'Aries': 'Fire', 'Leo': 'Fire', 'Sagittarius': 'Fire',
    'Taurus': 'Earth', 'Virgo': 'Earth', 'Capricorn': 'Earth',
    'Gemini': 'Air', 'Libra': 'Air', 'Aquarius': 'Air',
    'Cancer': 'Water', 'Scorpio': 'Water', 'Pisces': 'Water',
}

_TATVA_DESC = {
    'Fire': (
        "Your Moon's tatva is Fire. You are driven by action, initiative, and a need to lead. "
        "You process emotions quickly and move on. Anger is your primary emotional vulnerability, "
        "but it also fuels your greatest achievements."
    ),
    'Earth': (
        "Your Moon's tatva is Earth. You are grounded, practical, and security-conscious. "
        "You process emotions slowly but deeply. Material stability is essential for your peace of mind, "
        "and you build lasting structures in every area of life."
    ),
    'Air': (
        "Your Moon's tatva is Air. You are intellectually oriented, socially active, and mentally restless. "
        "You process emotions through analysis and conversation. Overthinking is your trap, "
        "but your ability to see multiple perspectives is your greatest asset."
    ),
    'Water': (
        "Your Moon's tatva is Water. You are emotionally deep, intuitive, and sensitive to atmospheres. "
        "You absorb the feelings of those around you. Emotional boundaries are essential for your "
        "wellbeing, but your empathy makes you a natural healer and counselor."
    ),
}

_PAYA_MAP = {1: 'Gold', 2: 'Silver', 3: 'Copper', 4: 'Iron'}

_PAYA_DESC = {
    'Gold': (
        "Your paya is Gold (Swarna), the most auspicious. The nakshatra's first pada bestows "
        "prosperity, recognition, and a fortunate start in life. Authority figures and institutions "
        "tend to favor you naturally."
    ),
    'Silver': (
        "Your paya is Silver (Rajat), indicating comfort, emotional richness, and artistic sensibility. "
        "You attract wealth through relationships and social connections rather than brute force."
    ),
    'Copper': (
        "Your paya is Copper (Tamra), suggesting a life of mixed results that improves with persistent "
        "effort. Early struggles give way to hard-earned success. Your resilience is your defining trait."
    ),
    'Iron': (
        "Your paya is Iron (Loha), indicating a tough, demanding life path that forges extraordinary "
        "strength. You face more obstacles than average but develop an unbreakable will. Late-life "
        "success is your signature pattern."
    ),
}


def get_avkahada_chakra(chart):
    """Calculate Avkahada Chakra elements from Moon sign and nakshatra."""
    moon_sign = chart['planets']['Moon']['sign']
    moon_nak = chart['planets']['Moon']['nakshatra']
    moon_pada = chart['planets']['Moon']['pada']

    varna = _VARNA_MAP.get(moon_sign, 'Vaishya')
    yoni = _YONI_MAP.get(moon_nak, 'Horse')
    gana = _GANA_MAP.get(moon_nak, 'Manushya')
    vasya = _VASYA_MAP.get(moon_sign, 'Biped')
    nadi = _NADI_MAP.get(moon_nak, 'Madhya')
    paya = _PAYA_MAP.get(moon_pada, 'Silver')
    tatva = _TATVA_MAP.get(moon_sign, 'Earth')

    return {
        'varna': varna,
        'varna_description': _VARNA_DESC.get(varna, ''),
        'yoni': yoni,
        'yoni_description': _YONI_DESC.get(yoni, ''),
        'gana': gana,
        'gana_description': _GANA_DESC.get(gana, ''),
        'vasya': vasya,
        'nadi': nadi,
        'nadi_description': _NADI_DESC.get(nadi, ''),
        'paya': paya,
        'paya_description': _PAYA_DESC.get(paya, ''),
        'tatva': tatva,
        'tatva_description': _TATVA_DESC.get(tatva, ''),
        'moon_sign': moon_sign,
        'moon_nakshatra': moon_nak,
        'moon_pada': moon_pada,
    }


# ════════════════════════════════════════════════════════════════
# SECTION 13: NAKSHATRA PHAL (MOON NAKSHATRA READING)
# ════════════════════════════════════════════════════════════════

_NAKSHATRA_PHAL = {
    'Ashwini': {
        'personality': (
            "You are quick-witted, impatient, and always in motion. Sitting idle makes you restless. "
            "You have a natural healing ability and an instinct to fix what is broken, whether it is "
            "a machine, a person, or a situation. Your decisions come fast, sometimes too fast. "
            "You are brave to the point of recklessness and deeply dislike taking orders from anyone."
        ),
        'education_income': (
            "You do well in medicine, sports, veterinary science, or any field requiring quick reflexes. "
            "Early career may involve frequent job changes before you find your niche. "
            "Income rises sharply after your late twenties once you commit to one direction."
        ),
        'family_life': (
            "You are fiercely protective of your family but can be emotionally unavailable due to "
            "constant activity. Marriage works best with a partner who values independence. "
            "You tend to marry someone from a different background than your own."
        ),
        'health': (
            "Head injuries, migraines, and accidents from speed or sports are your main risks. "
            "Your metabolism is fast, and you recover quickly from illness but burn out just as fast."
        ),
        'best_years': [17, 26, 28, 33, 40, 44],
    },
    'Bharani': {
        'personality': (
            "You carry a heavy sense of responsibility from a young age. Life teaches you about "
            "transformation, endings, and rebirth earlier than most. You have strong willpower and "
            "can endure situations that would break others. Your moral code is personal, not borrowed "
            "from society. You are intensely private about your inner world."
        ),
        'education_income': (
            "You thrive in law, finance, research, psychology, or anything involving investigation. "
            "Your income pattern is feast-or-famine in early years but stabilizes by your mid-thirties. "
            "You have a talent for managing other people's resources."
        ),
        'family_life': (
            "Relationships are intense and all-consuming for you. You demand deep loyalty and give the "
            "same in return. Family dynamics often involve power struggles. "
            "Your children become a source of profound transformation in your life."
        ),
        'health': (
            "Reproductive health, diabetes, and issues related to the lower abdomen need attention. "
            "You tend to suppress illness until it becomes serious. Regular checkups are not optional for you."
        ),
        'best_years': [20, 24, 33, 36, 42, 50],
    },
    'Krittika': {
        'personality': (
            "You have a sharp, cutting intellect and zero tolerance for dishonesty. Your words can "
            "burn, and you know it. You are fiercely independent, self-made, and proud of earning "
            "everything yourself. Authority comes naturally to you, but so does a tendency to be "
            "critical. You set impossibly high standards for yourself and everyone around you."
        ),
        'education_income': (
            "Military, engineering, surgery, cooking, or fire-related industries suit you. "
            "You earn through skill and expertise rather than connections. "
            "Your career takes a decisive upward turn in your early thirties."
        ),
        'family_life': (
            "You can be domineering at home without realizing it. Your partner needs thick skin "
            "and genuine respect for your capabilities. Family meals and shared routines "
            "are the glue that holds your domestic life together."
        ),
        'health': (
            "Acidity, fevers, inflammatory conditions, and issues with the neck and throat are common. "
            "You run hot both physically and emotionally."
        ),
        'best_years': [18, 25, 27, 35, 41, 48],
    },
    'Rohini': {
        'personality': (
            "You are magnetic, attractive, and have a natural gift for making others feel comfortable. "
            "Material beauty and sensory pleasure matter deeply to you. You are possessive about people "
            "and things you consider yours. Your creative eye is exceptional. "
            "You can be stubborn beyond reason when you have decided on something."
        ),
        'education_income': (
            "Fashion, agriculture, food industry, beauty, real estate, or the arts suit you best. "
            "You attract wealth naturally but must guard against overspending on luxuries. "
            "Your peak earning years start around 32 and continue strongly into your fifties."
        ),
        'family_life': (
            "You crave a beautiful home and a devoted partner. Jealousy and possessiveness can "
            "strain your marriage if unchecked. You are an indulgent parent who spoils children "
            "with affection and material comfort."
        ),
        'health': (
            "Throat issues, thyroid problems, and weight gain from overindulgence are your vulnerabilities. "
            "You benefit immensely from portion control and regular walks in nature."
        ),
        'best_years': [22, 25, 31, 38, 44, 51],
    },
    'Mrigashira': {
        'personality': (
            "You are perpetually curious, always searching for the next interesting thing. Your mind "
            "jumps between topics at dizzying speed. You have a gentle exterior but a restless core. "
            "You ask questions others never think of. Commitment to one path is your biggest challenge. "
            "You are naturally charming and witty in conversation."
        ),
        'education_income': (
            "Research, writing, journalism, travel industry, textiles, or sales suit your nature. "
            "You may have two income sources simultaneously. Your career path has more lateral moves "
            "than vertical climbs, but each move broadens your expertise significantly."
        ),
        'family_life': (
            "You need a partner who stimulates your mind. Boredom is the real enemy of your relationships. "
            "You are a fun, engaging parent but may struggle with the monotony of daily parenting routines. "
            "Extended family relationships are generally positive."
        ),
        'health': (
            "Nervous exhaustion, allergies, and upper respiratory issues are your weak spots. "
            "Your health improves dramatically when you reduce mental overstimulation and sleep on time."
        ),
        'best_years': [21, 27, 32, 36, 44, 50],
    },
    'Ardra': {
        'personality': (
            "You have experienced suffering or upheaval early in life, and it has made you sharper. "
            "You are analytical, sometimes cynical, but always honest. Your emotional storms can be "
            "intense, but you transform pain into power better than most. You have a dark sense of humor "
            "and a deep capacity for empathy born from your own struggles."
        ),
        'education_income': (
            "Technology, electronics, research, pharmaceuticals, or storm/disaster management suit you. "
            "Your career often involves a major disruption or restart around age 30. "
            "Post-disruption, your earning capacity multiplies."
        ),
        'family_life': (
            "Relationships require you to manage your emotional intensity. You form deep bonds but "
            "can push people away during your storm phases. Marriage stability improves significantly "
            "after your Saturn return. Your loyalty, once given, is permanent."
        ),
        'health': (
            "Asthma, mental health challenges, and chronic conditions triggered by stress are your risks. "
            "Breathing exercises and consistent therapy or meditation are non-negotiable for your wellbeing."
        ),
        'best_years': [24, 28, 34, 38, 42, 53],
    },
    'Punarvasu': {
        'personality': (
            "You are the eternal optimist who bounces back from setbacks with renewed energy. "
            "Your basic nature is generous, expansive, and philosophical. You see the bigger picture "
            "when others are lost in details. You dislike pettiness and small-mindedness. "
            "Your greatest strength is your ability to start over without bitterness."
        ),
        'education_income': (
            "Teaching, publishing, travel, import-export, philosophy, or spiritual counseling suit you. "
            "Your income may fluctuate but always recovers. Financial abundance comes in waves, "
            "with your strongest earning periods after 35."
        ),
        'family_life': (
            "You are a devoted family person who creates a warm, expansive home environment. "
            "You may live away from your birthplace for significant periods. "
            "Your children inherit your optimistic nature and benefit from your broad worldview."
        ),
        'health': (
            "Liver issues, weight gain from overeating, and respiratory conditions need watching. "
            "You recover from illness faster than most due to your inherently positive constitution."
        ),
        'best_years': [23, 27, 31, 36, 43, 48],
    },
    'Pushya': {
        'personality': (
            "You are the nourisher, the one everyone comes to for support and sustenance. Your patience "
            "is extraordinary, and your emotional steadiness anchors those around you. You are traditional "
            "in values but practical in approach. You rarely seek the spotlight but wield quiet influence. "
            "Your greatest risk is neglecting yourself while caring for everyone else."
        ),
        'education_income': (
            "Education, food industry, hospitality, dairy, healthcare, or government service suit you. "
            "You build wealth slowly and steadily. By your mid-forties, you are typically in a "
            "comfortable financial position earned through consistent effort."
        ),
        'family_life': (
            "Family is your center of gravity. You sacrifice willingly for children and parents. "
            "Your home is always open to guests. Marriage is generally stable and supportive, "
            "though you may feel unappreciated for the invisible work you do."
        ),
        'health': (
            "Water retention, chest congestion, and stomach acidity are your common complaints. "
            "You tend to eat emotionally. A disciplined diet transforms your health more than any medicine."
        ),
        'best_years': [22, 26, 33, 38, 45, 52],
    },
    'Ashlesha': {
        'personality': (
            "You are deeply perceptive, reading body language and hidden intentions with unsettling "
            "accuracy. Your mind works in layers, and you rarely take anything at face value. "
            "You can be manipulative when cornered, but your default mode is observant and strategic. "
            "Trust is something you give slowly and withdraw quickly. You have hypnotic personal magnetism."
        ),
        'education_income': (
            "Psychology, astrology, politics, pharmacology, poison/toxicology, or detective work suit you. "
            "You earn well from professions involving secrets or hidden knowledge. "
            "Financial instincts are sharp, and you rarely make losing investments."
        ),
        'family_life': (
            "Relationships with maternal figures are complicated. Your spouse must accept your need for "
            "emotional privacy. You are a protective but psychologically intense parent. "
            "Family dynamics involve undercurrents that outsiders never see."
        ),
        'health': (
            "Digestive issues, nervous disorders, and susceptibility to toxins or food poisoning are "
            "your vulnerabilities. Detox routines and avoiding processed foods are essential for you."
        ),
        'best_years': [19, 27, 30, 36, 42, 48],
    },
    'Magha': {
        'personality': (
            "You carry a sense of ancestral pride and an innate understanding of hierarchy. "
            "You demand respect and naturally command it through your bearing. Lineage, tradition, "
            "and legacy matter deeply to you. You are generous to those who show you loyalty "
            "but unforgiving toward disrespect. Your presence fills a room."
        ),
        'education_income': (
            "Administration, politics, history, heritage management, government, or family business suit you. "
            "You often inherit or continue a family professional legacy. "
            "Your earning potential peaks when you accept leadership positions without hesitation."
        ),
        'family_life': (
            "You treat your home like a kingdom. Family rituals, ancestral customs, and maintaining "
            "the family name are priorities. Marriage works when your partner respects your lineage. "
            "Your relationship with your father or father figures defines much of your life trajectory."
        ),
        'health': (
            "Heart conditions, back pain, and issues related to the spine are your primary concerns. "
            "Royal self-image means you may ignore symptoms until they become serious."
        ),
        'best_years': [21, 28, 33, 37, 44, 51],
    },
    'Purva Phalguni': {
        'personality': (
            "You are pleasure-loving, creative, and socially magnetic. You believe life should be "
            "enjoyed, not merely endured. Your artistic sensibility is refined, and you have excellent "
            "taste. You are generous with friends and lovers but can be lazy when unchallenged. "
            "Your charisma opens doors that hard work alone cannot."
        ),
        'education_income': (
            "Entertainment, arts, luxury goods, event management, or creative media suit you. "
            "You earn through charm and talent rather than grinding routine. "
            "Income is good but spending habits need constant monitoring."
        ),
        'family_life': (
            "You are a romantic partner who keeps the spark alive. Your home is tastefully decorated. "
            "Marriage may face challenges if your partner is overly practical or restrictive. "
            "Children bring out your playful, youthful side."
        ),
        'health': (
            "Reproductive health, lower back pain, and lifestyle diseases from excess indulgence are your risks. "
            "Moderation in diet and social activities is your best health strategy."
        ),
        'best_years': [22, 25, 31, 36, 44, 50],
    },
    'Uttara Phalguni': {
        'personality': (
            "You are reliable, dutiful, and focused on social contribution. People trust you with "
            "responsibility because you deliver consistently. Your approach to life is structured and "
            "purposeful. You combine warmth with discipline, making you an effective leader. "
            "You finish what you start, a trait rarer than most realize."
        ),
        'education_income': (
            "Government service, law, social work, corporate management, or philanthropy suit you. "
            "You build a solid career through competence and integrity. "
            "Financial growth is steady and predictable, peaking in your forties."
        ),
        'family_life': (
            "You take marriage vows seriously and create a stable, orderly home. Your partner appreciates "
            "your dependability. You may be stricter than necessary with children but always act from "
            "genuine concern for their future."
        ),
        'health': (
            "Digestive issues, hernias, and stress-related conditions from overwork are your risks. "
            "Scheduled relaxation and periodic breaks from responsibility are not luxury but necessity."
        ),
        'best_years': [24, 28, 35, 38, 46, 52],
    },
    'Hasta': {
        'personality': (
            "You are skilled with your hands and mind alike. Craftsmanship, precision, and attention "
            "to detail define you. You have a sharp wit and can be sarcastically funny. Your practical "
            "intelligence is exceptional. You sometimes struggle with self-doubt despite your obvious "
            "competence. You notice flaws others miss, in objects and in people."
        ),
        'education_income': (
            "Crafts, surgery, engineering, accounting, astrology, or any precision-based work suit you. "
            "You earn through specialized skill rather than general talent. "
            "Your value in the workplace increases steadily as your expertise deepens."
        ),
        'family_life': (
            "You show love through acts of service rather than words. Your home is well-organized. "
            "Marriage thrives when your partner recognizes your practical expressions of care. "
            "You teach your children through doing, not lecturing."
        ),
        'health': (
            "Skin conditions, digestive sensitivity, and nervous tension in the hands and arms are your concerns. "
            "Repetitive strain injuries are possible if you work with your hands extensively."
        ),
        'best_years': [20, 26, 32, 37, 42, 49],
    },
    'Chitra': {
        'personality': (
            "You are visually oriented, aesthetically driven, and drawn to creating beauty in all forms. "
            "Your appearance matters to you, and you invest in looking your best. You are ambitious "
            "with a competitive streak and a desire to be recognized for your unique contributions. "
            "Your inner world is more complex than your polished exterior suggests."
        ),
        'education_income': (
            "Architecture, fashion design, jewelry, interior design, or visual arts suit you. "
            "You can also excel in technology or engineering. "
            "Income rises significantly when you align your work with your aesthetic sensibility."
        ),
        'family_life': (
            "You need a partner who matches your standards of presentation and ambition. "
            "Superficial disagreements about lifestyle choices can escalate if unmanaged. "
            "Your home is a showpiece, and you take pride in creating an impressive living space."
        ),
        'health': (
            "Kidney issues, skin problems, and lower abdominal concerns need attention. "
            "Your health improves when you stop skipping meals for work and prioritize regular eating."
        ),
        'best_years': [23, 28, 33, 40, 45, 52],
    },
    'Swati': {
        'personality': (
            "You are independent, adaptable, and value personal freedom above almost everything. "
            "You bend without breaking, like the wind. Your diplomatic skills are excellent, and you "
            "can negotiate your way through situations that defeat more rigid personalities. "
            "You are fair-minded but indecisive when multiple good options exist."
        ),
        'education_income': (
            "Business, trade, diplomacy, travel, commission-based work, or law suit you. "
            "You prosper through networking and deal-making. Self-employment suits you better than "
            "rigid corporate structures. Income fluctuates but averages well."
        ),
        'family_life': (
            "You need space within your relationships. A controlling partner suffocates you. "
            "You are a fair, balanced parent who teaches independence by example. "
            "Your family life stabilizes significantly after your mid-thirties."
        ),
        'health': (
            "Kidney and urinary tract issues, skin allergies, and gas-related problems are your weak areas. "
            "You benefit from drinking plenty of water and avoiding cold, dry foods."
        ),
        'best_years': [21, 25, 31, 35, 43, 49],
    },
    'Vishakha': {
        'personality': (
            "You are goal-obsessed with a single-minded focus that can be both your greatest asset "
            "and your biggest blind spot. You set targets and pursue them relentlessly. Your ambition "
            "has a spiritual undertone. You are competitive but also philosophical about success and "
            "failure. You experience periodic identity crises that force meaningful transformation."
        ),
        'education_income': (
            "Research, politics, marketing, agriculture, or spiritual teaching suit you. "
            "You often achieve breakthrough success after prolonged struggle. "
            "Your income graph shows a clear before-and-after point where everything changes."
        ),
        'family_life': (
            "You bring intensity to your relationships that can overwhelm a gentle partner. "
            "Marriage benefits from shared goals and mutual ambition. "
            "You push your children to achieve, sometimes harder than they are ready for."
        ),
        'health': (
            "Liver and pancreas issues, hormonal imbalances, and burnout from overwork are your risks. "
            "Learning to celebrate small wins instead of only the final goal protects your mental health."
        ),
        'best_years': [24, 28, 33, 37, 44, 51],
    },
    'Anuradha': {
        'personality': (
            "You are devoted, emotionally resilient, and capable of thriving in foreign environments. "
            "You form deep friendships and honor your commitments even when it costs you. You have a "
            "quiet intensity that people underestimate at their peril. Organization and discipline "
            "come naturally. You succeed precisely where others have given up."
        ),
        'education_income': (
            "Corporate management, foreign assignments, occult sciences, statistics, or mining suit you. "
            "You often earn your best income away from your birthplace. "
            "Career breakthroughs involve a mentor or organizational backing."
        ),
        'family_life': (
            "You are a deeply loyal partner who invests fully in your relationship. Betrayal devastates "
            "you more than most. You maintain close ties with friends who become like family. "
            "Your children respect you for your integrity and steadfastness."
        ),
        'health': (
            "Hip and pelvic issues, dental problems, and reproductive health concerns are your vulnerabilities. "
            "Stress manifests physically for you more than mentally. Regular physical activity is essential."
        ),
        'best_years': [23, 27, 33, 38, 45, 50],
    },
    'Jyeshtha': {
        'personality': (
            "You are the eldest soul in any room, carrying authority and protective instincts "
            "regardless of your actual birth order. You are resourceful, brave, and quick to take "
            "charge during crises. Your sharp tongue and commanding manner can create enemies. "
            "You struggle with jealousy from peers and siblings. Power is your default orientation."
        ),
        'education_income': (
            "Police, military, administration, senior management, or crisis management suit you. "
            "You earn respect and income through demonstrated competence under pressure. "
            "Your career is marked by at least one major battle that defines your professional identity."
        ),
        'family_life': (
            "Sibling relationships are complicated and often involve rivalry. Your marriage needs "
            "a partner who accepts your dominant nature without being subservient. "
            "You are fiercely protective of your children but may impose your unfulfilled ambitions on them."
        ),
        'health': (
            "Muscular pain, joint issues, and stress-induced conditions are your weak spots. "
            "Anger and control issues affect your cardiovascular health. Regular de-stressing is critical."
        ),
        'best_years': [18, 26, 30, 36, 42, 50],
    },
    'Mula': {
        'personality': (
            "You are drawn to root causes, hidden truths, and the foundations beneath surface appearances. "
            "Destruction and reconstruction are recurring themes in your life. You question everything, "
            "including beliefs you were raised with. Your path involves stripping away the inessential "
            "to find what truly matters. You can be brutally honest."
        ),
        'education_income': (
            "Research, medicine (especially root-cause diagnosis), philosophy, botany, or investigation suit you. "
            "Your career may involve a complete restart at least once. "
            "Your greatest earning potential lies in specialized or niche domains."
        ),
        'family_life': (
            "Family relationships involve fundamental disagreements about values or lifestyle. "
            "You may distance yourself from your birth family to forge your own path. "
            "Marriage requires a partner who respects your need to question everything."
        ),
        'health': (
            "Hip and thigh problems, sciatic pain, and genetic or hereditary health conditions need attention. "
            "Your health often improves dramatically when you resolve deep psychological conflicts."
        ),
        'best_years': [19, 27, 31, 36, 42, 48],
    },
    'Purva Ashadha': {
        'personality': (
            "You are persuasive, optimistic, and have an infectious enthusiasm that wins people over. "
            "You believe in your vision even when no one else does, and this conviction often proves "
            "justified. You declare victory before the battle is won, which is both inspiring and "
            "occasionally premature. Your sense of justice is strong and vocal."
        ),
        'education_income': (
            "Law, public speaking, water-related industries, shipping, or motivational work suit you. "
            "You earn well from persuasion-based professions. "
            "International connections or foreign clientele boost your income significantly."
        ),
        'family_life': (
            "You are an enthusiastic partner who keeps the relationship dynamic and forward-looking. "
            "Your tendency to overcommit socially can leave your family feeling second-priority. "
            "Children admire your confidence and storytelling ability."
        ),
        'health': (
            "Thigh and hip issues, liver problems, and obesity from social eating are your risks. "
            "Water-based exercises like swimming suit your constitution perfectly."
        ),
        'best_years': [23, 28, 34, 38, 45, 52],
    },
    'Uttara Ashadha': {
        'personality': (
            "You are principled, unwavering, and committed to doing what is right regardless of personal "
            "cost. Your integrity is your identity. You are a late bloomer who achieves lasting success "
            "through sustained effort rather than lucky breaks. You are universally respected even by those "
            "who disagree with you. Your patience is legendary."
        ),
        'education_income': (
            "Government, judiciary, defense, agriculture, or social reform suit you. "
            "Career progress is slow but irreversible. You rarely get demoted or sidelined once you "
            "establish yourself. Your peak earning years are your late forties and fifties."
        ),
        'family_life': (
            "You are a rock-solid partner and parent. Your family relies on your stability. "
            "Marriage is a lifelong commitment you honor fully. You may marry later than average. "
            "Your children respect your discipline and learn perseverance from watching you."
        ),
        'health': (
            "Knee problems, bone density issues, and chronic conditions that worsen with age need monitoring. "
            "Preventive care starting in your thirties pays enormous dividends later."
        ),
        'best_years': [26, 30, 36, 42, 48, 55],
    },
    'Shravana': {
        'personality': (
            "You are an exceptional listener who absorbs information from every conversation. "
            "Your learning style is auditory, and you remember what you hear with remarkable clarity. "
            "You are wise beyond your years and often sought out for counsel. Your patience in "
            "understanding situations fully before acting gives you a decisive advantage."
        ),
        'education_income': (
            "Music, teaching, counseling, telecommunications, media, or knowledge management suit you. "
            "You earn through wisdom, knowledge transmission, and advisory roles. "
            "Your career flourishes when you position yourself as an expert or guide."
        ),
        'family_life': (
            "You create a harmonious home through attentive listening and measured responses. "
            "Your partner values your calm presence. You are the family member everyone calls "
            "when they need perspective. Your children develop strong communication skills from your example."
        ),
        'health': (
            "Ear infections, hearing issues, and knee or joint problems are your vulnerabilities. "
            "Protecting your ears from excessive noise is important for your long-term wellbeing."
        ),
        'best_years': [22, 28, 33, 39, 44, 51],
    },
    'Dhanishtha': {
        'personality': (
            "You are ambitious, rhythmically inclined, and drawn to wealth and status. Music and rhythm "
            "resonate with your soul at a fundamental level. You are generous when prosperous but "
            "can become ruthlessly competitive when resources are scarce. Your social skills are sharp, "
            "and you know how to work a room. You set trends rather than follow them."
        ),
        'education_income': (
            "Music, real estate, sports, surgery, or management suit you. "
            "You have a talent for converting assets into income. Property and fixed assets "
            "are your strongest wealth-building tools."
        ),
        'family_life': (
            "Marital harmony requires effort, as your ambitious nature can overshadow domestic duties. "
            "Delayed marriage or initial adjustment difficulties are common. "
            "Once settled, you build a prosperous household that others admire."
        ),
        'health': (
            "Blood pressure, anemia, and bone-marrow related issues need monitoring. "
            "Rhythmic exercise like walking to music or dancing keeps you physically balanced."
        ),
        'best_years': [24, 28, 35, 40, 46, 53],
    },
    'Shatabhisha': {
        'personality': (
            "You are a lone wolf with a healer's heart. You prefer working independently and can "
            "seem secretive or aloof to those who do not know you well. Your analytical mind excels "
            "at solving puzzles nobody else can crack. You have a contrarian streak and instinctively "
            "challenge mainstream thinking. Your independence is non-negotiable."
        ),
        'education_income': (
            "Medicine, technology, astrology, aviation, or space sciences suit you. "
            "You excel in roles that require solitary focus and technical depth. "
            "Your income grows when you embrace your specialist nature rather than trying to generalize."
        ),
        'family_life': (
            "Relationships require you to overcome your emotional guardedness. Your partner must accept "
            "your need for solitude without taking it personally. You are a thoughtful parent who teaches "
            "children to think for themselves."
        ),
        'health': (
            "Heart palpitations, calf muscle issues, and circulatory problems are your health concerns. "
            "You respond well to alternative medicine and holistic healing approaches."
        ),
        'best_years': [23, 29, 34, 38, 44, 51],
    },
    'Purva Bhadrapada': {
        'personality': (
            "You oscillate between worldly ambition and spiritual intensity. One part of you wants "
            "material success, the other craves transcendence. This internal tension makes you a "
            "powerful force when channeled correctly. You are passionate to the point of extremism "
            "and can be either profoundly generous or fiercely punishing."
        ),
        'education_income': (
            "Finance, occult studies, research, insurance, or transformative industries suit you. "
            "Your income often comes through unconventional channels. "
            "A spiritual practice paradoxically improves your material earning capacity."
        ),
        'family_life': (
            "You bring intensity to domestic life that can be both nurturing and overwhelming. "
            "Your partner needs emotional resilience. Family life improves dramatically when you "
            "find a spiritual outlet for your intensity rather than directing it at loved ones."
        ),
        'health': (
            "Swollen ankles, liver problems, and stress-induced conditions are your risks. "
            "Your health is directly tied to your mental state. Inner peace equals physical health for you."
        ),
        'best_years': [24, 28, 33, 40, 46, 53],
    },
    'Uttara Bhadrapada': {
        'personality': (
            "You are deeply compassionate, wise, and naturally inclined toward spirituality. "
            "Your patience and endurance are remarkable. You think in long time horizons and rarely "
            "panic over short-term setbacks. You have a gift for counseling and healing. "
            "Your calm exterior conceals depths that most people never see."
        ),
        'education_income': (
            "Charity work, spiritual teaching, counseling, marine industries, or research suit you. "
            "You may not chase money aggressively, but it finds you through your service and wisdom. "
            "Late-career recognition and financial rewards are your pattern."
        ),
        'family_life': (
            "You create a peaceful, spiritually oriented home. Your partner appreciates your "
            "emotional depth and stability. You are a wise parent who guides without controlling. "
            "Family members turn to you as the anchor during crises."
        ),
        'health': (
            "Foot problems, sleep disorders, and issues related to the lymphatic system are your concerns. "
            "Adequate sleep and foot care are simple but essential health practices for you."
        ),
        'best_years': [25, 30, 36, 42, 48, 55],
    },
    'Revati': {
        'personality': (
            "You are the nurturer of the zodiac, gentle, empathetic, and naturally protective of "
            "the vulnerable. Your imagination is vivid and your creative abilities are strong. "
            "You see potential in people and situations that others have written off. Your weakness "
            "is being overly trusting and sometimes naive about others' intentions."
        ),
        'education_income': (
            "Creative arts, marine biology, travel, hospitality, or healing professions suit you. "
            "You prosper in environments that value empathy and creativity. "
            "Your income improves when you stop undervaluing your own contributions."
        ),
        'family_life': (
            "You pour love into your family with complete selflessness. Your home is a sanctuary "
            "for anyone who needs shelter. Marriage is deeply fulfilling when your partner reciprocates "
            "your emotional generosity. Your children are creative and sensitive."
        ),
        'health': (
            "Foot ailments, allergies, and immune system sensitivity are your health concerns. "
            "You absorb stress from others physically. Energy clearing practices and adequate rest are vital."
        ),
        'best_years': [22, 27, 33, 38, 44, 50],
    },
}


def get_nakshatra_phal(chart):
    """Detailed Moon nakshatra reading for the person."""
    moon_nak = chart['planets']['Moon']['nakshatra']
    moon_pada = chart['planets']['Moon']['pada']
    moon_sign = chart['planets']['Moon']['sign']
    moon_lord = SIGN_LORDS.get(moon_sign, 'Moon')
    nak_lord = chart['planets']['Moon']['nakshatra_lord']

    phal = _NAKSHATRA_PHAL.get(moon_nak, {})

    return {
        'nakshatra': moon_nak,
        'pada': moon_pada,
        'nakshatra_lord': nak_lord,
        'moon_sign': moon_sign,
        'moon_sign_lord': moon_lord,
        'personality': phal.get('personality', ''),
        'education_income': phal.get('education_income', ''),
        'family_life': phal.get('family_life', ''),
        'health': phal.get('health', ''),
        'best_years': phal.get('best_years', []),
    }


# ════════════════════════════════════════════════════════════════
# MASTER FUNCTION
# ════════════════════════════════════════════════════════════════

def generate_all_predictions(chart):
    """Master function: generate all prediction sections."""
    return {
        'doshas': detect_doshas(chart),
        'planetary_analysis': analyze_planets(chart),
        'lal_kitab': get_lal_kitab_predictions(chart),
        'life_predictions': get_life_predictions(chart),
        'yearly_forecast': get_yearly_forecast(chart),
        'remedies': get_remedies(chart),
        'house_strengthening': get_house_strengthening(chart),
        'karmic_lessons': get_karmic_lessons(chart),
        'daily_rituals': get_daily_rituals(chart),
        'lucky_points': get_lucky_points(chart),
        'sade_sati': get_sade_sati(chart),
        'avkahada_chakra': get_avkahada_chakra(chart),
        'nakshatra_phal': get_nakshatra_phal(chart),
    }
