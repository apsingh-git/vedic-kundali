"""
Kundali Web App — Flask app for generating Vedic birth chart reports.
Mobile-friendly dark UI. Deploy to Render free tier.
"""

import os
import re
import time
import html as html_lib
from collections import defaultdict
from flask import Flask, render_template, request, abort, make_response

from calculator import calculate_chart
from yogas import identify_all_yogas
from html_report import generate_html_report
from constants import CITY_DB

app = Flask(__name__)

# ── Security ───────────────────────────────────────────────────
# Rate limiting: max requests per IP per minute
_RATE_LIMIT = int(os.environ.get('RATE_LIMIT', 5))
_RATE_WINDOW = 60  # seconds
_request_log = defaultdict(list)


def _check_rate_limit(ip):
    """Return True if request is allowed, False if rate-limited."""
    now = time.time()
    # Clean old entries
    _request_log[ip] = [t for t in _request_log[ip] if now - t < _RATE_WINDOW]
    if len(_request_log[ip]) >= _RATE_LIMIT:
        return False
    _request_log[ip].append(now)
    return True


def _sanitize(text, max_len=100):
    """Strip HTML/script tags and limit length."""
    if not text:
        return ''
    text = text.strip()[:max_len]
    text = re.sub(r'[<>&"\']', '', text)  # remove HTML-dangerous chars
    return text


def _validate_date(year, month, day):
    """Basic date range validation."""
    return 1900 <= year <= 2030 and 1 <= month <= 12 and 1 <= day <= 31


def _validate_time(hour, minute):
    """Basic time validation."""
    return 0 <= hour <= 23 and 0 <= minute <= 59


# ── Routes ─────────────────────────────────────────────────────

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/generate', methods=['POST'])
def generate():
    # Rate limit
    client_ip = request.headers.get('X-Forwarded-For', request.remote_addr)
    if not _check_rate_limit(client_ip):
        return render_template('index.html',
                               errors=['Too many requests. Please wait a minute and try again.']), 429

    # Sanitize inputs
    name = _sanitize(request.form.get('name', ''), max_len=80)
    date_str = _sanitize(request.form.get('date', ''), max_len=10)
    time_str = _sanitize(request.form.get('time', ''), max_len=5)
    city_raw = request.form.get('city', '').strip()
    city = _sanitize(city_raw, max_len=60).lower()

    # Validate presence
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
                               date=date_str, time=time_str, city=city_raw)

    # Parse and validate date
    try:
        parts = date_str.split('-')
        year, month, day = int(parts[0]), int(parts[1]), int(parts[2])
        if not _validate_date(year, month, day):
            raise ValueError('out of range')
    except (ValueError, IndexError):
        return render_template('index.html', errors=['Invalid date. Use the date picker.'],
                               name=name, date=date_str, time=time_str, city=city_raw)

    # Parse and validate time
    try:
        tparts = time_str.split(':')
        hour, minute = int(tparts[0]), int(tparts[1])
        if not _validate_time(hour, minute):
            raise ValueError('out of range')
    except (ValueError, IndexError):
        return render_template('index.html', errors=['Invalid time. Use the time picker.'],
                               name=name, date=date_str, time=time_str, city=city_raw)

    # Lookup city (exact match first, then partial)
    coords = CITY_DB.get(city)
    if not coords:
        matches = [k for k in CITY_DB if city in k or k in city]
        if matches:
            coords = CITY_DB[matches[0]]
        else:
            return render_template('index.html',
                                   errors=[f'City not found. Try a major Indian city name (e.g. Mumbai, Delhi, Pune).'],
                                   name=name, date=date_str, time=time_str, city=city_raw)

    lat, lon = coords

    # Generate chart
    try:
        chart = calculate_chart(year, month, day, hour, minute, lat, lon)
        chart['birth']['name'] = html_lib.escape(name)
        yogas_list = identify_all_yogas(chart)
        report_html = generate_html_report(chart, yogas_list)
        response = make_response(report_html)
        response.headers['Content-Type'] = 'text/html; charset=utf-8'
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        return response
    except Exception:
        return render_template('index.html',
                               errors=['Something went wrong generating the chart. Please check your inputs.'],
                               name=name, date=date_str, time=time_str, city=city_raw)


@app.after_request
def add_security_headers(response):
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['Referrer-Policy'] = 'no-referrer'
    return response


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
