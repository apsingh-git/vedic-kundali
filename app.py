"""
Kundali Web App — Flask app for generating Vedic birth chart reports.
Mobile-friendly dark UI. Deploy to Render free tier.
"""

import os
import io
import tempfile
from flask import Flask, render_template, request, send_file

from calculator import calculate_chart
from yogas import identify_all_yogas
from html_report import generate_html_report
from constants import CITY_DB

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/generate', methods=['POST'])
def generate():
    name = request.form.get('name', '').strip()
    date_str = request.form.get('date', '')  # YYYY-MM-DD from input[type=date]
    time_str = request.form.get('time', '')  # HH:MM from input[type=time]
    city = request.form.get('city', '').strip().lower()

    # Validate
    errors = []
    if not name:
        errors.append('Name is required')
    if not date_str:
        errors.append('Date of birth is required')
    if not time_str:
        errors.append('Time of birth is required')
    if not city:
        errors.append('Place of birth is required')

    if errors:
        return render_template('index.html', errors=errors, name=name,
                               date=date_str, time=time_str, city=request.form.get('city', ''))

    # Parse date
    try:
        parts = date_str.split('-')
        year, month, day = int(parts[0]), int(parts[1]), int(parts[2])
    except (ValueError, IndexError):
        return render_template('index.html', errors=['Invalid date format'],
                               name=name, date=date_str, time=time_str, city=request.form.get('city', ''))

    # Parse time
    try:
        tparts = time_str.split(':')
        hour, minute = int(tparts[0]), int(tparts[1])
    except (ValueError, IndexError):
        return render_template('index.html', errors=['Invalid time format'],
                               name=name, date=date_str, time=time_str, city=request.form.get('city', ''))

    # Lookup city
    coords = CITY_DB.get(city)
    if not coords:
        # Try partial match
        matches = [k for k in CITY_DB if city in k or k in city]
        if matches:
            coords = CITY_DB[matches[0]]
        else:
            return render_template('index.html',
                                   errors=[f'City "{request.form.get("city", "")}" not found. Try a major Indian city name.'],
                                   name=name, date=date_str, time=time_str, city=request.form.get('city', ''))

    lat, lon = coords

    # Generate chart
    try:
        chart = calculate_chart(year, month, day, hour, minute, lat, lon)
        chart['birth']['name'] = name
        yogas_list = identify_all_yogas(chart)
        html = generate_html_report(chart, yogas_list)
        return html
    except Exception as e:
        return render_template('index.html',
                               errors=[f'Error generating chart: {str(e)}'],
                               name=name, date=date_str, time=time_str, city=request.form.get('city', ''))


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
