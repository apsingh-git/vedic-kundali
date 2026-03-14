"""
HTML Report Generator — Clean, aesthetic Vedic birth chart report.
Generates a single self-contained HTML file with embedded charts and analysis.
"""

import base64
import io
import os
from datetime import datetime

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from constants import *
from visualization import (
    draw_south_indian_chart,
    COLORS as VIZ_COLORS,
    planet_color,
    PLANET_ABBR,
)
from predictions import generate_all_predictions


def chart_to_base64(draw_func, *args, **kwargs):
    """Render a matplotlib figure and return as base64 PNG string."""
    fig = draw_func(*args, **kwargs)
    if fig is None:
        return ''
    buf = io.BytesIO()
    fig.savefig(buf, format='png', dpi=150, bbox_inches='tight',
                facecolor=VIZ_COLORS['bg'], edgecolor='none')
    plt.close(fig)
    buf.seek(0)
    return base64.b64encode(buf.read()).decode('utf-8')


def render_chart_image(chart_data, chart_type, title):
    """Render a single South Indian chart to base64."""
    fig, ax = plt.subplots(1, 1, figsize=(6, 6), facecolor=VIZ_COLORS['bg'])
    draw_south_indian_chart(chart_data, chart_type, title, ax)
    buf = io.BytesIO()
    fig.savefig(buf, format='png', dpi=150, bbox_inches='tight',
                facecolor=VIZ_COLORS['bg'], edgecolor='none')
    plt.close(fig)
    buf.seek(0)
    return base64.b64encode(buf.read()).decode('utf-8')


def _build_d1_data(chart):
    asc = chart['ascendant']
    d1 = {'ascendant': {'sign_idx': asc['sign_idx']}}
    for name in PLANETS:
        d1[name] = {
            'sign_idx': chart['planets'][name]['sign_idx'],
            'is_retrograde': chart['planets'][name]['is_retrograde'],
        }
    return d1


def _build_div_data(div_chart, main_planets):
    data = {'ascendant': div_chart['ascendant']}
    for name in PLANETS:
        data[name] = {
            'sign_idx': div_chart[name]['sign_idx'],
            'is_retrograde': main_planets[name]['is_retrograde'],
        }
    return data


def dignity_class(dignity):
    if dignity in ('Exalted', 'Moolatrikona'):
        return 'dignity-exalted'
    elif dignity == 'Own Sign':
        return 'dignity-own'
    elif dignity == 'Friendly':
        return 'dignity-friendly'
    elif dignity == 'Neutral':
        return 'dignity-neutral'
    elif dignity == 'Enemy':
        return 'dignity-enemy'
    elif dignity == 'Debilitated':
        return 'dignity-debilitated'
    return 'dignity-neutral'


def planet_class(name):
    if name in ('Jupiter', 'Venus', 'Moon', 'Mercury'):
        return 'planet-benefic'
    return 'planet-malefic'


def generate_html_report(chart, yogas_list, output_path=None):
    """Generate complete HTML report. Returns HTML string and optionally saves to file."""

    b = chart['birth']
    asc = chart['ascendant']
    name = b.get('name', 'Birth Chart')
    date_str = f"{b['day']:02d}/{b['month']:02d}/{b['year']}"
    time_str = f"{b['hour']:02d}:{b['minute']:02d}"

    # Generate chart images
    d1_data = _build_d1_data(chart)
    d1_img = render_chart_image(d1_data, 'D1', 'RASI (D1)')

    d9 = chart['divisional']['D9']
    d9_data = _build_div_data(d9, chart['planets'])
    d9_img = render_chart_image(d9_data, 'D9', 'NAVAMSHA (D9)')

    d10 = chart['divisional']['D10']
    d10_data = _build_div_data(d10, chart['planets'])
    d10_img = render_chart_image(d10_data, 'D10', 'DASAMSHA (D10)')

    d7 = chart['divisional']['D7']
    d7_data = _build_div_data(d7, chart['planets'])
    d7_img = render_chart_image(d7_data, 'D7', 'SAPTAMSHA (D7)')

    # Dasha data
    dashas = chart['dashas']
    current_maha = None
    current_antar = None
    for d in dashas['dashas']:
        if d.get('is_current'):
            current_maha = d
            for ad in d['antardashas']:
                if ad.get('is_current'):
                    current_antar = ad
                    break
            break

    # Vargottama
    vargottama = []
    for n in PLANETS:
        if chart['planets'][n]['sign_idx'] == d9[n]['sign_idx']:
            vargottama.append(n)

    # Generate predictions
    pred = generate_all_predictions(chart)

    # Build HTML
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{name} — Vedic Birth Chart</title>
<style>
  :root {{
    --bg: #0f0f1a;
    --card: #1a1a2e;
    --card-alt: #16213e;
    --border: #2a2a4a;
    --accent: #e94560;
    --accent-soft: rgba(233, 69, 96, 0.15);
    --green: #4ecca3;
    --green-soft: rgba(78, 204, 163, 0.15);
    --gold: #f9c74f;
    --gold-soft: rgba(249, 199, 79, 0.12);
    --orange: #f8961e;
    --text: #e0e0e0;
    --text-dim: #8888a0;
    --text-bright: #ffffff;
    --radius: 12px;
  }}
  /* Light theme */
  .light {{
    --bg: #f5f5f0;
    --card: #ffffff;
    --card-alt: #f0ede6;
    --border: #d4d0c8;
    --accent: #c23152;
    --accent-soft: rgba(194, 49, 82, 0.1);
    --green: #2a9d6a;
    --green-soft: rgba(42, 157, 106, 0.1);
    --gold: #b8860b;
    --gold-soft: rgba(184, 134, 11, 0.08);
    --orange: #d47600;
    --text: #333333;
    --text-dim: #777777;
    --text-bright: #111111;
  }}
  .light img {{ filter: brightness(1.1) contrast(0.9); }}

  * {{ margin: 0; padding: 0; box-sizing: border-box; }}
  html {{ scroll-behavior: smooth; scroll-padding-top: 20px; overflow-x: hidden; overscroll-behavior-x: none; }}
  body {{ overscroll-behavior-x: none; }}
  /* Prevent tables and grids from pushing page width */
  table, .data-table {{ max-width: 100%; }}
  .table-scroll {{ overflow-x: auto; -webkit-overflow-scrolling: touch; max-width: 100%; overscroll-behavior-x: contain; }}
  .pred-grid {{ max-width: 100%; }}
  .container {{ overflow-x: hidden; }}
  /* Charts responsive */
  .chart-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(260px, 1fr)); }}
  .chart-box img {{ max-width: 100%; height: auto; }}
  /* Life cards responsive */
  .life-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); }}

  body {{
    font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, sans-serif;
    background: var(--bg);
    color: var(--text);
    line-height: 1.6;
    padding: 0;
  }}

  /* ── Header ─────────────────────────────── */
  .header {{
    background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
    padding: 48px 24px 40px;
    text-align: center;
    border-bottom: 1px solid var(--border);
  }}
  .header h1 {{
    font-size: 2.2rem;
    font-weight: 300;
    color: var(--text-bright);
    letter-spacing: 2px;
    margin-bottom: 4px;
  }}
  .header .subtitle {{
    font-size: 0.85rem;
    color: var(--text-dim);
    letter-spacing: 4px;
    text-transform: uppercase;
    margin-bottom: 28px;
  }}
  .header-grid {{
    display: flex;
    justify-content: center;
    gap: 40px;
    flex-wrap: wrap;
  }}
  .header-item {{
    text-align: center;
  }}
  .header-item .label {{
    font-size: 0.7rem;
    color: var(--text-dim);
    text-transform: uppercase;
    letter-spacing: 2px;
  }}
  .header-item .value {{
    font-size: 1.1rem;
    color: var(--text-bright);
    font-weight: 500;
  }}
  .header-item .value.accent {{ color: var(--accent); }}

  /* ── Container ──────────────────────────── */
  .container {{
    max-width: 1200px;
    margin: 0 auto;
    padding: 32px 20px;
  }}

  /* ── Section ────────────────────────────── */
  .section {{
    margin-bottom: 40px;
  }}
  .section-title {{
    font-size: 0.75rem;
    font-weight: 600;
    color: var(--accent);
    text-transform: uppercase;
    letter-spacing: 3px;
    margin-bottom: 16px;
    padding-bottom: 8px;
    border-bottom: 1px solid var(--border);
  }}

  /* ── Cards ──────────────────────────────── */
  .card {{
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 24px;
    margin-bottom: 16px;
  }}
  .card-alt {{
    background: var(--card-alt);
  }}

  /* ── Chart Grid ─────────────────────────── */
  .chart-grid {{
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
    gap: 20px;
  }}
  .chart-box {{
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    overflow: hidden;
    text-align: center;
  }}
  .chart-box img {{
    width: 100%;
    display: block;
  }}
  .chart-box .chart-label {{
    padding: 10px;
    font-size: 0.75rem;
    color: var(--text-dim);
    letter-spacing: 2px;
    text-transform: uppercase;
  }}

  /* ── Table ──────────────────────────────── */
  .data-table {{
    width: 100%;
    border-collapse: collapse;
    font-size: 0.9rem;
  }}
  .data-table th {{
    text-align: left;
    padding: 10px 12px;
    font-size: 0.7rem;
    font-weight: 600;
    color: var(--accent);
    text-transform: uppercase;
    letter-spacing: 1.5px;
    border-bottom: 1px solid var(--border);
  }}
  .data-table td {{
    padding: 10px 12px;
    border-bottom: 1px solid rgba(42, 42, 74, 0.5);
    vertical-align: top;
  }}
  .data-table tr:last-child td {{ border-bottom: none; }}
  .data-table tr:hover {{ background: rgba(233, 69, 96, 0.03); }}

  /* ── Dignity Colors ─────────────────────── */
  .dignity-exalted {{ color: #4ecca3; font-weight: 600; }}
  .dignity-own {{ color: #90be6d; font-weight: 600; }}
  .dignity-friendly {{ color: #f9c74f; }}
  .dignity-neutral {{ color: var(--text-dim); }}
  .dignity-enemy {{ color: #f8961e; }}
  .dignity-debilitated {{ color: #e94560; font-weight: 600; }}

  .planet-benefic {{ color: #4ecca3; }}
  .planet-malefic {{ color: #e94560; }}

  .tag {{
    display: inline-block;
    padding: 2px 8px;
    border-radius: 4px;
    font-size: 0.75rem;
    font-weight: 500;
  }}
  .tag-retro {{
    background: rgba(249, 168, 37, 0.15);
    color: #f9a825;
  }}
  .tag-combust {{
    background: rgba(233, 69, 96, 0.15);
    color: #e94560;
  }}
  .tag-vargottama {{
    background: var(--green-soft);
    color: var(--green);
  }}

  /* ── Yoga Cards ─────────────────────────── */
  .yoga-grid {{
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 12px;
  }}
  .yoga-card {{
    background: var(--card-alt);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 16px;
    border-left: 3px solid var(--accent);
  }}
  .yoga-card.positive {{ border-left-color: var(--green); }}
  .yoga-card.challenging {{ border-left-color: var(--orange); }}
  .yoga-card .yoga-name {{
    font-weight: 600;
    color: var(--text-bright);
    margin-bottom: 4px;
    font-size: 0.95rem;
  }}
  .yoga-card .yoga-planets {{
    font-size: 0.78rem;
    color: var(--text-dim);
    margin-bottom: 6px;
  }}
  .yoga-card .yoga-effect {{
    font-size: 0.85rem;
    color: var(--text);
    line-height: 1.5;
  }}
  .yoga-strength {{
    display: inline-block;
    padding: 1px 6px;
    border-radius: 3px;
    font-size: 0.7rem;
    font-weight: 600;
    margin-left: 6px;
  }}
  .strength-strong {{ background: var(--green-soft); color: var(--green); }}
  .strength-moderate {{ background: var(--gold-soft); color: var(--gold); }}
  .strength-weak {{ background: var(--accent-soft); color: var(--accent); }}

  /* ── House Grid ─────────────────────────── */
  .house-grid {{
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 12px;
  }}
  .house-card {{
    background: var(--card-alt);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 14px 16px;
  }}
  .house-num {{
    font-size: 0.7rem;
    color: var(--accent);
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 1px;
  }}
  .house-sign {{
    font-size: 1rem;
    color: var(--text-bright);
    font-weight: 500;
  }}
  .house-detail {{
    font-size: 0.8rem;
    color: var(--text-dim);
    margin-top: 4px;
  }}
  .house-occupants {{
    margin-top: 6px;
    font-size: 0.85rem;
  }}

  /* ── Dasha Timeline ─────────────────────── */
  .dasha-bar {{
    display: flex;
    border-radius: 6px;
    overflow: hidden;
    margin-bottom: 16px;
    height: 44px;
  }}
  .dasha-segment {{
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 0.75rem;
    font-weight: 600;
    color: white;
    position: relative;
    transition: opacity 0.2s;
    min-width: 0;
  }}
  .dasha-segment span {{
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    padding: 0 4px;
  }}
  .dasha-segment.current {{
    outline: 2px solid var(--accent);
    outline-offset: -2px;
    z-index: 1;
  }}
  .dasha-segment.past {{ opacity: 0.4; }}

  .dasha-detail-grid {{
    display: grid;
    grid-template-columns: 1fr 1fr 1fr;
    gap: 10px;
  }}
  .dasha-detail {{
    background: var(--card-alt);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 12px;
    font-size: 0.85rem;
  }}
  .dasha-detail.active {{
    border-color: var(--accent);
    background: var(--accent-soft);
  }}
  .dasha-lord {{
    font-weight: 600;
    color: var(--text-bright);
  }}
  .dasha-dates {{
    font-size: 0.78rem;
    color: var(--text-dim);
    margin-top: 2px;
  }}

  /* ── Life Areas ─────────────────────────── */
  .life-grid {{
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 16px;
  }}
  .life-card {{
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 20px;
  }}
  .life-card h3 {{
    font-size: 0.8rem;
    color: var(--accent);
    text-transform: uppercase;
    letter-spacing: 2px;
    margin-bottom: 12px;
  }}
  .life-card .life-detail {{
    font-size: 0.85rem;
    margin-bottom: 6px;
  }}
  .life-card .life-detail strong {{
    color: var(--text-bright);
  }}
  .life-reading {{
    margin-top: 10px;
    padding-top: 10px;
    border-top: 1px solid var(--border);
    font-size: 0.85rem;
    color: var(--text);
    line-height: 1.6;
  }}

  /* ── Strength Bars ──────────────────────── */
  .strength-row {{
    display: flex;
    align-items: center;
    margin-bottom: 8px;
    gap: 10px;
  }}
  .strength-name {{
    width: 80px;
    font-size: 0.85rem;
    font-weight: 500;
    text-align: right;
  }}
  .strength-bar-bg {{
    flex: 1;
    height: 8px;
    background: var(--border);
    border-radius: 4px;
    overflow: hidden;
  }}
  .strength-bar {{
    height: 100%;
    border-radius: 4px;
    transition: width 0.3s;
  }}
  .strength-label {{
    width: 90px;
    font-size: 0.75rem;
    color: var(--text-dim);
  }}

  /* ── Predictive ─────────────────────────── */
  .timeline-item {{
    display: flex;
    gap: 16px;
    margin-bottom: 16px;
    padding-left: 20px;
    border-left: 2px solid var(--border);
    position: relative;
  }}
  .timeline-item::before {{
    content: '';
    position: absolute;
    left: -5px;
    top: 6px;
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background: var(--border);
  }}
  .timeline-item.active {{ border-left-color: var(--accent); }}
  .timeline-item.active::before {{ background: var(--accent); }}
  .timeline-content {{
    flex: 1;
  }}
  .timeline-period {{
    font-weight: 600;
    color: var(--text-bright);
    font-size: 0.95rem;
  }}
  .timeline-dates {{
    font-size: 0.78rem;
    color: var(--text-dim);
  }}
  .timeline-reading {{
    font-size: 0.85rem;
    color: var(--text);
    margin-top: 4px;
  }}

  .footer {{
    text-align: center;
    padding: 32px;
    font-size: 0.75rem;
    color: var(--text-dim);
    border-top: 1px solid var(--border);
    margin-top: 40px;
  }}

  @media (max-width: 768px) {{
    .chart-grid, .yoga-grid, .house-grid, .life-grid, .dasha-detail-grid {{
      grid-template-columns: 1fr;
    }}
    .header h1 {{ font-size: 1.6rem; }}
    .header-grid {{ gap: 20px; }}
  }}
{_predictions_css()}
</style>
</head>
<body>

<!-- ═══════════ HEADER ═══════════ -->
<div class="header">
  <h1>{name}</h1>
  <div class="subtitle">Vedic Birth Chart &middot; Parashari Jyotish</div>
  <div class="header-grid">
    <div class="header-item">
      <div class="label">Date</div>
      <div class="value">{date_str}</div>
    </div>
    <div class="header-item">
      <div class="label">Time</div>
      <div class="value">{time_str}</div>
    </div>
    <div class="header-item">
      <div class="label">Place</div>
      <div class="value">{b['lat']:.2f}°N, {b['lon']:.2f}°E</div>
    </div>
    <div class="header-item">
      <div class="label">Lagna</div>
      <div class="value accent">{asc['sign']} {asc['degree']:.1f}°</div>
    </div>
    <div class="header-item">
      <div class="label">Moon</div>
      <div class="value">{chart['planets']['Moon']['sign']} {chart['planets']['Moon']['degree']:.1f}°</div>
    </div>
    <div class="header-item">
      <div class="label">Nakshatra</div>
      <div class="value">{asc['nakshatra']} · Pada {asc['pada']}</div>
    </div>
    <div class="header-item">
      <div class="label">Ayanamsa</div>
      <div class="value">{chart['ayanamsa']:.4f}° (Lahiri)</div>
    </div>
  </div>
</div>

<div class="container">

<!-- ═══════════ CHARTS ═══════════ -->
<div class="section">
  <div class="section-title">Birth Charts</div>
  <div class="chart-grid">
    <div class="chart-box">
      <img src="data:image/png;base64,{d1_img}" alt="Rasi Chart">
      <div class="chart-label">Rasi (D1) — Birth Chart</div>
    </div>
    <div class="chart-box">
      <img src="data:image/png;base64,{d9_img}" alt="Navamsha Chart">
      <div class="chart-label">Navamsha (D9) — Marriage &amp; Dharma</div>
    </div>
  </div>
</div>

<!-- ═══════════ PLANETARY POSITIONS ═══════════ -->
<div class="section">
  <div class="section-title">Planetary Positions</div>
  <div class="card"><div class="table-scroll">
    <table class="data-table">
      <thead>
        <tr>
          <th>Planet</th>
          <th>Sign</th>
          <th>Degree</th>
          <th>Nakshatra</th>
          <th>Pada</th>
          <th>House</th>
          <th>Dignity</th>
          <th>Status</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td style="color: var(--accent); font-weight:600;">Lagna</td>
          <td>{asc['sign']}</td>
          <td>{asc['degree']:.1f}°</td>
          <td>{asc['nakshatra']}</td>
          <td>{asc['pada']}</td>
          <td>1</td>
          <td>—</td>
          <td>—</td>
        </tr>
{_planet_rows(chart)}
      </tbody>
    </table>
  </div></div>
</div>

<!-- ═══════════ PLANETARY STRENGTH ═══════════ -->
<div class="section">
  <div class="section-title">Planetary Strength</div>
  <div class="card">
{_strength_bars(chart)}
  </div>
</div>

<!-- ═══════════ HOUSE ANALYSIS ═══════════ -->
<div class="section">
  <div class="section-title">House Analysis</div>
  <div class="house-grid">
{_house_cards(chart)}
  </div>
</div>

<!-- ═══════════ YOGAS ═══════════ -->
<div class="section">
  <div class="section-title">Yoga Analysis — {len(yogas_list)} yoga{"s" if len(yogas_list) != 1 else ""} identified</div>
  <div class="yoga-grid">
{_yoga_cards(yogas_list)}
  </div>
</div>

<!-- ═══════════ DIVISIONAL CHARTS ═══════════ -->
<div class="section">
  <div class="section-title">Divisional Charts</div>
  <div class="chart-grid">
    <div class="chart-box">
      <img src="data:image/png;base64,{d10_img}" alt="Dasamsha Chart">
      <div class="chart-label">Dasamsha (D10) — Career</div>
    </div>
    <div class="chart-box">
      <img src="data:image/png;base64,{d7_img}" alt="Saptamsha Chart">
      <div class="chart-label">Saptamsha (D7) — Children</div>
    </div>
  </div>
{_vargottama_note(vargottama)}
{_divisional_tables(chart)}
</div>

<!-- ═══════════ DASHA TIMELINE ═══════════ -->
<div class="section">
  <div class="section-title">Vimshottari Dasha Timeline</div>
  <div class="card">
    <div style="margin-bottom:12px; font-size:0.85rem; color:var(--text-dim);">
      Moon Nakshatra: <strong style="color:var(--text-bright)">{dashas['moon_nakshatra']}</strong> &middot;
      Lord: <strong style="color:var(--text-bright)">{dashas['moon_nak_lord']}</strong> &middot;
      Balance at birth: <strong style="color:var(--text-bright)">{dashas['balance_at_birth']*100:.1f}%</strong>
    </div>
{_dasha_bar(dashas)}
{_dasha_details(dashas)}
  </div>
</div>

<!-- ═══════════ CURRENT PERIOD ═══════════ -->
{_current_period_section(chart, current_maha, current_antar)}

<!-- ═══════════ LIFE AREAS ═══════════ -->
<div class="section">
  <div class="section-title">Life Areas Reading</div>
  <div class="life-grid">
{_life_area_cards(chart)}
  </div>
</div>

<!-- ═══════════ DETAILED INTERPRETATION ═══════════ -->
{_detailed_interpretation(chart, yogas_list)}

<!-- ═══════════ PREDICTIVE TIMELINE ═══════════ -->
{_predictive_section(chart, current_maha, current_antar)}

</div>

<!-- ═══════════ COMPREHENSIVE PREDICTIONS ═══════════ -->
<div class="container">
{_render_all_predictions(pred)}
</div>

<div class="footer">
  Generated on {datetime.now().strftime('%d %B %Y at %H:%M')} &middot;
  Vedic Astrology System &middot; Parashari Jyotish &middot; Lahiri Ayanamsa
</div>

<!-- Floating Controls -->
<div id="fab-menu" style="position:fixed; bottom:20px; right:20px; z-index:1000; display:flex; flex-direction:column; align-items:flex-end; gap:8px;">
  <div id="toc-popup" style="display:none; background:var(--card); border:1px solid var(--border); border-radius:12px; padding:12px; max-height:60vh; overflow-y:auto; width:200px; box-shadow:0 8px 32px rgba(0,0,0,0.4);">
    <div id="toc-links" style="display:flex; flex-direction:column; gap:4px;"></div>
  </div>
  <div style="display:flex; gap:8px;">
    <button onclick="toggleTheme()" style="width:44px; height:44px; border-radius:50%; border:1px solid var(--border); background:var(--card); color:var(--text); font-size:1.1rem; cursor:pointer; box-shadow:0 4px 12px rgba(0,0,0,0.3);" title="Toggle theme" aria-label="Toggle theme">&#9788;</button>
    <button onclick="toggleToc()" id="toc-btn" style="width:44px; height:44px; border-radius:50%; border:1px solid var(--border); background:var(--accent); color:white; font-size:1rem; cursor:pointer; box-shadow:0 4px 12px rgba(0,0,0,0.3);" title="Sections" aria-label="Jump to section">&#9776;</button>
    <button onclick="window.scrollTo({{top:0,behavior:'smooth'}})" style="width:44px; height:44px; border-radius:50%; border:1px solid var(--border); background:var(--card); color:var(--text); font-size:1.1rem; cursor:pointer; box-shadow:0 4px 12px rgba(0,0,0,0.3);" title="Back to top" aria-label="Back to top">&#8679;</button>
  </div>
</div>

<script>
// Smooth scroll for all anchors
document.querySelectorAll('a[href^="#"]').forEach(a => {{
  a.addEventListener('click', e => {{
    e.preventDefault();
    const el = document.querySelector(a.getAttribute('href'));
    if (el) el.scrollIntoView({{ behavior: 'smooth', block: 'start' }});
  }});
}});

// Theme toggle
function toggleTheme() {{
  document.documentElement.classList.toggle('light');
  localStorage.setItem('theme', document.documentElement.classList.contains('light') ? 'light' : 'dark');
}}
if (localStorage.getItem('theme') === 'light') document.documentElement.classList.add('light');

// TOC popup
function toggleToc() {{
  const popup = document.getElementById('toc-popup');
  if (popup.style.display === 'none') {{
    // Populate links from section titles
    const links = document.getElementById('toc-links');
    links.innerHTML = '';
    document.querySelectorAll('.section-title, .pred-section .section-title').forEach(el => {{
      const section = el.closest('[id]') || el.closest('.section') || el.closest('.pred-section');
      if (section) {{
        const id = section.id || '';
        const a = document.createElement('a');
        a.href = '#' + id;
        a.textContent = el.textContent;
        a.style.cssText = 'font-size:0.82rem; color:var(--text); text-decoration:none; padding:6px 8px; border-radius:6px; display:block;';
        a.onmouseover = function() {{ this.style.background = 'var(--accent-soft)'; }};
        a.onmouseout = function() {{ this.style.background = 'none'; }};
        a.onclick = function() {{ popup.style.display = 'none'; }};
        links.appendChild(a);
      }}
    }});
    popup.style.display = 'block';
  }} else {{
    popup.style.display = 'none';
  }}
}}

// Close TOC on outside click
document.addEventListener('click', e => {{
  const menu = document.getElementById('fab-menu');
  if (!menu.contains(e.target)) document.getElementById('toc-popup').style.display = 'none';
}});
</script>

</body>
</html>"""

    if output_path:
        with open(output_path, 'w') as f:
            f.write(html)

    return html


# ── Helper functions for HTML generation ──────────────────────

def _planet_rows(chart):
    rows = []
    for name in PLANETS:
        p = chart['planets'][name]
        pc = planet_class(name)
        dc = dignity_class(p['dignity'])

        tags = []
        if p['is_retrograde']:
            tags.append('<span class="tag tag-retro">R</span>')
        if p.get('is_combust'):
            tags.append('<span class="tag tag-combust">C</span>')
        tags_html = ' '.join(tags) if tags else '—'

        rows.append(f"""        <tr>
          <td class="{pc}" style="font-weight:600;">{PLANET_ABBR[name]} {name}</td>
          <td>{p['sign']}</td>
          <td>{p['degree']:.1f}°</td>
          <td>{p['nakshatra']}</td>
          <td>{p['pada']}</td>
          <td>{p['house']}</td>
          <td class="{dc}">{p['dignity']}</td>
          <td>{tags_html}</td>
        </tr>""")
    return '\n'.join(rows)


def _strength_bars(chart):
    rows = []
    for name in PLANETS:
        p = chart['planets'][name]
        # Calculate a simple strength score 0-100
        score = 50  # base
        if p['dignity'] == 'Exalted':
            score += 35
        elif p['dignity'] == 'Moolatrikona':
            score += 28
        elif p['dignity'] == 'Own Sign':
            score += 22
        elif p['dignity'] == 'Friendly':
            score += 10
        elif p['dignity'] == 'Enemy':
            score -= 15
        elif p['dignity'] == 'Debilitated':
            score -= 30
        if p['house'] in (1, 4, 7, 10):
            score += 12
        elif p['house'] in (5, 9):
            score += 10
        elif p['house'] in (6, 8, 12):
            score -= 12
        if p.get('is_combust'):
            score -= 15
        if name in DIG_BALA and p['house'] == DIG_BALA[name]:
            score += 10
        score = max(5, min(95, score))

        if score >= 65:
            color = 'var(--green)'
        elif score >= 45:
            color = 'var(--gold)'
        else:
            color = 'var(--accent)'

        pc = planet_class(name)
        label = p['dignity']

        rows.append(f"""    <div class="strength-row">
      <div class="strength-name {pc}">{PLANET_ABBR[name]} {name}</div>
      <div class="strength-bar-bg">
        <div class="strength-bar" style="width:{score}%; background:{color};"></div>
      </div>
      <div class="strength-label">{label}</div>
    </div>""")
    return '\n'.join(rows)


def _house_cards(chart):
    cards = []
    for h in range(1, 13):
        hd = chart['houses'][h]
        sig = HOUSE_SIGNIFICATIONS.get(h, '')
        occupants = hd['occupants']
        lord = hd['lord']
        lord_data = chart['planets'][lord]

        occ_html = ''
        if occupants:
            occ_parts = []
            for o in occupants:
                pc = planet_class(o)
                occ_parts.append(f'<span class="{pc}" style="font-weight:500;">{o}</span>')
            occ_html = f'<div class="house-occupants">{", ".join(occ_parts)}</div>'
        else:
            occ_html = '<div class="house-occupants" style="color:var(--text-dim); font-style:italic;">Empty</div>'

        cards.append(f"""    <div class="house-card">
      <div class="house-num">House {h}</div>
      <div class="house-sign">{hd['sign']}</div>
      <div class="house-detail">Lord: <strong style="color:var(--text-bright)">{lord}</strong> in H{hd['lord_house']} ({lord_data['sign']}, <span class="{dignity_class(lord_data['dignity'])}">{lord_data['dignity']}</span>)</div>
      {occ_html}
      <div class="house-detail" style="margin-top:6px; font-size:0.78rem;">{sig}</div>
    </div>""")
    return '\n'.join(cards)


def _yoga_cards(yogas_list):
    cards = []
    for y in yogas_list:
        ytype = y['type']
        card_class = 'positive'
        if 'Challenging' in ytype or 'Negative' in ytype:
            card_class = 'challenging'

        strength = y['strength']
        sc = 'strength-strong' if strength in ('Strong', 'Very Strong') else \
             'strength-moderate' if strength == 'Moderate' else 'strength-weak'

        planets_str = ', '.join(y['planets'])

        cards.append(f"""    <div class="yoga-card {card_class}">
      <div class="yoga-name">{y['name']} <span class="yoga-strength {sc}">{strength}</span></div>
      <div class="yoga-planets">{planets_str} &middot; {ytype}</div>
      <div class="yoga-effect">{y['effect']}</div>
    </div>""")
    return '\n'.join(cards)


def _vargottama_note(vargottama):
    if not vargottama:
        return ''
    names = ', '.join(vargottama)
    return f"""  <div class="card" style="margin-top:16px;">
    <span class="tag tag-vargottama" style="margin-right:8px;">Vargottama</span>
    <strong>{names}</strong> — same sign in D1 and D9. These planets give consistent, reliable results.
  </div>"""


def _divisional_tables(chart):
    html = '<div style="display:grid; grid-template-columns:repeat(auto-fit, minmax(280px, 1fr)); gap:16px; margin-top:16px;">'
    for key, label in [('D9', 'Navamsha (D9)'), ('D10', 'Dasamsha (D10)')]:
        div = chart['divisional'][key]
        html += f'<div class="card card-alt"><strong style="color:var(--accent); font-size:0.8rem;">{label}</strong>'
        html += f'<div style="font-size:0.8rem; color:var(--text-dim); margin:6px 0;">Lagna: {div["ascendant"]["sign"]}</div>'
        html += '<div class="table-scroll"><table class="data-table" style="font-size:0.82rem;">'
        html += '<tr><th>Planet</th><th>Sign</th><th>House</th><th>Lord</th></tr>'
        for name in PLANETS:
            d = div[name]
            pc = planet_class(name)
            html += f'<tr><td class="{pc}">{PLANET_ABBR[name]} {name}</td><td>{d["sign"]}</td><td>{d["house"]}</td><td>{d["lord"]}</td></tr>'
        html += '</table></div></div>'
    html += '</div>'
    return html


DASHA_COLORS = {
    'Sun': '#FF6B35', 'Moon': '#9e9e9e', 'Mars': '#DC143C',
    'Mercury': '#00CC66', 'Jupiter': '#DAA520', 'Venus': '#FF69B4',
    'Saturn': '#4169E1', 'Rahu': '#8B5E3C', 'Ketu': '#9370DB',
}


def _dasha_bar(dashas):
    now = datetime.now(dashas['dashas'][0]['start'].tzinfo)
    relevant = [d for d in dashas['dashas']
                if d['end'].year >= (now.year - 20) and d['start'].year <= (now.year + 30)]
    if not relevant:
        relevant = dashas['dashas'][:9]

    total = sum((d['end'] - d['start']).total_seconds() for d in relevant)

    segments = []
    for d in relevant:
        dur = (d['end'] - d['start']).total_seconds()
        pct = (dur / total) * 100
        color = DASHA_COLORS.get(d['lord'], '#666')
        is_current = d.get('is_current')
        is_past = d['end'] < now

        cls = 'current' if is_current else ('past' if is_past else '')
        label = f"{d['lord']}" if pct > 4 else ''

        segments.append(
            f'<div class="dasha-segment {cls}" style="width:{pct:.1f}%; background:{color};">'
            f'<span>{label}</span></div>'
        )

    return f'    <div class="dasha-bar">{"".join(segments)}</div>'


def _dasha_details(dashas):
    now = datetime.now(dashas['dashas'][0]['start'].tzinfo)
    relevant = [d for d in dashas['dashas']
                if d['end'].year >= (now.year - 5) and d['start'].year <= (now.year + 40)]
    if not relevant:
        relevant = dashas['dashas'][:9]

    items = []
    for d in relevant[:9]:
        is_current = d.get('is_current')
        is_past = d['end'] < now
        cls = 'active' if is_current else ''
        opacity = 'opacity:0.5;' if is_past else ''
        color = DASHA_COLORS.get(d['lord'], '#666')

        items.append(f"""      <div class="dasha-detail {cls}" style="{opacity}">
        <div style="display:flex; align-items:center; gap:6px;">
          <span style="width:10px; height:10px; border-radius:2px; background:{color}; display:inline-block;"></span>
          <span class="dasha-lord">{d['lord']}</span>
          <span style="font-size:0.75rem; color:var(--text-dim);">{d['years']:.1f}y</span>
        </div>
        <div class="dasha-dates">{d['start'].strftime('%b %Y')} — {d['end'].strftime('%b %Y')}</div>
      </div>""")
    return f'    <div class="dasha-detail-grid">\n{"".join(items)}\n    </div>'


def _current_period_section(chart, current_maha, current_antar):
    if not current_maha:
        return ''

    lord = current_maha['lord']
    p = chart['planets'][lord]
    themes = KARAKAS.get(lord, '')

    antar_html = ''
    if current_antar:
        al = current_antar['lord']
        ap = chart['planets'][al]
        antar_html = f"""
    <div class="card card-alt" style="margin-top:12px;">
      <div style="font-size:0.75rem; color:var(--accent); text-transform:uppercase; letter-spacing:2px; margin-bottom:8px;">Current Antardasha</div>
      <div style="font-size:1.1rem; font-weight:600; color:var(--text-bright);">{al}</div>
      <div style="font-size:0.85rem; color:var(--text-dim); margin-top:4px;">
        {current_antar['start'].strftime('%d %b %Y')} — {current_antar['end'].strftime('%d %b %Y')}
      </div>
      <div style="font-size:0.85rem; margin-top:8px;">
        {al} in {ap['sign']} (House {ap['house']}), {ap['dignity']}.
        Themes: {KARAKAS.get(al, '').split(',')[0].strip().lower()}.
      </div>
    </div>"""

    return f"""<div class="section">
  <div class="section-title">Current Period</div>
  <div class="card">
    <div style="display:flex; align-items:center; gap:12px; margin-bottom:12px;">
      <span style="width:16px; height:16px; border-radius:3px; background:{DASHA_COLORS.get(lord, '#666')}; display:inline-block;"></span>
      <span style="font-size:1.3rem; font-weight:600; color:var(--text-bright);">{lord} Mahadasha</span>
    </div>
    <div style="font-size:0.85rem; color:var(--text-dim); margin-bottom:8px;">
      {current_maha['start'].strftime('%d %b %Y')} — {current_maha['end'].strftime('%d %b %Y')}
    </div>
    <div style="font-size:0.9rem; line-height:1.7;">
      {lord} is in <strong>{p['sign']}</strong> (House {p['house']}), <span class="{dignity_class(p['dignity'])}">{p['dignity']}</span>.
      Nakshatra: {p['nakshatra']}, Pada {p['pada']}.<br>
      This period activates themes of <em>{themes.lower()}</em>.
      House {p['house']} matters ({HOUSE_SIGNIFICATIONS.get(p['house'], '').split(',')[0].strip().lower()}) will be prominent.
    </div>
    {antar_html}
  </div>
</div>"""


def _life_area_cards(chart):
    cards = []

    # Career
    h10 = chart['houses'][10]
    l10 = h10['lord']
    l10_d = chart['planets'][l10]
    career_signs = {
        'Aries': 'Leadership, military, sports, surgery, engineering',
        'Taurus': 'Finance, agriculture, luxury goods, hospitality, art',
        'Gemini': 'Communication, writing, media, trading, teaching',
        'Cancer': 'Nurturing professions, hospitality, real estate',
        'Leo': 'Government, politics, entertainment, management',
        'Virgo': 'Healthcare, accounting, analysis, editing, service',
        'Libra': 'Law, diplomacy, fashion, beauty, partnerships',
        'Scorpio': 'Research, investigation, medicine, occult, insurance',
        'Sagittarius': 'Education, philosophy, law, religion, foreign trade',
        'Capricorn': 'Administration, manufacturing, traditional business',
        'Aquarius': 'Technology, social work, innovation, science',
        'Pisces': 'Healing, arts, spirituality, film, photography',
    }
    occ10 = ', '.join(h10['occupants']) if h10['occupants'] else 'None'
    cards.append(f"""    <div class="life-card">
      <h3>Career &amp; Profession</h3>
      <div class="life-detail">10th House: <strong>{h10['sign']}</strong></div>
      <div class="life-detail">Lord: <strong>{l10}</strong> in H{h10['lord_house']} (<span class="{dignity_class(l10_d['dignity'])}">{l10_d['dignity']}</span>)</div>
      <div class="life-detail">Planets in 10th: {occ10}</div>
      <div class="life-reading">{career_signs.get(h10['sign'], 'Various fields')}</div>
    </div>""")

    # Marriage
    h7 = chart['houses'][7]
    l7 = h7['lord']
    l7_d = chart['planets'][l7]
    venus = chart['planets']['Venus']
    occ7 = ', '.join(h7['occupants']) if h7['occupants'] else 'None'
    cards.append(f"""    <div class="life-card">
      <h3>Marriage &amp; Partnerships</h3>
      <div class="life-detail">7th House: <strong>{h7['sign']}</strong></div>
      <div class="life-detail">Lord: <strong>{l7}</strong> in H{h7['lord_house']} (<span class="{dignity_class(l7_d['dignity'])}">{l7_d['dignity']}</span>)</div>
      <div class="life-detail">Planets in 7th: {occ7}</div>
      <div class="life-detail">Venus: {venus['sign']} (H{venus['house']}, <span class="{dignity_class(venus['dignity'])}">{venus['dignity']}</span>)</div>
    </div>""")

    # Wealth
    h2 = chart['houses'][2]
    h11 = chart['houses'][11]
    cards.append(f"""    <div class="life-card">
      <h3>Wealth &amp; Finances</h3>
      <div class="life-detail">2nd House: <strong>{h2['sign']}</strong> — Lord: {h2['lord']} in H{h2['lord_house']}</div>
      <div class="life-detail">11th House: <strong>{h11['sign']}</strong> — Lord: {h11['lord']} in H{h11['lord_house']}</div>
      <div class="life-reading">2nd house (stored wealth) and 11th house (gains) determine financial trajectory.</div>
    </div>""")

    # Health
    h6 = chart['houses'][6]
    occ6 = ', '.join(h6['occupants']) if h6['occupants'] else 'None'
    health_areas = {
        'Aries': 'Head, brain, blood pressure', 'Taurus': 'Throat, thyroid, neck',
        'Gemini': 'Lungs, arms, nervous system', 'Cancer': 'Stomach, chest, digestion',
        'Leo': 'Heart, spine, circulation', 'Virgo': 'Intestines, digestion, nerves',
        'Libra': 'Kidneys, lower back, skin', 'Scorpio': 'Reproductive system, chronic conditions',
        'Sagittarius': 'Hips, liver, thighs', 'Capricorn': 'Knees, bones, joints',
        'Aquarius': 'Ankles, circulation, nervous disorders', 'Pisces': 'Feet, lymphatic, immunity',
    }
    asc_sign = chart['ascendant']['sign']
    cards.append(f"""    <div class="life-card">
      <h3>Health</h3>
      <div class="life-detail">Lagna: <strong>{asc_sign}</strong></div>
      <div class="life-detail">6th House: {h6['sign']} — Lord: {h6['lord']} in H{h6['lord_house']}</div>
      <div class="life-detail">Planets in 6th: {occ6}</div>
      <div class="life-reading">Watch areas: {health_areas.get(asc_sign, 'General')}</div>
    </div>""")

    return '\n'.join(cards)


def _predictive_section(chart, current_maha, current_antar):
    if not current_maha:
        return ''

    dashas = chart['dashas']
    planets = chart['planets']
    items = []

    def _period_reading(maha_lord, antar_lord):
        """Generate a rich reading for a Maha-Antar period."""
        mp = planets[maha_lord]
        ap = planets[antar_lord]
        houses_active = sorted(set([mp['house'], ap['house']]))
        h_str = ', '.join(str(h) for h in houses_active)

        is_friend = antar_lord in NATURAL_FRIENDS.get(maha_lord, [])
        is_enemy = antar_lord in NATURAL_ENEMIES.get(maha_lord, [])

        quality_word = 'supportive' if is_friend else ('challenging' if is_enemy else 'neutral')
        quality_detail = ''
        if is_friend:
            quality_detail = f'{maha_lord} and {antar_lord} are natural friends. Energy flows harmoniously.'
        elif is_enemy:
            quality_detail = f'{maha_lord} and {antar_lord} are natural enemies. Internal tension drives growth through difficulty.'
        else:
            quality_detail = f'{maha_lord} and {antar_lord} have a neutral relationship. Results depend on house placements.'

        # What houses activate
        house_themes = []
        for h in houses_active:
            sig = HOUSE_SIGNIFICATIONS.get(h, '')
            if sig:
                house_themes.append(f'House {h} ({sig.split(",")[0].strip()})')

        # Antar lord dignity
        antar_dignity = ap['dignity']
        dignity_note = ''
        if antar_dignity in ('Exalted', 'Own Sign'):
            dignity_note = f'{antar_lord} is strong ({antar_dignity}), expect positive outcomes.'
        elif antar_dignity in ('Debilitated', 'Enemy'):
            dignity_note = f'{antar_lord} is weak ({antar_dignity}), requiring extra effort.'

        reading = f'{quality_detail} Life areas: {", ".join(house_themes)}. '
        reading += f'{antar_lord} brings themes of {KARAKAS.get(antar_lord, "general life matters").lower()}. '
        if dignity_note:
            reading += dignity_note

        return reading, quality_word

    # Current period
    if current_antar:
        al = current_antar['lord']
        reading, quality = _period_reading(current_maha['lord'], al)
        items.append(f"""    <div class="timeline-item active">
      <div class="timeline-content">
        <div class="timeline-period">{current_maha['lord']}-{al} <span style="color:var(--accent);">(Now)</span></div>
        <div class="timeline-dates">{current_antar['start'].strftime('%b %Y')} — {current_antar['end'].strftime('%b %Y')}</div>
        <div class="timeline-reading">{reading}</div>
      </div>
    </div>""")

    # ALL remaining antardashas in current mahadasha
    found = False
    for ad in current_maha['antardashas']:
        if ad.get('is_current'):
            found = True
            continue
        if found:
            al = ad['lord']
            reading, quality = _period_reading(current_maha['lord'], al)
            color = 'var(--green)' if quality == 'supportive' else ('var(--accent)' if quality == 'challenging' else 'var(--text-dim)')
            items.append(f"""    <div class="timeline-item">
      <div class="timeline-content">
        <div class="timeline-period">{current_maha['lord']}-{al} <span style="font-size:0.75rem; color:{color};">({quality})</span></div>
        <div class="timeline-dates">{ad['start'].strftime('%b %Y')} — {ad['end'].strftime('%b %Y')}</div>
        <div class="timeline-reading">{reading}</div>
      </div>
    </div>""")

    # Next 2 Mahadashas with full descriptions
    found_maha = False
    maha_count = 0
    for d in dashas['dashas']:
        if d.get('is_current'):
            found_maha = True
            continue
        if found_maha and maha_count < 2:
            p = planets[d['lord']]
            lord = d['lord']
            themes = KARAKAS.get(lord, '')
            dignity = p['dignity']
            house = p['house']
            h_sig = HOUSE_SIGNIFICATIONS.get(house, '')

            # Rich description of upcoming mahadasha
            strength_note = ''
            if dignity in ('Exalted', 'Own Sign', 'Moolatrikona'):
                strength_note = f'{lord} is <strong>{dignity}</strong> — this will be a powerful, productive period.'
            elif dignity in ('Debilitated', 'Enemy'):
                strength_note = f'{lord} is in {dignity} dignity — this period will test and ultimately strengthen you.'
            else:
                strength_note = f'{lord} in {dignity} dignity gives moderate, steady results.'

            reading = f'{lord} activates House {house} ({h_sig.split(",")[0].strip() if h_sig else "general"} matters). '
            reading += f'Themes: {themes.lower()}. {strength_note}'

            items.append(f"""    <div class="timeline-item">
      <div class="timeline-content">
        <div class="timeline-period" style="color:var(--accent);">{"Next" if maha_count == 0 else "Following"} Mahadasha: {lord} ({d['years']:.0f} years)</div>
        <div class="timeline-dates">{d['start'].strftime('%b %Y')} — {d['end'].strftime('%b %Y')}</div>
        <div class="timeline-reading">{reading}</div>
      </div>
    </div>""")
            maha_count += 1

    return f"""<div class="section">
  <div class="section-title">Predictive Timeline — Detailed Period-by-Period</div>
  <div class="card">
    <div style="margin-bottom:16px; font-size:0.85rem; color:var(--text-dim);">
      Each period activates specific life areas based on the Mahadasha and Antardasha lords' placements.
      Friendly planet combinations tend to give smoother results; enemy combinations create growth through friction.
    </div>
{"".join(items)}
  </div>
</div>"""


# ── Detailed Interpretation ───────────────────────────────────

def _detailed_interpretation(chart, yogas_list):
    """Generate rich textual analysis — personality, strengths, life themes."""
    asc = chart['ascendant']
    planets = chart['planets']
    houses = chart['houses']
    d9 = chart['divisional']['D9']

    sections = []

    # ── 1. PERSONALITY & CORE NATURE ──
    asc_sign = asc['sign']
    asc_lord = asc['lord']
    asc_lord_data = planets[asc_lord]
    moon = planets['Moon']
    sun = planets['Sun']

    asc_desc = {
        'Aries': 'pioneering spirit, independence, and natural leadership. Direct, action-oriented, and competitive.',
        'Taurus': 'stability, sensuality, and determination. Values comfort, beauty, and material security above all.',
        'Gemini': 'curiosity, adaptability, and communication. Quick-minded, versatile, but can scatter energy.',
        'Cancer': 'deep nurturing instinct, emotional intelligence, and attachment to home. Protective and intuitive.',
        'Leo': 'confidence, generosity, and dramatic self-expression. Natural authority with creative flair.',
        'Virgo': 'analytical precision, practical service, and attention to detail. Health-conscious and discerning.',
        'Libra': 'diplomacy, aesthetic sense, and partnership orientation. Seeks balance, fairness, and beauty.',
        'Scorpio': 'intense depth, transformative power, and psychological insight. Secretive but fiercely loyal.',
        'Sagittarius': 'philosophical outlook, adventurous spirit, and optimism. Seeker of truth, meaning, and higher knowledge. Naturally drawn to teaching, travel, and expanding horizons.',
        'Capricorn': 'ambition, discipline, and responsible pragmatism. Steady climb toward lasting achievement.',
        'Aquarius': 'innovative thinking, humanitarian ideals, and independence. Unconventional approach to life.',
        'Pisces': 'spiritual depth, compassion, and vivid imagination. Connected to the transcendent and artistic.',
    }

    moon_desc = {
        'Aries': 'emotionally assertive and quick to react. Needs independence and action to feel alive.',
        'Taurus': 'emotionally stable, sensual, and comfort-seeking. Needs beauty, nature, and material security for peace of mind.',
        'Gemini': 'emotionally restless and intellectually stimulated. Needs variety, conversation, and mental engagement.',
        'Cancer': 'deeply emotional, nurturing, and home-oriented. Strong mother connection and protective instincts.',
        'Leo': 'emotionally warm, dramatic, and needs recognition. Creative expression feeds the soul.',
        'Virgo': 'emotionally reserved, analytical, and service-oriented. Finds peace in order and usefulness.',
        'Libra': 'emotionally diplomatic, relationship-focused. Needs harmony and partnership for emotional balance.',
        'Scorpio': 'emotionally intense, private, and transformative. Deep inner world with powerful intuition.',
        'Sagittarius': 'emotionally optimistic, freedom-loving. Needs adventure and philosophical meaning.',
        'Capricorn': 'emotionally restrained, responsible. Finds security through achievement and structure.',
        'Aquarius': 'emotionally detached but humanitarian. Needs intellectual stimulation and social cause.',
        'Pisces': 'emotionally boundless, empathetic, and spiritually inclined. Absorbs others\' emotions.',
    }

    lagna_lord_house_reading = {
        1: 'gives a strong, self-defined personality. You lead from the front and your identity is clear to the world.',
        2: 'ties your identity to wealth, family values, and speech. Financial matters and family lineage are central life themes.',
        3: 'channels your energy into communication, courage, and self-effort. Siblings and short travels play a role in self-development.',
        4: 'roots your being in home, mother, and emotional security. Education and domestic happiness are foundational.',
        5: 'links your identity to creativity, children, and past-life merit. Naturally intelligent with a flair for self-expression.',
        6: 'channels your energy into overcoming obstacles, service, and competition. You grow through challenges.',
        7: 'makes partnerships the defining theme of your life. Your spouse or business partner significantly shapes your journey.',
        8: 'brings transformation, research, and hidden matters into focus. Life has sudden turns that ultimately deepen you.',
        9: 'blesses life with dharma, fortune, and higher learning. Father figure and philosophical quest are important.',
        10: 'makes career and public status the central purpose. Achievement and recognition drive your life.',
        11: 'connects your identity to social networks, gains, and aspirations. Desires tend to manifest.',
        12: 'gives a spiritual or foreign orientation. You may live away from your birthplace or gravitate toward isolation and inner work.',
    }

    personality = f"""
    <p>{asc_sign} rising gives you {asc_desc.get(asc_sign, '')}</p>
    <p>Your lagna lord <strong>{asc_lord}</strong> sits in <strong>{asc_lord_data['sign']}</strong>
    (House {asc_lord_data['house']}), which is <span class="{dignity_class(asc_lord_data['dignity'])}">{asc_lord_data['dignity'].lower()}</span> dignity.
    The lagna lord in House {asc_lord_data['house']} {lagna_lord_house_reading.get(asc_lord_data['house'], '')}</p>
    <p>Your Moon in <strong>{moon['sign']}</strong> ({moon['nakshatra']}, Pada {moon['pada']}) reveals your emotional nature:
    {moon_desc.get(moon['sign'], '')}
    {'Moon is <strong>exalted</strong> here, giving exceptional emotional strength and inner stability.' if moon['dignity'] == 'Exalted' else ''}
    {'Moon is <strong>debilitated</strong>, suggesting emotional challenges that become wisdom over time.' if moon['dignity'] == 'Debilitated' else ''}</p>
    <p>Sun in <strong>{sun['sign']}</strong> (House {sun['house']}) defines your soul nature and public identity.
    {'<strong>Exalted Sun</strong> gives a powerful sense of self, natural authority, and leadership ability. Father is a positive influence.' if sun['dignity'] == 'Exalted' else ''}
    {'Sun is debilitated, suggesting ego and authority lessons. Relationship with father may be complex.' if sun['dignity'] == 'Debilitated' else ''}</p>"""

    sections.append(('Personality & Core Nature', personality))

    # ── 2. KEY STRENGTHS ──
    strong_planets = [n for n in PLANETS if planets[n]['dignity'] in ('Exalted', 'Own Sign', 'Moolatrikona')]
    kendra_planets = [n for n in PLANETS if _is_kendra_h(planets[n]['house'])]
    trikona_planets = [n for n in PLANETS if planets[n]['house'] in (5, 9)]

    strengths_text = '<ul style="margin:8px 0; padding-left:20px;">'
    for p_name in strong_planets:
        p = planets[p_name]
        strengths_text += f'<li><strong class="{planet_class(p_name)}">{p_name}</strong> is <span class="{dignity_class(p["dignity"])}">{p["dignity"]}</span> in {p["sign"]} (House {p["house"]}). {KARAKAS.get(p_name, "").split(",")[0].strip()} themes are powerfully supported.</li>'
    if not strong_planets:
        strengths_text += '<li>No planets in exaltation or own sign. Strength comes from house placement and aspects.</li>'
    strengths_text += '</ul>'

    # Yogas summary
    positive_yogas = [y for y in yogas_list if y['type'] not in ('Challenging', 'Negative', 'Dosha', 'Cancelled Negative')]
    if positive_yogas:
        strengths_text += '<p style="margin-top:12px;">Your chart carries <strong>' + str(len(positive_yogas)) + ' positive yogas</strong>, indicating:'
        strengths_text += '<ul style="margin:8px 0; padding-left:20px;">'
        raj_count = sum(1 for y in positive_yogas if 'Raj' in y['type'])
        dhana_count = sum(1 for y in positive_yogas if 'Dhana' in y['type'])
        if raj_count:
            strengths_text += f'<li>{raj_count} Raj Yoga(s) — potential for power, status, and leadership</li>'
        if dhana_count:
            strengths_text += f'<li>{dhana_count} Dhana Yoga(s) — wealth accumulation and financial growth</li>'
        for y in positive_yogas:
            if 'Raj' not in y['type'] and 'Dhana' not in y['type']:
                strengths_text += f'<li>{y["name"]} — {y["effect"].split(".")[0]}.</li>'
        strengths_text += '</ul></p>'

    sections.append(('Key Strengths', strengths_text))

    # ── 3. CHALLENGES & GROWTH AREAS ──
    weak_planets = [n for n in PLANETS if planets[n]['dignity'] in ('Debilitated', 'Enemy')]
    dusthana_planets_list = [n for n in PLANETS if planets[n]['house'] in (6, 8, 12) and n not in ('Rahu', 'Ketu')]
    combust_planets = [n for n in PLANETS if planets[n].get('is_combust')]
    retro_planets = [n for n in PLANETS if planets[n]['is_retrograde'] and n not in ('Rahu', 'Ketu')]

    challenges_text = '<ul style="margin:8px 0; padding-left:20px;">'
    for p_name in weak_planets:
        p = planets[p_name]
        challenges_text += f'<li><strong>{p_name}</strong> in <span class="{dignity_class(p["dignity"])}">{p["dignity"]}</span> sign ({p["sign"]}, House {p["house"]}). {KARAKAS.get(p_name, "").split(",")[0].strip()} themes need conscious effort.</li>'
    for p_name in dusthana_planets_list:
        if p_name not in weak_planets:
            p = planets[p_name]
            challenges_text += f'<li><strong>{p_name}</strong> in dusthana House {p["house"]}. {KARAKAS.get(p_name, "").split(",")[0].strip()} themes face obstacles that build resilience.</li>'
    for p_name in combust_planets:
        challenges_text += f'<li><strong>{p_name}</strong> is combust (too close to Sun). Its significations are overshadowed by ego/authority themes.</li>'
    for p_name in retro_planets:
        p = planets[p_name]
        challenges_text += f'<li><strong>{p_name}</strong> is retrograde in House {p["house"]}. Its energy is internalized — results come after delay and introspection.</li>'
    negative_y = [y for y in yogas_list if y['type'] in ('Challenging', 'Negative', 'Dosha')]
    for y in negative_y:
        challenges_text += f'<li><strong>{y["name"]}</strong>: {y["effect"]}</li>'
    if not weak_planets and not dusthana_planets_list and not combust_planets and not negative_y:
        challenges_text += '<li>No major afflictions. Chart has good overall balance.</li>'
    challenges_text += '</ul>'

    sections.append(('Challenges & Growth Areas', challenges_text))

    # ── 4. MARRIAGE & RELATIONSHIPS ──
    h7 = houses[7]
    l7 = h7['lord']
    l7_data = planets[l7]
    venus = planets['Venus']
    jupiter = planets['Jupiter']
    d9_7_sign_idx = (d9['ascendant']['sign_idx'] + 6) % 12

    marriage_text = f"""
    <p>The 7th house ({h7['sign']}) governs marriage and partnerships, with its lord <strong>{l7}</strong>
    in {l7_data['sign']} (House {l7_data['house']}, <span class="{dignity_class(l7_data['dignity'])}">{l7_data['dignity']}</span>).</p>"""

    if h7['occupants']:
        occ = ', '.join(f'<strong>{o}</strong>' for o in h7['occupants'])
        marriage_text += f'<p>Planets in 7th house: {occ}. '
        for o in h7['occupants']:
            if o == 'Jupiter':
                marriage_text += 'Jupiter in 7th is excellent — brings a wise, supportive spouse. Marriage is a source of growth. '
            elif o == 'Venus':
                marriage_text += 'Venus in 7th blesses with an attractive, loving partner and harmonious relationships. '
            elif o == 'Saturn':
                marriage_text += 'Saturn in 7th delays marriage but gives a mature, committed partner. Relationship improves with age. '
            elif o == 'Mars':
                marriage_text += 'Mars in 7th brings passion but also conflict in partnerships. Manglik consideration applies. '
            elif o == 'Rahu':
                marriage_text += 'Rahu in 7th may attract unconventional or foreign partners. Marriage can have unexpected dimensions. '
            elif o == 'Ketu':
                marriage_text += 'Ketu in 7th can create detachment in partnerships. Past-life karmic connections with spouse. '
        marriage_text += '</p>'

    marriage_text += f"""<p>Venus ({venus['sign']}, House {venus['house']}, <span class="{dignity_class(venus['dignity'])}">{venus['dignity']}</span>)
    is the natural significator of marriage. {'Venus is well-placed, supporting romantic happiness.' if venus['dignity'] in ('Exalted', 'Own Sign', 'Friendly') else 'Venus needs support from aspects and dashas for relationship harmony.'}</p>
    <p>In the Navamsha (D9), the 7th sign is <strong>{SIGNS[d9_7_sign_idx]}</strong>, suggesting
    the spouse's nature will carry {SIGNS[d9_7_sign_idx]} qualities.</p>"""

    sections.append(('Marriage & Relationships', marriage_text))

    # ── 5. CAREER & PURPOSE ──
    h10 = houses[10]
    l10 = h10['lord']
    l10_data = planets[l10]
    h10_sign = h10['sign']

    career_text = f"""
    <p>The 10th house in <strong>{h10_sign}</strong> sets the tone for career.
    Its lord <strong>{l10}</strong> sits in {l10_data['sign']} (House {l10_data['house']},
    <span class="{dignity_class(l10_data['dignity'])}">{l10_data['dignity']}</span>).</p>"""

    career_fields = {
        'Aries': 'Leadership, military, sports, surgery, engineering, entrepreneurship.',
        'Taurus': 'Finance, agriculture, luxury goods, hospitality, art, banking.',
        'Gemini': 'Communication, writing, media, trading, teaching, marketing.',
        'Cancer': 'Nurturing professions, hospitality, real estate, public dealing, counseling.',
        'Leo': 'Government, politics, entertainment, management, creative direction.',
        'Virgo': 'Healthcare, accounting, analysis, editing, IT, service industry.',
        'Libra': 'Law, diplomacy, fashion, beauty, partnerships, design.',
        'Scorpio': 'Research, investigation, psychology, medicine, insurance, occult.',
        'Sagittarius': 'Education, philosophy, law, religion, foreign trade, publishing.',
        'Capricorn': 'Administration, manufacturing, traditional business, government.',
        'Aquarius': 'Technology, social work, innovation, networking, science, startups.',
        'Pisces': 'Healing, arts, spirituality, charity, film, photography, music.',
    }

    career_text += f'<p><strong>Natural career fields:</strong> {career_fields.get(h10_sign, "")}</p>'

    if h10['occupants']:
        career_text += f'<p>Planets in 10th: <strong>{", ".join(h10["occupants"])}</strong> — these planets directly influence career visibility and nature.</p>'

    # 10th lord placement
    career_text += f'<p>10th lord in House {l10_data["house"]} suggests career success through '
    h_themes = {1: 'personal brand and self-effort', 2: 'wealth management, family business, or speech-related work',
                3: 'communication, media, courage, and self-enterprise', 4: 'real estate, education, or homeland-connected work',
                5: 'creativity, speculation, teaching, or advisory roles', 6: 'service, healthcare, competition, or legal work',
                7: 'partnerships, client-facing roles, or business collaborations', 8: 'research, transformation, insurance, or hidden knowledge',
                9: 'higher education, international work, or dharmic/philosophical fields', 10: 'direct public achievement and strong career focus',
                11: 'networking, social circles, technology, and gains-oriented work', 12: 'foreign lands, spiritual work, hospitals, or behind-the-scenes roles'}
    career_text += f'{h_themes.get(l10_data["house"], "various fields")}.</p>'

    # D10 note
    d10 = chart['divisional']['D10']
    d10_asc = d10['ascendant']['sign']
    career_text += f'<p>D10 (career chart) Lagna is <strong>{d10_asc}</strong>, which further refines career direction toward {career_fields.get(d10_asc, d10_asc + " related fields")}.</p>'

    sections.append(('Career & Professional Life', career_text))

    # ── 6. WEALTH & FINANCES ──
    h2 = houses[2]
    h11 = houses[11]
    l2 = h2['lord']
    l2_data = planets[l2]
    l11 = h11['lord']
    l11_data = planets[l11]

    wealth_text = f"""
    <p>2nd house ({h2['sign']}) represents stored wealth, with lord <strong>{l2}</strong> in
    {l2_data['sign']} (House {l2_data['house']}, <span class="{dignity_class(l2_data['dignity'])}">{l2_data['dignity']}</span>).
    {'<strong>' + l2 + ' in its own house gives excellent wealth stability.</strong>' if l2_data['house'] == 2 and l2_data['dignity'] in ('Own Sign', 'Exalted') else ''}</p>
    <p>11th house ({h11['sign']}) represents gains and income, with lord <strong>{l11}</strong> in
    House {l11_data['house']} ({l11_data['dignity']}).</p>"""

    dhana_yogas_found = [y for y in yogas_list if 'Dhana' in y['type']]
    if dhana_yogas_found:
        wealth_text += '<p><strong>Dhana Yogas active:</strong></p><ul style="padding-left:20px;">'
        for dy in dhana_yogas_found:
            wealth_text += f'<li>{dy["name"]}: {dy["effect"].split(".")[0]}.</li>'
        wealth_text += '</ul>'

    sections.append(('Wealth & Finances', wealth_text))

    # ── 7. NAVAMSHA INSIGHTS ──
    d9_asc = d9['ascendant']['sign']
    vargottama = [n for n in PLANETS if planets[n]['sign_idx'] == d9[n]['sign_idx']]

    navamsha_text = f"""
    <p>The Navamsha (D9) is the chart of dharma, inner nature, and marriage. Your D9 lagna is
    <strong>{d9_asc}</strong>, revealing that your inner self and spouse carry {d9_asc} qualities.</p>"""

    if vargottama:
        varg_str = ', '.join(f'<strong>{v}</strong>' for v in vargottama)
        navamsha_text += f'<p><span class="tag tag-vargottama">Vargottama</span> {varg_str} — '
        navamsha_text += 'these planets occupy the same sign in both D1 and D9, making them exceptionally reliable. '
        navamsha_text += 'Their promises in the birth chart will manifest consistently.</p>'

    # Check D9 strength of key planets
    for key_planet in [asc_lord, 'Venus', 'Jupiter']:
        if key_planet in d9:
            d9_sign = d9[key_planet]['sign']
            d9_house = d9[key_planet]['house']
            navamsha_text += f'<p>{key_planet} in D9: <strong>{d9_sign}</strong> (House {d9_house}). '
            if key_planet == 'Venus':
                navamsha_text += 'Venus\'s D9 position shows the deeper quality of relationships and marriage satisfaction.'
            elif key_planet == asc_lord:
                navamsha_text += 'Lagna lord\'s D9 position shows your soul\'s deeper purpose and inner strength.'
            elif key_planet == 'Jupiter':
                navamsha_text += 'Jupiter\'s D9 position indicates wisdom, dharma, and spiritual growth potential.'
            navamsha_text += '</p>'

    sections.append(('Navamsha (D9) Insights', navamsha_text))

    # ── Build HTML ──
    interpretation_css = """
  .interp-section { margin-bottom: 28px; }
  .interp-section h3 {
    font-size: 1rem;
    font-weight: 600;
    color: var(--text-bright);
    margin-bottom: 10px;
    padding-left: 12px;
    border-left: 3px solid var(--accent);
  }
  .interp-content {
    font-size: 0.9rem;
    line-height: 1.8;
    color: var(--text);
    padding-left: 12px;
  }
  .interp-content p { margin-bottom: 10px; }
  .interp-content ul { margin-bottom: 10px; }
  .interp-content li { margin-bottom: 4px; line-height: 1.6; }
  .interp-content strong { color: var(--text-bright); }"""

    html_parts = []
    for title, content in sections:
        html_parts.append(f"""    <div class="interp-section">
      <h3>{title}</h3>
      <div class="interp-content">{content}</div>
    </div>""")

    return f"""<style>{interpretation_css}</style>
<div class="section">
  <div class="section-title">Detailed Interpretation</div>
  <div class="card">
{"".join(html_parts)}
  </div>
</div>"""


def _is_kendra_h(h):
    return h in (1, 4, 7, 10)


# ════════════════════════════════════════════════════════════════
# PREDICTION SECTIONS RENDERING
# ════════════════════════════════════════════════════════════════

def _predictions_css():
    """Additional CSS for prediction sections."""
    return """
  /* ── Prediction Sections ─────────────────────── */
  .pred-section { margin-bottom: 32px; }
  .pred-section .section-title { margin-bottom: 16px; }
  .pred-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 14px; }
  @media (max-width: 768px) { .pred-grid { grid-template-columns: 1fr; } }

  .dosha-card {
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 18px;
    margin-bottom: 14px;
    border-left: 4px solid var(--accent);
  }
  .dosha-card.mild { border-left-color: var(--gold); }
  .dosha-card.cancelled { border-left-color: var(--green); }
  .dosha-name { font-size: 1.05rem; font-weight: 600; color: var(--text-bright); margin-bottom: 6px; }
  .dosha-severity { font-size: 0.75rem; padding: 2px 8px; border-radius: 4px; display: inline-block; margin-bottom: 8px; }
  .sev-severe { background: rgba(233,69,96,0.2); color: var(--accent); }
  .sev-moderate { background: rgba(249,199,79,0.15); color: var(--gold); }
  .sev-mild { background: rgba(78,204,163,0.15); color: var(--green); }
  .sev-cancelled { background: rgba(78,204,163,0.1); color: var(--green); }
  .dosha-impact { font-size: 0.88rem; line-height: 1.7; margin-bottom: 10px; }
  .dosha-remedies { font-size: 0.82rem; color: var(--text-dim); }
  .dosha-remedies li { margin-bottom: 3px; }

  .planet-analysis-card {
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 16px;
    margin-bottom: 12px;
  }
  .pa-header { display: flex; align-items: center; gap: 10px; margin-bottom: 10px; }
  .pa-planet { font-size: 1.1rem; font-weight: 600; }
  .pa-badge { font-size: 0.72rem; padding: 2px 7px; border-radius: 3px; background: var(--card-alt); color: var(--text-dim); }
  .pa-text { font-size: 0.87rem; line-height: 1.7; margin-bottom: 8px; }
  .pa-detail { font-size: 0.82rem; color: var(--text-dim); line-height: 1.6; margin-bottom: 4px; }

  .lk-card {
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 14px;
  }
  .lk-planet { font-weight: 600; color: var(--text-bright); font-size: 0.95rem; }
  .lk-prediction { font-size: 0.85rem; line-height: 1.6; margin: 6px 0; }
  .lk-remedy { font-size: 0.82rem; color: var(--green); margin-top: 4px; }
  .lk-remedy::before { content: "Remedy: "; font-weight: 600; }

  .life-pred-card {
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 18px;
    margin-bottom: 14px;
  }
  .lp-title { font-size: 1rem; font-weight: 600; color: var(--accent); margin-bottom: 8px; }
  .lp-summary { font-size: 0.88rem; line-height: 1.7; margin-bottom: 10px; }
  .lp-factors { font-size: 0.82rem; }
  .lp-factor { padding: 3px 0; }
  .lp-factor.pos::before { content: "+"; color: var(--green); font-weight: 700; margin-right: 6px; }
  .lp-factor.neg::before { content: "!"; color: var(--accent); font-weight: 700; margin-right: 6px; }
  .lp-periods { font-size: 0.82rem; margin-top: 8px; color: var(--text-dim); }

  .year-card {
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 14px;
    margin-bottom: 10px;
  }
  .year-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px; }
  .year-num { font-size: 1.15rem; font-weight: 700; color: var(--text-bright); }
  .year-quality { font-size: 0.72rem; padding: 2px 8px; border-radius: 3px; }
  .yq-favorable { background: rgba(78,204,163,0.15); color: var(--green); }
  .yq-challenging { background: rgba(233,69,96,0.15); color: var(--accent); }
  .yq-mixed { background: rgba(249,199,79,0.12); color: var(--gold); }
  .year-summary { font-size: 0.85rem; line-height: 1.6; }

  .remedy-card {
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 16px;
    margin-bottom: 12px;
    border-left: 4px solid var(--gold);
  }
  .rem-planet { font-size: 1rem; font-weight: 600; color: var(--text-bright); }
  .rem-reason { font-size: 0.8rem; color: var(--accent); margin: 4px 0 10px; }
  .rem-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 6px; font-size: 0.82rem; }
  .rem-item { color: var(--text-dim); }
  .rem-item strong { color: var(--text); }
  .rem-mantra { font-family: serif; font-size: 0.9rem; color: var(--gold); margin-top: 8px; padding: 8px; background: var(--card-alt); border-radius: 6px; text-align: center; }

  .house-bar {
    height: 6px;
    border-radius: 3px;
    background: var(--border);
    margin: 6px 0;
  }
  .house-bar-fill { height: 100%; border-radius: 3px; }

  .karma-card {
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 18px;
    margin-bottom: 14px;
  }
  .karma-label { font-size: 0.75rem; text-transform: uppercase; letter-spacing: 2px; color: var(--accent); margin-bottom: 6px; }
  .karma-text { font-size: 0.88rem; line-height: 1.7; }

  .ritual-list { list-style: none; padding: 0; }
  .ritual-list li {
    font-size: 0.88rem;
    padding: 8px 0;
    border-bottom: 1px solid var(--border);
    line-height: 1.5;
  }
  .ritual-list li:last-child { border-bottom: none; }
  .ritual-list li::before { content: "\\25C8 "; color: var(--accent); margin-right: 6px; }

  .nav-toc {
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 16px 20px;
    margin-bottom: 24px;
  }
  .nav-toc-title { font-size: 0.8rem; color: var(--text-dim); text-transform: uppercase; letter-spacing: 2px; margin-bottom: 10px; }
  .nav-toc a {
    display: inline-block;
    font-size: 0.82rem;
    color: var(--text);
    text-decoration: none;
    padding: 4px 10px;
    margin: 2px;
    border-radius: 4px;
    background: var(--card-alt);
    transition: background 0.2s;
  }
  .nav-toc a:hover { background: var(--accent-soft); color: var(--accent); }
"""


def _render_toc():
    """Table of contents for prediction sections."""
    links = [
        ('lucky-points', 'Lucky Points'),
        ('nakshatra-phal', 'Nakshatra Phal'),
        ('life-predictions', 'Life Predictions'),
        ('yearly-forecast', '10-Year Forecast'),
        ('doshas', 'Doshas'),
        ('sade-sati', 'Sade Sati'),
        ('planetary-analysis', 'Planets'),
        ('lal-kitab', 'Lal Kitab'),
        ('remedies', 'Remedies'),
        ('daily-rituals', 'Daily Rituals'),
        ('house-strength', 'House Strength'),
        ('avkahada', 'Avkahada'),
        ('karmic-lessons', 'Karmic Lessons'),
    ]
    items = ' '.join(f'<a href="#{id_}">{label}</a>' for id_, label in links)
    return f'''<div class="nav-toc">
  <div class="nav-toc-title">Detailed Predictions</div>
  {items}
</div>'''


def _render_doshas(doshas):
    if not doshas:
        return '''<div class="pred-section" id="doshas">
  <div class="section-title">Doshas</div>
  <div class="card"><p style="color:var(--green); font-size:0.9rem;">No major doshas detected in this chart. This is a positive sign.</p></div>
</div>'''

    cards = []
    for d in doshas:
        sev = d['severity'].lower()
        sev_cls = 'sev-severe' if 'severe' in sev else ('sev-mild' if 'mild' in sev or 'cancel' in sev or 'mitigat' in sev else 'sev-moderate')
        card_cls = 'cancelled' if 'cancel' in sev else ('mild' if 'mild' in sev else '')

        remedies_html = ''
        if d.get('remedies'):
            remedies_html = '<div class="dosha-remedies"><strong style="color:var(--text);">Remedies:</strong><ul style="padding-left:16px; margin-top:4px;">'
            for r in d['remedies'][:5]:
                remedies_html += f'<li>{r}</li>'
            remedies_html += '</ul></div>'

        cancellations_html = ''
        if d.get('cancellations'):
            cancellations_html = '<div style="font-size:0.82rem; color:var(--green); margin-bottom:8px;"><strong>Mitigating factors:</strong><ul style="padding-left:16px; margin-top:4px;">'
            for c in d['cancellations']:
                cancellations_html += f'<li>{c}</li>'
            cancellations_html += '</ul></div>'

        triggers_html = ''
        if d.get('triggers'):
            triggers_html = '<div style="font-size:0.82rem; margin-bottom:8px; color:var(--text-dim);"><strong style="color:var(--text);">Triggers:</strong><ul style="padding-left:16px; margin-top:4px;">'
            for t in d['triggers']:
                triggers_html += f'<li>{t}</li>'
            triggers_html += '</ul></div>'

        cards.append(f'''<div class="dosha-card {card_cls}">
  <div class="dosha-name">{d['name']}</div>
  <span class="dosha-severity {sev_cls}">{d['severity']}</span>
  {triggers_html}
  <div class="dosha-impact">{d['impact']}</div>
  {cancellations_html}
  {remedies_html}
</div>''')

    return f'''<div class="pred-section" id="doshas">
  <div class="section-title">Doshas</div>
  {"".join(cards)}
</div>'''


def _render_planetary_analysis(analyses):
    cards = []
    for a in analyses:
        badges = []
        badges.append(f'<span class="pa-badge {dignity_class(a["dignity"])}">{a["dignity"]}</span>')
        badges.append(f'<span class="pa-badge">{a["sign"]} &middot; H{a["house"]}</span>')
        badges.append(f'<span class="pa-badge">{a["nakshatra"]} P{a["pada"]}</span>')
        if a['is_retrograde'] and a['planet'] not in ('Sun', 'Moon', 'Rahu', 'Ketu'):
            badges.append('<span class="pa-badge" style="color:var(--orange);">Retrograde</span>')
        if a['is_combust']:
            badges.append('<span class="pa-badge" style="color:var(--accent);">Combust</span>')

        extra = ''
        if a.get('narrative'):
            extra += f'<div class="pa-text" style="color:var(--gold); font-style:italic; margin-bottom:8px; border-left:2px solid var(--gold); padding-left:10px;">{a["narrative"]}</div>'
        if a['retrograde_effect']:
            extra += f'<div class="pa-detail" style="margin-bottom:6px;"><strong style="color:var(--orange);">Retrograde:</strong> {a["retrograde_effect"]}</div>'
        if a['combustion_effect']:
            extra += f'<div class="pa-detail" style="margin-bottom:6px;"><strong style="color:var(--accent);">Combustion:</strong> {a["combustion_effect"]}</div>'
        if a.get('conjunction_text'):
            extra += f'<div class="pa-detail" style="margin-bottom:6px;"><strong style="color:var(--text-bright);">Conjunctions:</strong> {a["conjunction_text"]}</div>'
        if a['aspects_text']:
            extra += f'<div class="pa-detail" style="margin-bottom:6px;"><strong style="color:var(--text-bright);">Aspects:</strong> {a["aspects_text"]}</div>'
        if a['house_lord_text']:
            extra += f'<div class="pa-detail" style="margin-bottom:6px;"><strong style="color:var(--text-bright);">House Lord:</strong> {a["house_lord_text"]}</div>'
        if a.get('dasha_note'):
            extra += f'<div class="pa-detail" style="margin-top:6px; padding:8px; background:var(--accent-soft); border-radius:6px;"><strong style="color:var(--accent);">Active Now:</strong> {a["dasha_note"]}</div>'

        cards.append(f'''<div class="planet-analysis-card">
  <div class="pa-header">
    <span class="pa-planet {planet_class(a["planet"])}">{PLANET_ABBR.get(a["planet"], "")} {a["planet"]}</span>
    {"".join(badges)}
  </div>
  <div class="pa-text">{a["placement"]}</div>
  <div class="pa-text" style="color:var(--text-dim);">{a["dignity_effect"]}</div>
  <div class="pa-detail" style="margin-bottom:6px;">{a["nakshatra_effect"]}</div>
  {extra}
</div>''')

    return f'''<div class="pred-section" id="planetary-analysis">
  <div class="section-title">Detailed Planetary Analysis</div>
  {"".join(cards)}
</div>'''


def _render_lal_kitab(predictions):
    cards = []
    for p in predictions:
        cards.append(f'''<div class="lk-card">
  <div class="lk-planet">{PLANET_ABBR.get(p["planet"], "")} {p["planet"]} <span style="color:var(--text-dim); font-weight:400; font-size:0.82rem;">in {p["sign"]} (House {p["house"]})</span></div>
  <div class="lk-prediction">{p["prediction"]}</div>
  <div class="lk-remedy">{p["remedy"]}</div>
</div>''')

    return f'''<div class="pred-section" id="lal-kitab">
  <div class="section-title">Lal Kitab Predictions &amp; Remedies</div>
  <div style="font-size:0.82rem; color:var(--text-dim); margin-bottom:14px;">Based on the unique Lal Kitab system — planet-in-house predictions with practical remedies.</div>
  <div class="pred-grid">
    {"".join(cards)}
  </div>
</div>'''


def _render_life_predictions(life):
    sections = []
    for key in ('career', 'marriage', 'wealth', 'health', 'spiritual'):
        lp = life[key]
        factors_html = ''
        if lp.get('strength_factors') or lp.get('weakness_factors'):
            factors_html = '<div class="lp-factors">'
            for f in lp.get('strength_factors', []):
                factors_html += f'<div class="lp-factor pos">{f}</div>'
            for f in lp.get('weakness_factors', []):
                factors_html += f'<div class="lp-factor neg">{f}</div>'
            factors_html += '</div>'
        elif lp.get('factors'):
            factors_html = '<div class="lp-factors">'
            for f in lp['factors']:
                cls = 'pos' if 'strong' in f.lower() else 'neg'
                factors_html += f'<div class="lp-factor {cls}">{f}</div>'
            factors_html += '</div>'
        elif lp.get('timing_factors') or lp.get('quality_factors'):
            factors_html = '<div class="lp-factors">'
            for f in lp.get('timing_factors', []):
                factors_html += f'<div class="lp-factor pos">{f}</div>'
            for f in lp.get('quality_factors', []):
                factors_html += f'<div class="lp-factor pos">{f}</div>'
            factors_html += '</div>'
        elif lp.get('vulnerabilities'):
            factors_html = '<div class="lp-factors">'
            for v in lp['vulnerabilities']:
                factors_html += f'<div class="lp-factor neg">{v["issue"]}</div>'
            factors_html += '</div>'

        periods_html = ''
        period_key = next((k for k in ('best_periods', 'marriage_periods', 'wealth_periods', 'vulnerable_periods', 'sadhana_periods') if lp.get(k)), None)
        if period_key and lp[period_key]:
            periods_html = '<div class="lp-periods"><strong style="color:var(--text);">Key periods:</strong> '
            periods_html += ', '.join(f'{p["period"]} ({p.get("start", "")}-{p.get("end", "")})' for p in lp[period_key][:3])
            periods_html += '</div>'

        detailed_html = ''
        if lp.get('detailed_reading'):
            detailed_html = f'<div style="margin-top:12px; font-size:0.87rem; line-height:1.8; color:var(--text); border-top:1px solid var(--border); padding-top:12px;">{lp["detailed_reading"]}</div>'

        sections.append(f'''<div class="life-pred-card">
  <div class="lp-title">{lp["title"]}</div>
  <div class="lp-summary">{lp["summary"]}</div>
  {factors_html}
  {periods_html}
  {detailed_html}
</div>''')

    return f'''<div class="pred-section" id="life-predictions">
  <div class="section-title">Life Predictions</div>
  <div style="font-size:0.82rem; color:var(--text-dim); margin-bottom:14px;">Scenario-based predictions tied to your dasha periods and house lord placements.</div>
  {"".join(sections)}
</div>'''


def _render_yearly_forecast(forecasts):
    cards = []
    for f in forecasts:
        q_cls = f'yq-{f["quality"]}'
        caution = ''
        if f['caution_areas']:
            caution = '<div style="font-size:0.8rem; color:var(--accent); margin-top:6px;">'
            caution += '<br>'.join(f['caution_areas'])
            caution += '</div>'

        cards.append(f'''<div class="year-card">
  <div class="year-header">
    <span class="year-num">{f["year"]}</span>
    <span class="year-quality {q_cls}">{f["maha_lord"]}-{f["antar_lord"]} &middot; {f["quality"]}</span>
  </div>
  <div class="year-summary">{f["summary"]}</div>
  {caution}
</div>''')

    return f'''<div class="pred-section" id="yearly-forecast">
  <div class="section-title">Year-by-Year Forecast (Next 10 Years)</div>
  {"".join(cards)}
</div>'''


def _render_remedies(remedies):
    if not remedies:
        return '''<div class="pred-section" id="remedies">
  <div class="section-title">Remedies &amp; Precautions</div>
  <div class="card"><p style="color:var(--green); font-size:0.9rem;">All planets are well-placed. No specific remedies needed at this time.</p></div>
</div>'''

    cards = []
    for r in remedies:
        cards.append(f'''<div class="remedy-card">
  <div class="rem-planet">{PLANET_ABBR.get(r["planet"], "")} {r["planet"]} <span style="font-weight:400; font-size:0.82rem; color:var(--text-dim);">in {r["sign"]} (H{r["house"]})</span></div>
  <div class="rem-reason">{", ".join(r["reasons"])}</div>
  <div class="rem-grid">
    <div class="rem-item"><strong>Gemstone:</strong> {r["gemstone"]}</div>
    <div class="rem-item"><strong>Metal:</strong> {r["metal"]}</div>
    <div class="rem-item"><strong>Color:</strong> {r["color"]}</div>
    <div class="rem-item"><strong>Deity:</strong> {r["deity"]}</div>
    <div class="rem-item"><strong>Charity:</strong> {r["charity"]}</div>
    <div class="rem-item"><strong>Fasting:</strong> {r["fasting"]}</div>
  </div>
  <div class="rem-mantra">{r["mantra"]}<br><span style="font-size:0.75rem; color:var(--text-dim);">{r["mantra_count"]}</span></div>
</div>''')

    return f'''<div class="pred-section" id="remedies">
  <div class="section-title">Remedies &amp; Precautions</div>
  <div style="font-size:0.82rem; color:var(--text-dim); margin-bottom:14px;">Only planets that need strengthening are listed below. Gemstones should be worn only after consulting a qualified astrologer.</div>
  {"".join(cards)}
</div>'''


def _render_house_strengthening(houses):
    cards = []
    for h in houses:
        score = h['strength_score']
        color = 'var(--green)' if score >= 70 else ('var(--gold)' if score >= 50 else 'var(--accent)')

        factors_html = ''
        if h['strength_factors'] or h['weakness_factors']:
            factors_html = '<div style="font-size:0.8rem; margin-top:6px;">'
            for f in h['strength_factors']:
                factors_html += f'<div style="color:var(--green);">+ {f}</div>'
            for f in h['weakness_factors']:
                factors_html += f'<div style="color:var(--accent);">- {f}</div>'
            factors_html += '</div>'

        remedies_html = ''
        if h['weakness_factors'] and h['remedies']:
            remedies_html = '<div style="font-size:0.8rem; color:var(--text-dim); margin-top:6px;"><strong style="color:var(--text);">Remedies:</strong><ul style="padding-left:16px; margin-top:2px;">'
            for r in h['remedies'][:3]:
                remedies_html += f'<li>{r}</li>'
            remedies_html += '</ul></div>'

        occ = ', '.join(h['occupants']) if h['occupants'] else 'Empty'

        cards.append(f'''<div class="card card-alt" style="margin-bottom:8px; padding:14px;">
  <div style="display:flex; justify-content:space-between; align-items:center;">
    <div>
      <strong style="color:var(--text-bright);">House {h["house"]}</strong>
      <span style="font-size:0.82rem; color:var(--text-dim);"> &middot; {h["sign"]} &middot; Lord: {h["lord"]} (H{h["lord_house"]}) &middot; {occ}</span>
    </div>
    <span style="font-size:0.78rem; color:{color}; font-weight:600;">{h["assessment"]} ({score}%)</span>
  </div>
  <div style="font-size:0.8rem; color:var(--text-dim); margin-top:2px;">{h["area"]}</div>
  <div class="house-bar"><div class="house-bar-fill" style="width:{score}%; background:{color};"></div></div>
  {factors_html}
  {remedies_html}
</div>''')

    return f'''<div class="pred-section" id="house-strength">
  <div class="section-title">House Strength Assessment</div>
  {"".join(cards)}
</div>'''


def _render_karmic_lessons(karma):
    rk = karma['rahu_karma']
    return f'''<div class="pred-section" id="karmic-lessons">
  <div class="section-title">Karmic Lessons &amp; Life Purpose</div>

  <div class="karma-card">
    <div class="karma-label">Rahu in {karma["rahu_sign"]} (House {karma["rahu_house"]}) — This Life's Direction</div>
    <div class="karma-text">{rk.get("this_life", "")}</div>
    <div class="karma-text" style="margin-top:8px; color:var(--text-dim);">{rk.get("lesson", "")}</div>
  </div>

  <div class="karma-card">
    <div class="karma-label">Ketu in {karma["ketu_sign"]} (House {karma["ketu_house"]}) — Past Life Mastery</div>
    <div class="karma-text">{rk.get("past_life", "")}</div>
  </div>

  <div class="karma-card">
    <div class="karma-label">Saturn in {karma["saturn_sign"]} (House {karma["saturn_house"]}) — Discipline Required</div>
    <div class="karma-text">{karma["saturn_lesson"]}</div>
  </div>

  <div class="karma-card">
    <div class="karma-label">12th House ({karma["twelfth_sign"]}) — What to Let Go</div>
    <div class="karma-text">{karma["letting_go"]}</div>
  </div>

  <div class="karma-card" style="border-left: 3px solid var(--accent);">
    <div class="karma-label">House Focus</div>
    <div class="karma-text">{karma.get("rahu_house_karma", "")}</div>
  </div>
</div>'''


def _render_daily_rituals(rituals):
    routine_items = ''
    for step in rituals['daily_routine']:
        routine_items += f'<li>{step}</li>'

    weak_html = ''
    if rituals['weak_planet_mantras']:
        weak_html = '<div style="margin-top:14px;"><strong style="color:var(--accent); font-size:0.85rem;">Weak Planet Mantras:</strong><ul style="padding-left:16px; font-size:0.85rem; margin-top:6px;">'
        for wp in rituals['weak_planet_mantras']:
            if wp['mantra']:
                weak_html += f'<li><strong>{wp["planet"]}</strong> ({wp["day"]}): <em style="color:var(--gold);">{wp["mantra"]}</em></li>'
        weak_html += '</ul></div>'

    return f'''<div class="pred-section" id="daily-rituals">
  <div class="section-title">Personalized Daily Rituals</div>
  <div class="card">
    <div class="pred-grid" style="margin-bottom:16px;">
      <div>
        <div class="pa-detail"><strong>Primary Deity:</strong> {rituals["primary_deity"]}</div>
        <div class="pa-detail"><strong>Primary Mantra:</strong> <em style="color:var(--gold);">{rituals["primary_mantra"]}</em></div>
        <div class="pa-detail"><strong>Lagna Lord Mantra:</strong> <em style="color:var(--gold);">{rituals["lagna_lord_mantra"]}</em></div>
        <div class="pa-detail"><strong>Meditation Direction:</strong> {rituals["meditation_direction"]}</div>
      </div>
      <div>
        <div class="pa-detail"><strong>Best Day:</strong> {rituals["best_day"]}</div>
        <div class="pa-detail"><strong>Best Colors:</strong> {rituals["best_colors"]}</div>
        <div class="pa-detail"><strong>Wake Time:</strong> {rituals["wake_time"]}</div>
        <div class="pa-detail"><strong>Foods to Favor:</strong> {rituals["foods_to_favor"]}</div>
        <div class="pa-detail"><strong>Foods to Avoid:</strong> {rituals["foods_to_avoid"]}</div>
      </div>
    </div>
    <strong style="color:var(--text-bright); font-size:0.9rem;">Daily Routine</strong>
    <ul class="ritual-list" style="margin-top:8px;">
      {routine_items}
    </ul>
    {weak_html}
  </div>
</div>'''


def _render_lucky_points(lp):
    if not lp:
        return ''
    items = [
        ('Lucky Number', str(lp.get('lucky_number', ''))),
        ('Good Numbers', ', '.join(str(n) for n in lp.get('good_numbers', []))),
        ('Evil Numbers', ', '.join(str(n) for n in lp.get('evil_numbers', []))),
        ('Lucky Days', ', '.join(lp.get('lucky_days', []))),
        ('Lucky Stone', lp.get('lucky_stone', '')),
        ('Lucky Metal', lp.get('lucky_metal', '')),
        ('Lucky Colors', lp.get('lucky_colors', '')),
        ('Good Planets', ', '.join(lp.get('good_planets', []))),
        ('Bad Planets', ', '.join(lp.get('bad_planets', []))),
        ('Friendly Signs', ', '.join(lp.get('friendly_signs', []))),
        ('Good Years (Age)', ', '.join(str(y) for y in lp.get('good_years', []))),
    ]
    rows = ''
    for label, val in items:
        if val:
            rows += f'<div style="display:flex; justify-content:space-between; padding:8px 0; border-bottom:1px solid var(--border);"><span style="color:var(--text-dim);">{label}</span><strong style="color:var(--text-bright);">{val}</strong></div>'

    return f'''<div class="pred-section" id="lucky-points">
  <div class="section-title">Lucky Points</div>
  <div class="card">{rows}</div>
</div>'''


def _render_sade_sati(ss):
    if not ss:
        return ''

    status_html = ''
    status = ss.get('current_status', '')
    if status:
        color = 'var(--accent)' if 'currently' in status.lower() else 'var(--green)'
        status_html = f'<div style="padding:12px; background:var(--card-alt); border-radius:8px; margin-bottom:14px; font-size:0.9rem; color:{color}; font-weight:600;">{status}</div>'

    periods_html = ''
    for p in ss.get('periods', []):
        phase_color = {'Rising': 'var(--gold)', 'Peak': 'var(--accent)', 'Setting': 'var(--text-dim)'}.get(p.get('phase', ''), 'var(--text-dim)')
        desc = p.get('description', '')
        periods_html += f'''<div style="padding:10px 0; border-bottom:1px solid var(--border);">
  <div style="display:flex; justify-content:space-between; align-items:center;">
    <span><strong style="color:var(--text-bright);">{p.get('type', '')}</strong> <span style="color:{phase_color}; font-size:0.82rem;">({p.get('phase', '')})</span></span>
    <span style="font-size:0.8rem; color:var(--text-dim);">{p.get('start', '')} — {p.get('end', '')}</span>
  </div>
  <div style="font-size:0.8rem; color:var(--text-dim); margin-top:2px;">Saturn in {p.get('saturn_sign', '')}</div>
  {"<div style='font-size:0.85rem; margin-top:6px; line-height:1.6;'>" + desc + "</div>" if desc else ""}
</div>'''

    phase_desc = ''
    for key in ('rising_description', 'peak_description', 'setting_description'):
        if ss.get(key):
            phase_name = key.replace('_description', '').title()
            phase_desc += f'<div class="karma-card"><div class="karma-label">Sade Sati {phase_name} Phase</div><div class="karma-text">{ss[key]}</div></div>'

    return f'''<div class="pred-section" id="sade-sati">
  <div class="section-title">Sade Sati Report</div>
  {status_html}
  {phase_desc}
  <div class="card" style="max-height:400px; overflow-y:auto;">
    {periods_html}
  </div>
</div>'''


def _render_avkahada(av):
    if not av:
        return ''
    fields = [
        ('Varna', 'varna'), ('Yoni', 'yoni'), ('Gana', 'gana'),
        ('Vasya', 'vasya'), ('Nadi', 'nadi'), ('Paya', 'paya'), ('Tatva', 'tatva'),
    ]
    rows = ''
    for label, key in fields:
        val = av.get(key, '')
        desc = av.get(f'{key}_desc', '')
        rows += f'''<div style="padding:10px 0; border-bottom:1px solid var(--border);">
  <div style="display:flex; justify-content:space-between;">
    <span style="color:var(--text-dim);">{label}</span>
    <strong style="color:var(--text-bright);">{val}</strong>
  </div>
  {"<div style='font-size:0.82rem; color:var(--text-dim); margin-top:4px;'>" + desc + "</div>" if desc else ""}
</div>'''

    return f'''<div class="pred-section" id="avkahada">
  <div class="section-title">Avkahada Chakra</div>
  <div class="card">{rows}</div>
</div>'''


def _render_nakshatra_phal(np):
    if not np:
        return ''
    sections = ''
    for key, title in [('personality', 'Personality'), ('education_income', 'Career & Income'),
                        ('family_life', 'Family & Relationships'), ('health', 'Health')]:
        text = np.get(key, '')
        if text:
            sections += f'''<div style="margin-bottom:16px;">
  <h3 style="font-size:0.9rem; color:var(--accent); margin-bottom:6px; border-left:3px solid var(--accent); padding-left:10px;">{title}</h3>
  <div style="font-size:0.88rem; line-height:1.8;">{text}</div>
</div>'''

    best_years = np.get('best_years', [])
    years_html = ''
    if best_years:
        years_html = f'<div style="margin-top:10px; font-size:0.85rem; color:var(--gold);"><strong>Key ages:</strong> {", ".join(str(y) for y in best_years)}</div>'

    return f'''<div class="pred-section" id="nakshatra-phal">
  <div class="section-title">Nakshatra Phal — {np.get("nakshatra", "")} Nakshatra</div>
  <div style="font-size:0.82rem; color:var(--text-dim); margin-bottom:12px;">Your Moon nakshatra shapes your emotional nature, instincts, and life patterns.</div>
  <div class="card">
    {sections}
    {years_html}
  </div>
</div>'''


def _render_all_predictions(pred):
    """Render all prediction sections — ordered for maximum engagement."""
    html = _render_toc()
    # 1. Quick wins — instantly engaging
    html += _render_lucky_points(pred.get('lucky_points'))
    html += _render_nakshatra_phal(pred.get('nakshatra_phal'))
    # 2. What people came for — life answers
    html += _render_life_predictions(pred['life_predictions'])
    html += _render_yearly_forecast(pred['yearly_forecast'])
    # 3. Doshas and Sade Sati — am I affected?
    html += _render_doshas(pred['doshas'])
    html += _render_sade_sati(pred.get('sade_sati'))
    # 4. Deep planetary readings
    html += _render_planetary_analysis(pred['planetary_analysis'])
    html += _render_lal_kitab(pred['lal_kitab'])
    # 5. Remedies and actions
    html += _render_remedies(pred['remedies'])
    html += _render_daily_rituals(pred['daily_rituals'])
    # 6. Technical / reference
    html += _render_house_strengthening(pred['house_strengthening'])
    html += _render_avkahada(pred.get('avkahada_chakra'))
    html += _render_karmic_lessons(pred['karmic_lessons'])
    return html
