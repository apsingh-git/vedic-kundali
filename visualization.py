"""
Vedic Astrology Chart Visualization — South Indian Style Charts,
Dasha Timeline, and Planetary Position Tables using Matplotlib.
"""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch
import numpy as np
from datetime import datetime
from constants import *


# ── Color Palette ─────────────────────────────────────────────
COLORS = {
    'bg': '#1a1a2e',
    'chart_bg': '#16213e',
    'grid': '#e94560',
    'grid_light': '#533483',
    'sign_text': '#a8a8a8',
    'planet_benefic': '#4ecca3',
    'planet_malefic': '#e94560',
    'planet_neutral': '#eeeeee',
    'retrograde': '#f9a825',
    'lagna_mark': '#ff6b6b',
    'title': '#eeeeee',
    'subtitle': '#a8a8a8',
    'dasha_current': '#4ecca3',
    'dasha_past': '#533483',
    'dasha_future': '#16213e',
    'text': '#eeeeee',
    'accent': '#e94560',
}

BENEFIC_PLANETS = {'Jupiter', 'Venus', 'Moon', 'Mercury'}
MALEFIC_PLANETS = {'Sun', 'Mars', 'Saturn', 'Rahu', 'Ketu'}


def planet_color(name):
    if name in BENEFIC_PLANETS:
        return COLORS['planet_benefic']
    elif name in MALEFIC_PLANETS:
        return COLORS['planet_malefic']
    return COLORS['planet_neutral']


def draw_south_indian_chart(chart_data, chart_type='D1', title=None, ax=None):
    """
    Draw a South Indian style chart on a matplotlib axes.
    chart_data: dict mapping planet names to sign indices + optional 'ascendant' key
    """
    standalone = ax is None
    if standalone:
        fig, ax = plt.subplots(1, 1, figsize=(8, 8), facecolor=COLORS['bg'])

    ax.set_facecolor(COLORS['chart_bg'])
    ax.set_xlim(0, 4)
    ax.set_ylim(0, 4)
    ax.set_aspect('equal')
    ax.axis('off')

    # Draw grid
    for i in range(5):
        ax.plot([i, i], [0, 4], color=COLORS['grid'], linewidth=1.5)
        ax.plot([0, 4], [i, i], color=COLORS['grid'], linewidth=1.5)

    # Clear inner 2x2
    inner = FancyBboxPatch((1, 1), 2, 2, boxstyle="square,pad=0",
                            facecolor=COLORS['chart_bg'], edgecolor=COLORS['grid'],
                            linewidth=1.5)
    ax.add_patch(inner)

    # Chart label in center
    if title:
        ax.text(2, 2.15, title, ha='center', va='center',
                fontsize=16, fontweight='bold', color=COLORS['title'],
                fontfamily='serif')

    # Get ascendant sign for lagna marking
    asc_sign_idx = None
    if 'ascendant' in chart_data:
        asc_sign_idx = chart_data['ascendant'].get('sign_idx')

    # Collect planets per sign
    sign_planets = {i: [] for i in range(12)}
    for name in PLANETS:
        if name in chart_data and name != 'ascendant':
            s_idx = chart_data[name].get('sign_idx')
            if s_idx is not None:
                suffix = ''
                # Check retrograde from main chart planets data
                if isinstance(chart_data[name], dict) and chart_data[name].get('is_retrograde'):
                    suffix = '(R)'
                sign_planets[s_idx].append((name, suffix))

    # Draw each sign box
    for sign_idx in range(12):
        if sign_idx not in SOUTH_INDIAN_LAYOUT:
            continue
        row, col = SOUTH_INDIAN_LAYOUT[sign_idx]
        # Convert to matplotlib coords (row 0 = top, but y=0 is bottom)
        x = col
        y = 3 - row  # Flip y

        # Sign abbreviation (top-left of cell)
        ax.text(x + 0.08, y + 0.92, SIGN_ABBR[sign_idx],
                ha='left', va='top', fontsize=8, color=COLORS['sign_text'],
                fontstyle='italic', alpha=0.7)

        # Lagna marker (diagonal line in the cell)
        if sign_idx == asc_sign_idx:
            ax.plot([x, x + 0.25], [y + 1, y + 0.75],
                    color=COLORS['lagna_mark'], linewidth=2.5)
            ax.text(x + 0.28, y + 0.92, 'Asc',
                    ha='left', va='top', fontsize=7, color=COLORS['lagna_mark'],
                    fontweight='bold')

        # Place planets
        planets_in_sign = sign_planets[sign_idx]
        for i, (pname, suffix) in enumerate(planets_in_sign):
            px = x + 0.5
            py = y + 0.65 - (i * 0.18)
            if len(planets_in_sign) > 4:
                py = y + 0.75 - (i * 0.14)

            label = PLANET_ABBR.get(pname, pname[:2])
            if suffix:
                label += suffix

            color = planet_color(pname)
            ax.text(px, py, label, ha='center', va='center',
                    fontsize=11, fontweight='bold', color=color,
                    fontfamily='monospace')

    if standalone:
        plt.tight_layout()
        return fig
    return ax


def draw_full_chart_page(chart, output_path):
    """
    Draw complete chart page: D1 (Rasi), D9 (Navamsha), with birth details.
    """
    fig = plt.figure(figsize=(20, 12), facecolor=COLORS['bg'])

    # Title
    birth = chart['birth']
    date_str = f"{birth['day']:02d}/{birth['month']:02d}/{birth['year']}"
    time_str = f"{birth['hour']:02d}:{birth['minute']:02d}"
    name = birth.get('name', '')
    name_part = f"{name}  |  " if name else ""
    title = f"{name_part}Vedic Birth Chart  |  {date_str}  {time_str}  |  {birth['timezone']}"
    fig.suptitle(title, fontsize=18, fontweight='bold', color=COLORS['title'],
                 fontfamily='serif', y=0.97)

    asc = chart['ascendant']
    subtitle = (f"Lagna: {asc['sign']} {asc['degree']:.1f}°  |  "
                f"Nakshatra: {asc['nakshatra']} Pada {asc['pada']}  |  "
                f"Ayanamsa (Lahiri): {chart['ayanamsa']:.4f}°")
    fig.text(0.5, 0.93, subtitle, ha='center', fontsize=12,
             color=COLORS['subtitle'], fontfamily='serif')

    # ── D1 Rasi Chart ──────────────────────────
    ax1 = fig.add_axes([0.02, 0.08, 0.45, 0.80])
    d1_data = {'ascendant': {'sign_idx': asc['sign_idx']}}
    for name in PLANETS:
        d1_data[name] = {
            'sign_idx': chart['planets'][name]['sign_idx'],
            'is_retrograde': chart['planets'][name]['is_retrograde'],
        }
    draw_south_indian_chart(d1_data, 'D1', 'RASI (D1)', ax1)

    # ── D9 Navamsha Chart ──────────────────────
    ax2 = fig.add_axes([0.52, 0.08, 0.45, 0.80])
    d9 = chart['divisional']['D9']
    d9_data = {'ascendant': d9['ascendant']}
    for name in PLANETS:
        d9_data[name] = {
            'sign_idx': d9[name]['sign_idx'],
            'is_retrograde': chart['planets'][name]['is_retrograde'],
        }
    draw_south_indian_chart(d9_data, 'D9', 'NAVAMSHA (D9)', ax2)

    plt.savefig(output_path, dpi=150, bbox_inches='tight',
                facecolor=COLORS['bg'], edgecolor='none')
    plt.close(fig)
    return output_path


def draw_divisional_charts_page(chart, output_path):
    """Draw D10 (Dasamsha) and D7 (Saptamsha) charts."""
    fig = plt.figure(figsize=(20, 12), facecolor=COLORS['bg'])
    fig.suptitle('Divisional Charts', fontsize=18, fontweight='bold',
                 color=COLORS['title'], fontfamily='serif', y=0.97)

    # D10
    ax1 = fig.add_axes([0.02, 0.08, 0.45, 0.80])
    d10 = chart['divisional']['D10']
    d10_data = {'ascendant': d10['ascendant']}
    for name in PLANETS:
        d10_data[name] = {
            'sign_idx': d10[name]['sign_idx'],
            'is_retrograde': chart['planets'][name]['is_retrograde'],
        }
    draw_south_indian_chart(d10_data, 'D10', 'DASAMSHA (D10)\nCareer', ax1)

    # D7
    ax2 = fig.add_axes([0.52, 0.08, 0.45, 0.80])
    d7 = chart['divisional']['D7']
    d7_data = {'ascendant': d7['ascendant']}
    for name in PLANETS:
        d7_data[name] = {
            'sign_idx': d7[name]['sign_idx'],
            'is_retrograde': chart['planets'][name]['is_retrograde'],
        }
    draw_south_indian_chart(d7_data, 'D7', 'SAPTAMSHA (D7)\nChildren', ax2)

    plt.savefig(output_path, dpi=150, bbox_inches='tight',
                facecolor=COLORS['bg'], edgecolor='none')
    plt.close(fig)
    return output_path


def draw_dasha_timeline(dashas, output_path):
    """Draw Vimshottari Dasha timeline with Mahadashas and current Antardashas."""
    now = datetime.now(dashas['dashas'][0]['start'].tzinfo)

    # Filter dashas to show relevant range (past 30 years to next 30 years)
    relevant = []
    for d in dashas['dashas']:
        if d['end'].year >= (now.year - 30) and d['start'].year <= (now.year + 40):
            relevant.append(d)

    if not relevant:
        relevant = dashas['dashas'][:9]

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(20, 10), facecolor=COLORS['bg'],
                                     gridspec_kw={'height_ratios': [1, 1.5]})

    # ── Mahadasha Timeline (top) ──────────────
    ax1.set_facecolor(COLORS['bg'])
    ax1.set_title('VIMSHOTTARI MAHADASHA TIMELINE', fontsize=16, fontweight='bold',
                  color=COLORS['title'], fontfamily='serif', pad=15)

    dasha_colors = {
        'Sun': '#FF6B35', 'Moon': '#C0C0C0', 'Mars': '#DC143C',
        'Mercury': '#00CC66', 'Jupiter': '#FFD700', 'Venus': '#FF69B4',
        'Saturn': '#4169E1', 'Rahu': '#8B4513', 'Ketu': '#9370DB',
    }

    y_pos = 0.5
    bar_height = 0.6

    min_date = min(d['start'] for d in relevant)
    max_date = max(d['end'] for d in relevant)
    total_days = (max_date - min_date).total_seconds() / 86400

    for d in relevant:
        start_offset = (d['start'] - min_date).total_seconds() / 86400
        duration = (d['end'] - d['start']).total_seconds() / 86400
        x = start_offset / total_days
        w = duration / total_days

        color = dasha_colors.get(d['lord'], '#666666')
        alpha = 1.0 if d.get('is_current') else 0.6
        edgecolor = COLORS['accent'] if d.get('is_current') else 'none'
        lw = 3 if d.get('is_current') else 0

        rect = patches.FancyBboxPatch((x, y_pos - bar_height/2), w, bar_height,
                                       boxstyle="round,pad=0.01",
                                       facecolor=color, alpha=alpha,
                                       edgecolor=edgecolor, linewidth=lw)
        ax1.add_patch(rect)

        # Label
        if w > 0.03:
            label = f"{d['lord']}\n{d['start'].strftime('%Y')}-{d['end'].strftime('%Y')}"
            ax1.text(x + w/2, y_pos, label, ha='center', va='center',
                    fontsize=9, fontweight='bold', color='white',
                    fontfamily='monospace')

    # Now marker
    now_offset = (now - min_date).total_seconds() / 86400
    now_x = now_offset / total_days
    ax1.axvline(x=now_x, color=COLORS['accent'], linewidth=2, linestyle='--', alpha=0.8)
    ax1.text(now_x, y_pos + bar_height/2 + 0.15, 'NOW', ha='center', va='bottom',
            fontsize=10, fontweight='bold', color=COLORS['accent'])

    ax1.set_xlim(0, 1)
    ax1.set_ylim(-0.2, 1.2)
    ax1.axis('off')

    # ── Current Mahadasha Antardashas (bottom) ──
    ax2.set_facecolor(COLORS['bg'])
    current_maha = None
    for d in dashas['dashas']:
        if d.get('is_current'):
            current_maha = d
            break

    if current_maha:
        ax2.set_title(f'CURRENT MAHADASHA: {current_maha["lord"]} '
                     f'({current_maha["start"].strftime("%b %Y")} — '
                     f'{current_maha["end"].strftime("%b %Y")})\n'
                     f'Antardasha Breakdown',
                     fontsize=14, fontweight='bold', color=COLORS['title'],
                     fontfamily='serif', pad=15)

        antars = current_maha['antardashas']
        total_days_m = (current_maha['end'] - current_maha['start']).total_seconds() / 86400

        for i, ad in enumerate(antars):
            start_off = (ad['start'] - current_maha['start']).total_seconds() / 86400
            dur = (ad['end'] - ad['start']).total_seconds() / 86400
            x = start_off / total_days_m
            w = dur / total_days_m

            color = dasha_colors.get(ad['lord'], '#666666')
            is_past = ad['end'] < now
            is_current = ad.get('is_current', False)

            alpha = 0.3 if is_past else (1.0 if is_current else 0.7)
            lw = 3 if is_current else 0

            rect = patches.FancyBboxPatch((x, 0.3), w, 0.4,
                                           boxstyle="round,pad=0.005",
                                           facecolor=color, alpha=alpha,
                                           edgecolor=COLORS['accent'] if is_current else 'none',
                                           linewidth=lw)
            ax2.add_patch(rect)

            if w > 0.04:
                label = f"{ad['lord']}\n{ad['start'].strftime('%b %y')}"
                ax2.text(x + w/2, 0.5, label, ha='center', va='center',
                        fontsize=8, fontweight='bold', color='white',
                        fontfamily='monospace')

        # Now marker
        now_off = (now - current_maha['start']).total_seconds() / 86400
        now_x2 = now_off / total_days_m
        if 0 <= now_x2 <= 1:
            ax2.axvline(x=now_x2, color=COLORS['accent'], linewidth=2, linestyle='--')

        ax2.set_xlim(0, 1)
        ax2.set_ylim(0, 1)
    ax2.axis('off')

    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight',
                facecolor=COLORS['bg'], edgecolor='none')
    plt.close(fig)
    return output_path


def draw_planetary_strength_chart(chart, output_path):
    """Draw a visual summary of planetary dignity, houses, and status."""
    fig, ax = plt.subplots(figsize=(16, 9), facecolor=COLORS['bg'])
    ax.set_facecolor(COLORS['bg'])
    ax.axis('off')

    ax.set_title('PLANETARY POSITIONS & STRENGTH', fontsize=18, fontweight='bold',
                 color=COLORS['title'], fontfamily='serif', pad=20)

    # Table headers
    headers = ['Planet', 'Sign', 'Degree', 'Nakshatra', 'Pada', 'House',
               'Dignity', 'R', 'Nak Lord']
    col_x = [0.02, 0.10, 0.22, 0.34, 0.50, 0.58, 0.66, 0.80, 0.87]

    y = 0.92
    for i, h in enumerate(headers):
        ax.text(col_x[i], y, h, ha='left', va='center', fontsize=12,
                fontweight='bold', color=COLORS['accent'], fontfamily='monospace',
                transform=ax.transAxes)

    # Separator line
    ax.plot([0.01, 0.99], [0.88, 0.88], color=COLORS['grid_light'],
            linewidth=1, transform=ax.transAxes)

    # Planet rows
    dignity_colors = {
        'Exalted': '#4ecca3', 'Moolatrikona': '#7bc67e', 'Own Sign': '#90be6d',
        'Friendly': '#f9c74f', 'Neutral': '#a8a8a8', 'Enemy': '#f8961e',
        'Debilitated': '#e94560',
    }

    y = 0.83
    # Add Ascendant first
    asc = chart['ascendant']
    row_data = [
        'Lagna', asc['sign'], f"{asc['degree']:.1f}°",
        asc['nakshatra'], str(asc['pada']), '1',
        '—', '—', '—'
    ]
    for i, val in enumerate(row_data):
        color = COLORS['lagna_mark'] if i == 0 else COLORS['text']
        ax.text(col_x[i], y, val, ha='left', va='center', fontsize=11,
                color=color, fontfamily='monospace', transform=ax.transAxes)
    y -= 0.06

    for name in PLANETS:
        p = chart['planets'][name]
        deg_str = f"{p['degree']:.1f}°"
        retro = 'R' if p['is_retrograde'] else ''
        dignity = p.get('dignity', 'Neutral')
        d_color = dignity_colors.get(dignity, COLORS['text'])

        row = [
            PLANET_ABBR[name] + ' ' + name,
            p['sign'],
            deg_str,
            p['nakshatra'],
            str(p['pada']),
            str(p['house']),
            dignity,
            retro,
            p.get('nakshatra_lord', ''),
        ]

        for i, val in enumerate(row):
            if i == 0:
                color = planet_color(name)
            elif i == 6:
                color = d_color
            elif i == 7 and val == 'R':
                color = COLORS['retrograde']
            else:
                color = COLORS['text']

            ax.text(col_x[i], y, val, ha='left', va='center', fontsize=11,
                    color=color, fontfamily='monospace', transform=ax.transAxes)
        y -= 0.06

    # Combustion note
    y -= 0.04
    combust_planets = [n for n in PLANETS if chart['planets'][n].get('is_combust')]
    if combust_planets:
        ax.text(0.02, y, f"Combust: {', '.join(combust_planets)}",
                ha='left', va='center', fontsize=10, color=COLORS['retrograde'],
                fontfamily='monospace', transform=ax.transAxes, fontstyle='italic')

    plt.savefig(output_path, dpi=150, bbox_inches='tight',
                facecolor=COLORS['bg'], edgecolor='none')
    plt.close(fig)
    return output_path
