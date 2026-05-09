"""
evaluation/evaluate.py

Compares NDBC buoy data against Surfline LOTUS ground truth.
Queries evaluation.swell_readings, computes per-spot statistics,
and renders a self-contained HTML report at evaluation/report.html.

Usage:
    python evaluate.py              # all spots
    python evaluate.py rockaways    # one spot
"""

import sys
import os
import argparse
import math
import json
from datetime import datetime, timezone, timedelta
from zoneinfo import ZoneInfo
from dotenv import load_dotenv
import psycopg2
import psycopg2.extras

load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))

SPOTS = ['rockaways', 'manasquan', 'steamer_lane', 'trestles', 'ocean_beach_central']
MATCH_TOLERANCE_MINUTES = 90

SPOT_TIMEZONES = {
    'rockaways':           'America/New_York',
    'manasquan':           'America/New_York',
    'steamer_lane':        'America/Los_Angeles',
    'trestles':            'America/Los_Angeles',
    'ocean_beach_central': 'America/Los_Angeles',
}

# ---------------------------------------------------------------------------
# DB
# ---------------------------------------------------------------------------

def get_connection():
    db_url = os.environ.get('DATABASE_URL')
    if not db_url:
        print("DATABASE_URL not set.")
        sys.exit(1)
    return psycopg2.connect(db_url, cursor_factory=psycopg2.extras.RealDictCursor)


def fetch_readings(conn, location):
    with conn.cursor() as cur:
        cur.execute("""
            SELECT source, timestamp,
                   primary_swell_height, primary_swell_period, primary_swell_direction,
                   secondary_swell_height, secondary_swell_period, secondary_swell_direction
            FROM evaluation.swell_readings
            WHERE location = %s
              AND source IN ('surfline_lotus', 'ndbc_buoy')
            ORDER BY timestamp ASC
        """, (location,))
        return cur.fetchall()


def fetch_readings_recent(conn, location, days=7):
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)
    with conn.cursor() as cur:
        cur.execute("""
            SELECT source, timestamp,
                   primary_swell_height, primary_swell_period, primary_swell_direction
            FROM evaluation.swell_readings
            WHERE location = %s
              AND source IN ('surfline_lotus', 'ndbc_buoy')
              AND timestamp >= %s
            ORDER BY timestamp ASC
        """, (location, cutoff))
        return cur.fetchall()


# ---------------------------------------------------------------------------
# Matching
# ---------------------------------------------------------------------------

def match_readings(rows):
    surfline = [r for r in rows if r['source'] == 'surfline_lotus']
    ndbc     = [r for r in rows if r['source'] == 'ndbc_buoy']
    tolerance_seconds = MATCH_TOLERANCE_MINUTES * 60
    pairs = []
    for sl in surfline:
        sl_ts = sl['timestamp'].replace(tzinfo=timezone.utc) if sl['timestamp'].tzinfo is None else sl['timestamp']
        best, best_delta = None, float('inf')
        for nb in ndbc:
            nb_ts = nb['timestamp'].replace(tzinfo=timezone.utc) if nb['timestamp'].tzinfo is None else nb['timestamp']
            delta = abs((sl_ts - nb_ts).total_seconds())
            if delta < best_delta and delta <= tolerance_seconds:
                best_delta = delta
                best = nb
        if best:
            pairs.append((sl, best))
    return pairs


# ---------------------------------------------------------------------------
# Stats helpers
# ---------------------------------------------------------------------------

def direction_delta(a, b):
    if a is None or b is None:
        return None
    return (b - a + 180) % 360 - 180

def safe_delta(ndbc_val, sl_val):
    if ndbc_val is None or sl_val is None:
        return None
    return float(ndbc_val) - float(sl_val)

def compute_stats(deltas):
    valid = [d for d in deltas if d is not None]
    if not valid:
        return {'mae': None, 'bias': None, 'std': None, 'n': 0}
    n = len(valid)
    bias = sum(valid) / n
    mae = sum(abs(d) for d in valid) / n
    variance = sum((d - bias) ** 2 for d in valid) / n
    return {'mae': round(mae, 2), 'bias': round(bias, 2), 'std': round(math.sqrt(variance), 2), 'n': n}

def compute_r2(xs, ys):
    pairs = [(x, y) for x, y in zip(xs, ys) if x is not None and y is not None]
    if len(pairs) < 3:
        return None, None, None
    n = len(pairs)
    xs_, ys_ = [p[0] for p in pairs], [p[1] for p in pairs]
    xm = sum(xs_) / n
    ym = sum(ys_) / n
    num = sum((x - xm) * (y - ym) for x, y in zip(xs_, ys_))
    den = sum((x - xm) ** 2 for x in xs_)
    if den == 0:
        return None, None, None
    slope = num / den
    intercept = ym - slope * xm
    ss_res = sum((y - (slope * x + intercept)) ** 2 for x, y in zip(xs_, ys_))
    ss_tot = sum((y - ym) ** 2 for y in ys_)
    r2 = 1 - ss_res / ss_tot if ss_tot > 0 else None
    return (round(r2, 3) if r2 is not None else None,
            round(slope, 3), round(intercept, 3))


# ---------------------------------------------------------------------------
# Per-spot analysis
# ---------------------------------------------------------------------------

def fv(row, key):
    """Safe float extraction from a db row."""
    v = row[key]
    return float(v) if v is not None else None

def analyze_spot(location, rows):
    pairs = match_readings(rows)
    if not pairs:
        return None

    p_height_deltas, p_period_deltas, p_dir_deltas = [], [], []
    s_height_deltas, s_period_deltas, s_dir_deltas = [], [], []
    time_series   = []
    scatter_primary   = []
    scatter_secondary = []

    for sl, nb in pairs:
        p_height_deltas.append(safe_delta(nb['primary_swell_height'],   sl['primary_swell_height']))
        p_period_deltas.append(safe_delta(nb['primary_swell_period'],   sl['primary_swell_period']))
        p_dir_deltas.append(direction_delta(sl['primary_swell_direction'], nb['primary_swell_direction']))
        s_height_deltas.append(safe_delta(nb['secondary_swell_height'], sl['secondary_swell_height']))
        s_period_deltas.append(safe_delta(nb['secondary_swell_period'], sl['secondary_swell_period']))
        s_dir_deltas.append(direction_delta(sl['secondary_swell_direction'], nb['secondary_swell_direction']))

        time_series.append({
            'ts':                      sl['timestamp'].isoformat(),
            'sl_primary_height':       fv(sl, 'primary_swell_height'),
            'nb_primary_height':       fv(nb, 'primary_swell_height'),
            'sl_primary_period':       fv(sl, 'primary_swell_period'),
            'nb_primary_period':       fv(nb, 'primary_swell_period'),
            'sl_primary_direction':    fv(sl, 'primary_swell_direction'),
            'nb_primary_direction':    fv(nb, 'primary_swell_direction'),
            'sl_secondary_height':     fv(sl, 'secondary_swell_height'),
            'nb_secondary_height':     fv(nb, 'secondary_swell_height'),
            'sl_secondary_period':     fv(sl, 'secondary_swell_period'),
            'nb_secondary_period':     fv(nb, 'secondary_swell_period'),
            'sl_secondary_direction':  fv(sl, 'secondary_swell_direction'),
            'nb_secondary_direction':  fv(nb, 'secondary_swell_direction'),
        })

        if nb['primary_swell_height'] is not None and sl['primary_swell_height'] is not None:
            scatter_primary.append({'x': fv(nb, 'primary_swell_height'), 'y': fv(sl, 'primary_swell_height')})
        if nb['secondary_swell_height'] is not None and sl['secondary_swell_height'] is not None:
            scatter_secondary.append({'x': fv(nb, 'secondary_swell_height'), 'y': fv(sl, 'secondary_swell_height')})

    px = [p['x'] for p in scatter_primary]
    py = [p['y'] for p in scatter_primary]
    r2_primary, slope_primary, intercept_primary = compute_r2(px, py)

    return {
        'location': location,
        'n_pairs':  len(pairs),
        'stats': {
            'primary_height':      compute_stats(p_height_deltas),
            'primary_period':      compute_stats(p_period_deltas),
            'primary_direction':   compute_stats(p_dir_deltas),
            'secondary_height':    compute_stats(s_height_deltas),
            'secondary_period':    compute_stats(s_period_deltas),
            'secondary_direction': compute_stats(s_dir_deltas),
        },
        'time_series':       time_series,
        'scatter_primary':   scatter_primary,
        'scatter_secondary': scatter_secondary,
        'r2_primary':        r2_primary,
        'slope_primary':     slope_primary,
        'intercept_primary': intercept_primary,
    }


def analyze_spot_recent(location, rows):
    """Extract matched pairs for the last-N-days height chart."""
    tz = ZoneInfo(SPOT_TIMEZONES.get(location, 'UTC'))
    pairs = match_readings(rows)
    if not pairs:
        return None

    pair_rows = []
    for sl, nb in pairs:
        sl_ts = sl['timestamp'].replace(tzinfo=timezone.utc) if sl['timestamp'].tzinfo is None else sl['timestamp']
        local_ts = sl_ts.astimezone(tz)
        pair_rows.append({
            'date':      local_ts.strftime('%b %-d'),
            'slot':      local_ts.strftime('%-I%p').lower(),
            'tz_abbr':   local_ts.strftime('%Z'),
            'sl_height': fv(sl, 'primary_swell_height'),
            'nb_height': fv(nb, 'primary_swell_height'),
        })

    tz_abbr = pair_rows[-1]['tz_abbr'] if pair_rows else ''
    return {
        'location': location,
        'n_pairs':  len(pairs),
        'tz_abbr':  tz_abbr,
        'pairs':    pair_rows,
    }


# ---------------------------------------------------------------------------
# HTML renderer
# ---------------------------------------------------------------------------

def render_weekly_section(recent_results, days=7):
    """Returns the HTML for the Last 7 Days grid of primary height charts."""
    now   = datetime.now(timezone.utc)
    start = now - timedelta(days=days)
    date_range = f"{start.strftime('%b %-d')} → {now.strftime('%b %-d, %Y')}"

    if not recent_results:
        return f'''
    <section class="weekly-section" id="weekly">
        <div class="section-title">Last {days} Days — Primary Swell Height — {date_range}</div>
        <p class="weekly-no-data">No matched readings in the last {days} days.</p>
    </section>'''

    cards_html = ''
    charts_js  = ''

    for r in recent_results:
        loc     = r['location']
        label   = SPOT_LABELS.get(loc, loc)
        pairs   = r['pairs']
        tz_abbr = r['tz_abbr']

        if not pairs:
            cards_html += f'<div class="weekly-chart-card"><div class="weekly-chart-title">{label}</div><p class="weekly-no-data">No data</p></div>'
            continue

        labels_json = json.dumps([f"{p['date']} {p['slot']}" for p in pairs])
        sl_json     = json.dumps([p['sl_height'] for p in pairs])
        nb_json     = json.dumps([p['nb_height']  for p in pairs])

        cards_html += f'''
        <div class="weekly-chart-card">
            <div class="weekly-chart-title">{label} <span class="weekly-chart-meta">{r["n_pairs"]} readings · {tz_abbr}</span></div>
            <div class="weekly-chart-wrap"><canvas id="wk-{loc}"></canvas></div>
        </div>'''

        charts_js += f'''
        (function() {{
            var MONO = "'IBM Plex Mono', monospace";
            var ctx = document.getElementById('wk-{loc}').getContext('2d');
            new Chart(ctx, {{
                type: 'line',
                data: {{
                    labels: {labels_json},
                    datasets: [
                        {{ label: 'Surfline', data: {sl_json},
                           borderColor: '#38bdf8', backgroundColor: 'rgba(56,189,248,0.08)',
                           borderWidth: 1.5, pointRadius: 0, tension: 0.3, fill: true, spanGaps: true }},
                        {{ label: 'NDBC', data: {nb_json},
                           borderColor: '#f97316', backgroundColor: 'rgba(249,115,22,0.08)',
                           borderWidth: 1.5, pointRadius: 0, tension: 0.3, fill: true, spanGaps: true }},
                    ]
                }},
                options: {{
                    responsive: true, maintainAspectRatio: false,
                    interaction: {{ mode: 'index', intersect: false }},
                    plugins: {{
                        legend: {{ labels: {{ color: '#94a3b8', font: {{ family: MONO, size: 10 }}, boxWidth: 10, padding: 6 }} }},
                        tooltip: {{
                            backgroundColor: '#0f172a', titleColor: '#94a3b8',
                            bodyColor: '#e2e8f0', borderColor: '#1e293b', borderWidth: 1,
                            titleFont: {{ family: MONO, size: 10 }}, bodyFont: {{ family: MONO, size: 10 }},
                            callbacks: {{ label: function(c) {{
                                var v = c.parsed.y;
                                return v != null ? c.dataset.label + ': ' + v.toFixed(1) + 'ft' : c.dataset.label + ': —';
                            }} }}
                        }},
                    }},
                    scales: {{
                        x: {{
                            ticks: {{
                                color: '#475569', font: {{ family: MONO, size: 9 }},
                                maxTicksLimit: 7, maxRotation: 0,
                                callback: function(val) {{
                                    var lbl = this.getLabelForValue(val);
                                    return lbl ? lbl.split(' ').slice(0, 2).join(' ') : '';
                                }}
                            }},
                            grid: {{ color: '#1e293b' }},
                        }},
                        y: {{
                            ticks: {{ color: '#475569', font: {{ family: MONO, size: 9 }}, callback: function(v) {{ return v + 'ft'; }} }},
                            grid: {{ color: '#1e293b' }},
                            beginAtZero: true,
                        }},
                    }}
                }}
            }});
        }})();'''

    return f'''
    <section class="weekly-section" id="weekly">
        <div class="section-title">Last {days} Days — Primary Swell Height — {date_range}</div>
        <div class="weekly-grid">{cards_html}</div>
        <script>document.addEventListener('DOMContentLoaded', function() {{ {charts_js} }});</script>
    </section>'''


SPOT_LABELS = {
    'rockaways':           'Rockaways',
    'manasquan':           'Manasquan',
    'steamer_lane':        'Steamer Lane',
    'trestles':            'Trestles',
    'ocean_beach_central': 'Ocean Beach',
}

def fmt(val, unit='', precision=2):
    if val is None:
        return '<span class="null">—</span>'
    sign = '+' if val > 0 else ''
    return f'{sign}{val:.{precision}f}{unit}'

def bias_class(val):
    if val is None: return ''
    if val > 0.3:  return 'pos'
    if val < -0.3: return 'neg'
    return 'neutral'

def render_html(results, target_spots, recent_results=None):
    from datetime import datetime
    generated = datetime.now().strftime('%B %d, %Y at %H:%M')

    spot_sections = ''
    summary_rows  = ''

    for r in results:
        loc   = r['location']
        label = SPOT_LABELS.get(loc, loc)
        s     = r['stats']
        ts_json        = json.dumps(r['time_series'])
        scatter_p_json = json.dumps(r['scatter_primary'])
        scatter_s_json = json.dumps(r['scatter_secondary'])
        r2        = r['r2_primary']
        slope     = r['slope_primary']
        intercept = r['intercept_primary']
        r2_str  = f'{r2:.2f}' if r2 is not None else '—'
        fit_str = ''
        if slope is not None:
            sign = '+' if intercept >= 0 else ''
            fit_str = f'y = {slope:.2f}x {sign}{intercept:.2f}'

        def stat_row(metric_key, label_text, unit='ft'):
            st = s[metric_key]
            if st['n'] == 0:
                return f'<tr><td>{label_text}</td><td colspan="3" class="null">no data</td></tr>'
            u = unit
            return f'''<tr>
                <td>{label_text}</td>
                <td>{st["mae"]:.2f}{u}</td>
                <td class="{bias_class(st["bias"])}">{fmt(st["bias"], u)}</td>
                <td>{st["std"]:.2f}{u}</td>
            </tr>'''

        spot_sections += f'''
        <section class="spot-section" id="{loc}">
            <div class="spot-header">
                <h2>{label}</h2>
                <span class="pair-count">{r["n_pairs"]} matched readings</span>
            </div>

            <div class="spot-grid">
                <div class="stats-block">
                    <table class="stats-table">
                        <thead>
                            <tr>
                                <th>Metric</th><th>MAE</th>
                                <th>Bias (NDBC − SL)</th><th>Std Dev</th>
                            </tr>
                        </thead>
                        <tbody>
                            {stat_row("primary_height",     "Primary Swell Ht",    "ft")}
                            {stat_row("primary_period",     "Primary Period",      "s")}
                            {stat_row("primary_direction",  "Primary Direction",   "°")}
                            {stat_row("secondary_height",   "Secondary Swell Ht",  "ft")}
                            {stat_row("secondary_period",   "Secondary Period",    "s")}
                            {stat_row("secondary_direction","Secondary Direction", "°")}
                        </tbody>
                    </table>
                    <div class="legend">
                        <span class="pos-legend">Positive bias → NDBC reads higher than Surfline</span>
                        <span class="neg-legend">Negative bias → NDBC reads lower than Surfline</span>
                    </div>
                </div>

                <div class="chart-block">
                    <div class="chart-tabs">
                        <button class="tab-btn active"
                                onclick="switchView('{loc}', 'primary')">Primary Swell</button>
                        <button class="tab-btn"
                                onclick="switchView('{loc}', 'secondary')">Secondary Swell</button>
                        <button class="tab-btn"
                                onclick="switchView('{loc}', 'scatter')">Scatter</button>
                    </div>

                    <!-- PRIMARY: height / period / direction stacked -->
                    <div id="ts-primary-{loc}" class="chart-wrap" style="display:block;">
                        <div style="position:relative;height:140px;">
                            <canvas id="chart-p-ht-{loc}"></canvas>
                        </div>
                        <div style="position:relative;height:110px;margin-top:2px;">
                            <canvas id="chart-p-per-{loc}"></canvas>
                        </div>
                        <div style="position:relative;height:100px;margin-top:2px;">
                            <canvas id="chart-p-dir-{loc}"></canvas>
                        </div>
                    </div>

                    <!-- SECONDARY: height / period / direction stacked -->
                    <div id="ts-secondary-{loc}" class="chart-wrap" style="display:none;">
                        <div style="position:relative;height:140px;">
                            <canvas id="chart-s-ht-{loc}"></canvas>
                        </div>
                        <div style="position:relative;height:110px;margin-top:2px;">
                            <canvas id="chart-s-per-{loc}"></canvas>
                        </div>
                        <div style="position:relative;height:100px;margin-top:2px;">
                            <canvas id="chart-s-dir-{loc}"></canvas>
                        </div>
                    </div>

                    <!-- SCATTER -->
                    <div id="sc-{loc}" class="chart-wrap" style="display:none;">
                        <div class="scatter-meta">
                            <span class="r2-badge">R² = {r2_str}</span>
                            <span class="fit-eq">{fit_str}</span>
                        </div>
                        <div style="position:relative;height:340px;">
                            <canvas id="scatter-{loc}"></canvas>
                        </div>
                    </div>
                </div>
            </div>
        </section>

        <script>
        (function() {{
            var tsData    = {ts_json};
            var scatterP  = {scatter_p_json};
            var scatterS  = {scatter_s_json};
            var slope     = {slope if slope is not None else 'null'};
            var intercept = {intercept if intercept is not None else 'null'};

            // Chart instances — keyed by role
            var charts = {{}};

            var MONO = "'IBM Plex Mono', monospace";
            var GRID = '#1e293b';
            var TICK = '#475569';
            var SL_COLOR  = '#38bdf8';
            var NB_COLOR  = '#f97316';
            var SL_FILL   = 'rgba(56,189,248,0.08)';
            var NB_FILL   = 'rgba(249,115,22,0.08)';

            var labels = tsData.map(function(d) {{
                return new Date(d.ts).toLocaleDateString('en-US', {{month:'short', day:'numeric'}});
            }});

            function tooltipDefaults(unitSuffix) {{
                return {{
                    backgroundColor: '#0f172a',
                    titleColor: '#94a3b8', bodyColor: '#e2e8f0',
                    borderColor: '#1e293b', borderWidth: 1,
                    titleFont: {{ family: MONO, size: 11 }},
                    bodyFont:  {{ family: MONO, size: 11 }},
                    callbacks: {{
                        label: function(c) {{
                            var v = c.parsed.y;
                            return v != null
                                ? c.dataset.label + ': ' + v.toFixed(1) + unitSuffix
                                : c.dataset.label + ': —';
                        }}
                    }}
                }};
            }}

            function xAxis(showLabels) {{
                return {{
                    ticks: {{
                        color: showLabels ? TICK : 'transparent',
                        font: {{ family: MONO, size: 10 }},
                        maxTicksLimit: 10, maxRotation: 0,
                    }},
                    grid: {{ color: GRID }},
                }};
            }}

            function yAxis(unit, opts) {{
                return Object.assign({{
                    ticks: {{
                        color: TICK,
                        font: {{ family: MONO, size: 10 }},
                        callback: function(v) {{ return v + unit; }},
                    }},
                    grid: {{ color: GRID }},
                    beginAtZero: true,
                }}, opts || {{}});
            }}

            function lineDataset(label, data, color, fill) {{
                return {{
                    label: label, data: data,
                    borderColor: color,
                    backgroundColor: fill || 'transparent',
                    borderWidth: 1.5,
                    pointRadius: 0, tension: 0.3,
                    fill: !!fill, spanGaps: true,
                }};
            }}

            function destroyIfExists(key) {{
                if (charts[key]) {{ charts[key].destroy(); delete charts[key]; }}
            }}

            // ── PRIMARY: height / period / direction stacked ─────────────
            function buildPrimary() {{
                destroyIfExists('p-ht');
                destroyIfExists('p-per');
                destroyIfExists('p-dir');

                var ctxHt = document.getElementById('chart-p-ht-{loc}').getContext('2d');
                charts['p-ht'] = new Chart(ctxHt, {{
                    type: 'line',
                    data: {{
                        labels: labels,
                        datasets: [
                            lineDataset('Surfline Ht', tsData.map(function(d) {{ return d.sl_primary_height; }}), SL_COLOR, SL_FILL),
                            lineDataset('NDBC Ht',     tsData.map(function(d) {{ return d.nb_primary_height; }}), NB_COLOR, NB_FILL),
                        ]
                    }},
                    options: {{
                        responsive: true, maintainAspectRatio: false,
                        interaction: {{ mode: 'index', intersect: false }},
                        plugins: {{
                            legend: {{ labels: {{ color: '#94a3b8', font: {{ family: MONO, size: 10 }}, boxWidth: 10 }} }},
                            tooltip: tooltipDefaults('ft'),
                        }},
                        scales: {{ x: xAxis(false), y: yAxis('ft') }}
                    }}
                }});

                var ctxPer = document.getElementById('chart-p-per-{loc}').getContext('2d');
                charts['p-per'] = new Chart(ctxPer, {{
                    type: 'line',
                    data: {{
                        labels: labels,
                        datasets: [
                            lineDataset('Surfline Period', tsData.map(function(d) {{ return d.sl_primary_period; }}), SL_COLOR),
                            lineDataset('NDBC Period',     tsData.map(function(d) {{ return d.nb_primary_period; }}), NB_COLOR),
                        ]
                    }},
                    options: {{
                        responsive: true, maintainAspectRatio: false,
                        interaction: {{ mode: 'index', intersect: false }},
                        plugins: {{
                            legend: {{ labels: {{ color: '#94a3b8', font: {{ family: MONO, size: 10 }}, boxWidth: 10 }} }},
                            tooltip: tooltipDefaults('s'),
                        }},
                        scales: {{ x: xAxis(false), y: yAxis('s', {{ beginAtZero: false }}) }}
                    }}
                }});

                var ctxDir = document.getElementById('chart-p-dir-{loc}').getContext('2d');
                charts['p-dir'] = new Chart(ctxDir, {{
                    type: 'line',
                    data: {{
                        labels: labels,
                        datasets: [
                            lineDataset('Surfline Dir', tsData.map(function(d) {{ return d.sl_primary_direction; }}), SL_COLOR),
                            lineDataset('NDBC Dir',     tsData.map(function(d) {{ return d.nb_primary_direction; }}), NB_COLOR),
                        ]
                    }},
                    options: {{
                        responsive: true, maintainAspectRatio: false,
                        interaction: {{ mode: 'index', intersect: false }},
                        plugins: {{
                            legend: {{ labels: {{ color: '#94a3b8', font: {{ family: MONO, size: 10 }}, boxWidth: 10 }} }},
                            tooltip: tooltipDefaults('°'),
                        }},
                        scales: {{
                            x: xAxis(true),
                            y: {{ ticks: {{ color: TICK, font: {{ family: MONO, size: 10 }}, callback: function(v) {{ return v + '°'; }} }}, grid: {{ color: GRID }}, min: 0, max: 360 }}
                        }}
                    }}
                }});
            }}

            // ── SECONDARY: height / period / direction stacked ────────────
            function buildSecondary() {{
                destroyIfExists('s-ht');
                destroyIfExists('s-per');
                destroyIfExists('s-dir');

                var ctxHt = document.getElementById('chart-s-ht-{loc}').getContext('2d');
                charts['s-ht'] = new Chart(ctxHt, {{
                    type: 'line',
                    data: {{
                        labels: labels,
                        datasets: [
                            lineDataset('Surfline Ht', tsData.map(function(d) {{ return d.sl_secondary_height; }}), SL_COLOR, SL_FILL),
                            lineDataset('NDBC Ht',     tsData.map(function(d) {{ return d.nb_secondary_height; }}), NB_COLOR, NB_FILL),
                        ]
                    }},
                    options: {{
                        responsive: true, maintainAspectRatio: false,
                        interaction: {{ mode: 'index', intersect: false }},
                        plugins: {{
                            legend: {{ labels: {{ color: '#94a3b8', font: {{ family: MONO, size: 10 }}, boxWidth: 10 }} }},
                            tooltip: tooltipDefaults('ft'),
                        }},
                        scales: {{ x: xAxis(false), y: yAxis('ft') }}
                    }}
                }});

                var ctxPer = document.getElementById('chart-s-per-{loc}').getContext('2d');
                charts['s-per'] = new Chart(ctxPer, {{
                    type: 'line',
                    data: {{
                        labels: labels,
                        datasets: [
                            lineDataset('Surfline Period', tsData.map(function(d) {{ return d.sl_secondary_period; }}), SL_COLOR),
                            lineDataset('NDBC Period',     tsData.map(function(d) {{ return d.nb_secondary_period; }}), NB_COLOR),
                        ]
                    }},
                    options: {{
                        responsive: true, maintainAspectRatio: false,
                        interaction: {{ mode: 'index', intersect: false }},
                        plugins: {{
                            legend: {{ labels: {{ color: '#94a3b8', font: {{ family: MONO, size: 10 }}, boxWidth: 10 }} }},
                            tooltip: tooltipDefaults('s'),
                        }},
                        scales: {{ x: xAxis(false), y: yAxis('s', {{ beginAtZero: false }}) }}
                    }}
                }});

                var ctxDir = document.getElementById('chart-s-dir-{loc}').getContext('2d');
                charts['s-dir'] = new Chart(ctxDir, {{
                    type: 'line',
                    data: {{
                        labels: labels,
                        datasets: [
                            lineDataset('Surfline Dir', tsData.map(function(d) {{ return d.sl_secondary_direction; }}), SL_COLOR),
                            lineDataset('NDBC Dir',     tsData.map(function(d) {{ return d.nb_secondary_direction; }}), NB_COLOR),
                        ]
                    }},
                    options: {{
                        responsive: true, maintainAspectRatio: false,
                        interaction: {{ mode: 'index', intersect: false }},
                        plugins: {{
                            legend: {{ labels: {{ color: '#94a3b8', font: {{ family: MONO, size: 10 }}, boxWidth: 10 }} }},
                            tooltip: tooltipDefaults('°'),
                        }},
                        scales: {{
                            x: xAxis(true),
                            y: {{ ticks: {{ color: TICK, font: {{ family: MONO, size: 10 }}, callback: function(v) {{ return v + '°'; }} }}, grid: {{ color: GRID }}, min: 0, max: 360 }}
                        }}
                    }}
                }});
            }}

            // ── SCATTER ───────────────────────────────────────────────────
            function buildScatter(pts) {{
                destroyIfExists('sc');
                var allX   = pts.map(function(p) {{ return p.x; }});
                var maxVal = allX.length ? Math.max.apply(null, allX) * 1.1 : 10;
                var refLine = [{{x:0,y:0}}, {{x:maxVal,y:maxVal}}];
                var fitLine = slope !== null
                    ? [{{x:0,y:intercept}}, {{x:maxVal,y:slope*maxVal+intercept}}]
                    : [];
                var ctx = document.getElementById('scatter-{loc}').getContext('2d');
                charts['sc'] = new Chart(ctx, {{
                    type: 'scatter',
                    data: {{
                        datasets: [
                            {{ label: 'Readings', data: pts,
                               backgroundColor: 'rgba(56,189,248,0.45)',
                               pointRadius: 3, pointHoverRadius: 5 }},
                            {{ label: 'y = x (perfect)', data: refLine,
                               type: 'line', borderColor: 'rgba(148,163,184,0.35)',
                               borderWidth: 1, borderDash: [4,4],
                               pointRadius: 0, fill: false }},
                            {{ label: 'Fit', data: fitLine,
                               type: 'line', borderColor: NB_COLOR,
                               borderWidth: 1.5, pointRadius: 0, fill: false }},
                        ]
                    }},
                    options: {{
                        responsive: true, maintainAspectRatio: false,
                        plugins: {{
                            legend: {{ labels: {{ color: '#94a3b8', font: {{ family: MONO, size: 11 }}, boxWidth: 12 }} }},
                            tooltip: {{
                                backgroundColor: '#0f172a', titleColor: '#94a3b8',
                                bodyColor: '#e2e8f0', borderColor: '#1e293b', borderWidth: 1,
                                titleFont: {{ family: MONO, size: 11 }},
                                bodyFont:  {{ family: MONO, size: 11 }},
                                callbacks: {{
                                    label: function(c) {{
                                        if (c.datasetIndex !== 0) return null;
                                        return 'NDBC ' + c.parsed.x.toFixed(1) + 'ft → SL ' + c.parsed.y.toFixed(1) + 'ft';
                                    }}
                                }}
                            }},
                        }},
                        scales: {{
                            x: {{ ticks: {{ color:TICK, font:{{family:MONO,size:10}}, callback:function(v){{return v+'ft';}} }},
                                  grid:{{color:GRID}}, beginAtZero:true,
                                  title:{{display:true,text:'NDBC (ft)',color:TICK,font:{{family:MONO,size:10}}}} }},
                            y: {{ ticks: {{ color:TICK, font:{{family:MONO,size:10}}, callback:function(v){{return v+'ft';}} }},
                                  grid:{{color:GRID}}, beginAtZero:true,
                                  title:{{display:true,text:'Surfline (ft)',color:TICK,font:{{family:MONO,size:10}}}} }},
                        }}
                    }}
                }});
            }}

            // ── SHOW / HIDE helpers ───────────────────────────────────────
            var allPanels = ['ts-primary-{loc}','ts-secondary-{loc}','sc-{loc}'];

            function showOnly(id) {{
                allPanels.forEach(function(p) {{
                    document.getElementById(p).style.display = p === id ? 'block' : 'none';
                }});
            }}

            // ── REGISTER spot handler ─────────────────────────────────────
            if (!window._slappViews) window._slappViews = {{}};
            window._slappViews['{loc}'] = {{
                switchTo: function(mode) {{
                    var section = document.getElementById('{loc}');
                    var btns = section.querySelectorAll('.tab-btn');
                    btns.forEach(function(b) {{ b.classList.remove('active'); }});
                    var idx = {{'primary':0,'secondary':1,'scatter':2}};
                    if (idx[mode] !== undefined) btns[idx[mode]].classList.add('active');

                    if (mode === 'primary') {{
                        showOnly('ts-primary-{loc}');
                        buildPrimary();
                    }} else if (mode === 'secondary') {{
                        showOnly('ts-secondary-{loc}');
                        buildSecondary();
                    }} else if (mode === 'scatter') {{
                        showOnly('sc-{loc}');
                        if (!charts['sc']) buildScatter(scatterP);
                    }}
                }}
            }};

            window.switchView = function(spotId, mode) {{
                if (window._slappViews && window._slappViews[spotId]) {{
                    window._slappViews[spotId].switchTo(mode);
                }}
            }};

            document.addEventListener('DOMContentLoaded', function() {{
                buildPrimary();
            }});
        }})();
        </script>
        '''

        # Summary row
        ph  = s['primary_height']
        sh  = s['secondary_height']
        pp  = s['primary_period']
        pd_ = s['primary_direction']
        r2_disp = f'{r2:.2f}' if r2 is not None else '—'
        summary_rows += f'''<tr>
            <td class="spot-name">{label}</td>
            <td>{ph["mae"] if ph["n"] else "—"}ft</td>
            <td class="{bias_class(ph["bias"])}">{fmt(ph["bias"], "ft") if ph["n"] else "—"}</td>
            <td>{pp["mae"] if pp["n"] else "—"}s</td>
            <td class="{bias_class(pd_["bias"])}">{fmt(pd_["bias"], "°", 0) if pd_["n"] else "—"}</td>
            <td>{sh["mae"] if sh["n"] else "—"}ft</td>
            <td class="{bias_class(sh["bias"])}">{fmt(sh["bias"], "ft") if sh["n"] else "—"}</td>
            <td class="neutral">{r2_disp}</td>
            <td>{r["n_pairs"]}</td>
        </tr>'''

    weekly_html = render_weekly_section(recent_results) if recent_results else ''
    weekly_nav  = '<a href="#weekly">Last 7 Days</a>' if weekly_html else ''

    return f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>SLAPP / Wave Data Evaluation</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@300;400;500&family=Syne:wght@400;600;800&display=swap" rel="stylesheet">
<script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.1/chart.umd.min.js"></script>
<style>
    *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
    :root {{
        --bg:      #080e1a; --surface: #0d1625; --border: #1a2740;
        --text:    #e2e8f0; --muted:   #475569; --subtle: #94a3b8;
        --blue:    #38bdf8; --orange:  #f97316; --green:  #34d399;
    }}
    html {{ scroll-behavior: smooth; }}
    body {{
        background: var(--bg); color: var(--text);
        font-family: 'IBM Plex Mono', monospace;
        font-size: 13px; line-height: 1.6; min-height: 100vh;
    }}
    header {{
        border-bottom: 1px solid var(--border);
        padding: 3rem 3rem 2rem; position: relative; overflow: hidden;
    }}
    header::before {{
        content: ''; position: absolute; top: -60px; left: -60px;
        width: 400px; height: 400px;
        background: radial-gradient(circle, rgba(56,189,248,0.06) 0%, transparent 70%);
        pointer-events: none;
    }}
    .header-label {{ font-size:10px; letter-spacing:.2em; text-transform:uppercase; color:var(--blue); margin-bottom:.75rem; }}
    h1 {{ font-family:'Syne',sans-serif; font-size:clamp(2rem,5vw,3.5rem); font-weight:800; line-height:1; color:var(--text); margin-bottom:.5rem; }}
    h1 span {{ color: var(--blue); }}
    .header-sub {{ color:var(--subtle); font-size:12px; margin-top:.75rem; }}
    .header-meta {{ margin-top:1.5rem; display:flex; gap:2rem; flex-wrap:wrap; }}
    .meta-item {{ display:flex; flex-direction:column; gap:2px; }}
    .meta-label {{ font-size:10px; color:var(--muted); letter-spacing:.1em; text-transform:uppercase; }}
    .meta-value {{ font-size:13px; color:var(--blue); }}
    nav {{ display:flex; gap:0; border-bottom:1px solid var(--border); padding:0 3rem; overflow-x:auto; }}
    nav a {{ text-decoration:none; color:var(--muted); font-size:11px; letter-spacing:.05em; padding:.85rem 1.25rem; border-bottom:2px solid transparent; transition:color .15s,border-color .15s; white-space:nowrap; }}
    nav a:hover {{ color:var(--text); border-color:var(--border); }}
    main {{ padding:2rem 3rem 4rem; max-width:1400px; }}
    .summary-section {{ margin-bottom:3rem; }}
    .section-title {{ font-family:'Syne',sans-serif; font-size:11px; font-weight:600; letter-spacing:.15em; text-transform:uppercase; color:var(--muted); margin-bottom:1rem; padding-bottom:.5rem; border-bottom:1px solid var(--border); }}
    .summary-table {{ width:100%; border-collapse:collapse; }}
    .summary-table th {{ font-size:10px; letter-spacing:.1em; text-transform:uppercase; color:var(--muted); text-align:left; padding:.6rem 1rem; border-bottom:1px solid var(--border); }}
    .summary-table td {{ padding:.7rem 1rem; border-bottom:1px solid #111d2e; font-size:12px; }}
    .summary-table tr:last-child td {{ border-bottom:none; }}
    .summary-table .spot-name {{ font-family:'Syne',sans-serif; font-weight:600; color:var(--text); }}
    .spot-section {{ margin-bottom:3rem; background:var(--surface); border:1px solid var(--border); border-radius:4px; overflow:hidden; }}
    .spot-header {{ display:flex; align-items:baseline; gap:1rem; padding:1.25rem 1.5rem; border-bottom:1px solid var(--border); background:linear-gradient(90deg,#0d1625 0%,#080e1a 100%); }}
    .spot-header h2 {{ font-family:'Syne',sans-serif; font-size:1.3rem; font-weight:800; color:var(--text); }}
    .pair-count {{ font-size:10px; color:var(--muted); letter-spacing:.08em; }}
    .spot-grid {{ display:grid; grid-template-columns:1fr 1.4fr; gap:0; }}
    @media (max-width:900px) {{ .spot-grid {{ grid-template-columns:1fr; }} main {{ padding:1.5rem; }} header {{ padding:2rem 1.5rem; }} nav {{ padding:0 1.5rem; }} }}
    .stats-block {{ padding:1.25rem 1.5rem; border-right:1px solid var(--border); }}
    .stats-table {{ width:100%; border-collapse:collapse; }}
    .stats-table th {{ font-size:10px; letter-spacing:.08em; text-transform:uppercase; color:var(--muted); text-align:right; padding:.4rem .6rem; border-bottom:1px solid var(--border); }}
    .stats-table th:first-child {{ text-align:left; }}
    .stats-table td {{ padding:.45rem .6rem; font-size:12px; text-align:right; border-bottom:1px solid #0d1625; color:var(--subtle); }}
    .stats-table td:first-child {{ text-align:left; color:var(--text); font-size:11px; }}
    .stats-table tr:last-child td {{ border-bottom:none; }}
    .pos {{ color:var(--orange) !important; }}
    .neg {{ color:var(--blue)   !important; }}
    .neutral {{ color:var(--green) !important; }}
    .null {{ color:var(--muted); }}
    .legend {{ margin-top:1rem; font-size:10px; color:var(--muted); display:flex; flex-direction:column; gap:3px; }}
    .pos-legend::before {{ content:'▲ '; color:var(--orange); }}
    .neg-legend::before {{ content:'▼ '; color:var(--blue); }}
    .chart-block {{ padding:1.25rem 1.5rem; display:flex; flex-direction:column; gap:.75rem; min-width:0; }}
    .chart-wrap {{ width:100%; }}
    .chart-tabs {{ display:flex; gap:.5rem; flex-wrap:wrap; }}
    .tab-btn {{ background:none; border:1px solid var(--border); color:var(--muted); font-family:'IBM Plex Mono',monospace; font-size:10px; letter-spacing:.08em; padding:.35rem .75rem; cursor:pointer; transition:all .15s; border-radius:2px; }}
    .tab-btn:hover {{ color:var(--text); border-color:var(--subtle); }}
    .tab-btn.active {{ background:var(--border); color:var(--blue); border-color:var(--blue); }}
    .scatter-meta {{ display:flex; align-items:center; gap:1rem; margin-bottom:.4rem; }}
    .r2-badge {{ font-size:11px; color:var(--green); border:1px solid rgba(52,211,153,.3); padding:.15rem .5rem; border-radius:2px; }}
    .fit-eq {{ font-size:10px; color:var(--muted); }}
    .dir-note {{ font-size:10px; color:var(--muted); margin-bottom:.4rem; font-style:italic; }}
    footer {{ border-top:1px solid var(--border); padding:1.5rem 3rem; font-size:11px; color:var(--muted); display:flex; justify-content:space-between; flex-wrap:wrap; gap:.5rem; }}
    footer span {{ color:var(--blue); }}
    .weekly-section {{ margin-bottom:3rem; }}
    .weekly-grid {{ display:grid; grid-template-columns:repeat(3,1fr); gap:1rem; }}
    @media (max-width:900px) {{ .weekly-grid {{ grid-template-columns:1fr 1fr; }} }}
    @media (max-width:600px) {{ .weekly-grid {{ grid-template-columns:1fr; }} }}
    .weekly-chart-card {{ background:var(--surface); border:1px solid var(--border); border-radius:4px; padding:.75rem 1rem; }}
    .weekly-chart-title {{ font-family:'Syne',sans-serif; font-size:11px; font-weight:600; color:var(--text); margin-bottom:.5rem; }}
    .weekly-chart-meta {{ color:var(--muted); font-weight:400; font-family:'IBM Plex Mono',monospace; font-size:10px; }}
    .weekly-chart-wrap {{ position:relative; height:160px; }}
    .weekly-no-data {{ color:var(--muted); font-size:12px; padding:.5rem 0; }}
</style>
</head>
<body>

<header>
    <div class="header-label">SLAPP · Wave Data Pipeline</div>
    <h1>NDBC <span>vs</span> Surfline</h1>
    <p class="header-sub">Comparing raw buoy spectral data against Surfline LOTUS nearshore estimates</p>
    <div class="header-meta">
        <div class="meta-item"><span class="meta-label">Generated</span><span class="meta-value">{generated}</span></div>
        <div class="meta-item"><span class="meta-label">Spots</span><span class="meta-value">{len(results)}</span></div>
        <div class="meta-item"><span class="meta-label">Bias direction</span><span class="meta-value">NDBC − Surfline</span></div>
        <div class="meta-item"><span class="meta-label">Match window</span><span class="meta-value">±{MATCH_TOLERANCE_MINUTES}min</span></div>
    </div>
</header>

<nav>
    {weekly_nav}
    <a href="#summary">All-Time Summary</a>
    {"".join(f'<a href="#{r["location"]}">{SPOT_LABELS.get(r["location"], r["location"])}</a>' for r in results)}
</nav>

<main>
    {weekly_html}
    <section class="summary-section" id="summary">
        <div class="section-title">All Spots — Primary &amp; Secondary Swell Comparison</div>
        <table class="summary-table">
            <thead>
                <tr>
                    <th>Spot</th>
                    <th>Primary Ht MAE</th><th>Primary Ht Bias</th>
                    <th>Primary Period MAE</th><th>Primary Dir Bias</th>
                    <th>Secondary Ht MAE</th><th>Secondary Ht Bias</th>
                    <th>Primary R²</th><th>N Pairs</th>
                </tr>
            </thead>
            <tbody>{summary_rows}</tbody>
        </table>
    </section>

    {spot_sections}
</main>

<footer>
    <div>SLAPP evaluation pipeline · NDBC realtime2 spectral data vs Surfline LOTUS</div>
    <div>Generated <span>{generated}</span></div>
</footer>

</body>
</html>'''


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description='Evaluate NDBC vs Surfline LOTUS')
    parser.add_argument('spot', nargs='?', default=None)
    args = parser.parse_args()

    target_spots = [args.spot] if args.spot else SPOTS
    if args.spot and args.spot not in SPOTS:
        print(f"Unknown spot '{args.spot}'. Options: {', '.join(SPOTS)}")
        sys.exit(1)

    conn = get_connection()
    print(f"Connected. Analyzing {len(target_spots)} spot(s)...\n")

    results = []
    for loc in target_spots:
        rows = fetch_readings(conn, loc)
        if not rows:
            print(f"  {loc}: no data")
            continue
        result = analyze_spot(loc, rows)
        if result:
            results.append(result)
            s  = result['stats']
            ph = s['primary_height']
            r2 = result['r2_primary']
            print(f"  {SPOT_LABELS.get(loc, loc)}: {result['n_pairs']} pairs | "
                  f"primary ht MAE={ph['mae']}ft bias={ph['bias']}ft R²={r2}")
        else:
            print(f"  {loc}: no matched pairs")

    print("\nAnalyzing last 7 days...")
    recent_results = []
    for loc in target_spots:
        rows = fetch_readings_recent(conn, loc)
        if not rows:
            continue
        result = analyze_spot_recent(loc, rows)
        if result:
            recent_results.append(result)
            print(f"  {SPOT_LABELS.get(loc, loc)}: {result['n_pairs']} pairs")

    conn.close()

    if not results:
        print("No results to render.")
        sys.exit(0)

    output_path = os.path.join(os.path.dirname(__file__), 'report.html')
    with open(output_path, 'w') as f:
        f.write(render_html(results, target_spots, recent_results or None))

    print(f"\nReport written to {output_path}")


if __name__ == '__main__':
    main()