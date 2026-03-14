#!/usr/bin/env python3
"""
Vedic Birth Chart Reader — Complete Jyotish Analysis
=====================================================
Generates:
  1. Structured text analysis (printed to terminal)
  2. Rasi + Navamsha chart image (PNG)
  3. D10 + D7 divisional chart image (PNG)
  4. Dasha timeline image (PNG)
  5. Planetary positions table image (PNG)

Usage:
  python3 main.py                    # Interactive mode
  python3 main.py --demo             # Demo with sample data
"""

import sys
import os

# Add parent dir to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from calculator import calculate_chart
from yogas import identify_all_yogas
from analysis import generate_full_analysis
from visualization import (
    draw_full_chart_page,
    draw_divisional_charts_page,
    draw_dasha_timeline,
    draw_planetary_strength_chart,
)
from constants import CITY_DB


def get_birth_details():
    """Interactive input for birth details."""
    print('\n' + '=' * 60)
    print('  VEDIC BIRTH CHART READER')
    print('  Parashari Jyotish System | Lahiri Ayanamsa')
    print('=' * 60 + '\n')

    # Name
    name = input('  Full name: ').strip()

    # Date
    while True:
        date_str = input('  Date of birth (DD/MM/YYYY): ').strip()
        try:
            parts = date_str.replace('-', '/').split('/')
            day, month, year = int(parts[0]), int(parts[1]), int(parts[2])
            if 1 <= day <= 31 and 1 <= month <= 12 and 1900 <= year <= 2100:
                break
        except (ValueError, IndexError):
            pass
        print('  Invalid date. Use DD/MM/YYYY format.')

    # Time
    while True:
        time_str = input('  Time of birth (HH:MM, 24hr): ').strip()
        try:
            parts = time_str.split(':')
            hour, minute = int(parts[0]), int(parts[1])
            if 0 <= hour <= 23 and 0 <= minute <= 59:
                break
        except (ValueError, IndexError):
            pass
        print('  Invalid time. Use HH:MM in 24-hour format.')

    # Place
    print('\n  Enter birth place (city name or coordinates):')
    place_str = input('  City name or lat,lon: ').strip().lower()

    lat, lon = None, None

    # Try city database
    if place_str in CITY_DB:
        lat, lon = CITY_DB[place_str]
        print(f'  Found: {place_str.title()} ({lat:.4f}, {lon:.4f})')
    else:
        # Try as coordinates
        try:
            parts = place_str.replace(' ', '').split(',')
            lat, lon = float(parts[0]), float(parts[1])
        except (ValueError, IndexError):
            # Partial match
            matches = [k for k in CITY_DB if place_str in k]
            if matches:
                print(f'  Did you mean: {", ".join(m.title() for m in matches[:5])}?')
                retry = input('  Enter exact city name or lat,lon: ').strip().lower()
                if retry in CITY_DB:
                    lat, lon = CITY_DB[retry]
                else:
                    try:
                        parts = retry.replace(' ', '').split(',')
                        lat, lon = float(parts[0]), float(parts[1])
                    except (ValueError, IndexError):
                        pass

    if lat is None or lon is None:
        print('  Could not resolve location. Using Delhi as default.')
        lat, lon = 28.6139, 77.2090

    return year, month, day, hour, minute, lat, lon, name


def generate_chart(year, month, day, hour, minute, lat, lon, name='', output_dir=None):
    """
    Generate complete chart analysis and visualizations.
    Can be called programmatically.
    """
    if output_dir is None:
        output_dir = os.path.dirname(os.path.abspath(__file__))

    os.makedirs(output_dir, exist_ok=True)

    print('\n  Calculating planetary positions...')
    chart = calculate_chart(year, month, day, hour, minute, lat, lon)

    print('  Identifying yogas...')
    yogas_list = identify_all_yogas(chart)

    print('  Generating analysis...')
    chart['birth']['name'] = name
    analysis_text = generate_full_analysis(chart, yogas_list)

    # Print full analysis
    print('\n')
    print(analysis_text)

    # Save analysis to file
    analysis_path = os.path.join(output_dir, 'analysis.txt')
    with open(analysis_path, 'w') as f:
        f.write(analysis_text)
    print(f'\n  Analysis saved to: {analysis_path}')

    # Generate visualizations
    print('\n  Generating chart visualizations...')

    p1 = os.path.join(output_dir, 'chart_rasi_navamsha.png')
    draw_full_chart_page(chart, p1)
    print(f'  Rasi + Navamsha chart: {p1}')

    p2 = os.path.join(output_dir, 'chart_d10_d7.png')
    draw_divisional_charts_page(chart, p2)
    print(f'  D10 + D7 charts: {p2}')

    p3 = os.path.join(output_dir, 'chart_dasha_timeline.png')
    draw_dasha_timeline(chart['dashas'], p3)
    print(f'  Dasha timeline: {p3}')

    p4 = os.path.join(output_dir, 'chart_planetary_positions.png')
    draw_planetary_strength_chart(chart, p4)
    print(f'  Planetary positions: {p4}')

    print('\n  Done. All files saved to: ' + output_dir)
    print()

    return chart, yogas_list, analysis_text


def demo():
    """Run with sample birth data for testing."""
    print('\n  Running demo with sample data...')
    print('  Date: 15/08/1947, Time: 00:00, Place: Delhi')
    generate_chart(1947, 8, 15, 0, 0, 28.6139, 77.2090)


if __name__ == '__main__':
    if '--demo' in sys.argv:
        demo()
    else:
        year, month, day, hour, minute, lat, lon, name = get_birth_details()
        generate_chart(year, month, day, hour, minute, lat, lon, name=name)
