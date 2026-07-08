"""
evaluation/evaluate.py

Compares public data sources (NDBC, CDIP, ...) against Surfline LOTUS ground
truth. Queries evaluation.swell_readings, computes per-spot statistics for
each comparison source, and renders a self-contained HTML report at
evaluation/report.html.

Every comparison source is matched independently against the ground-truth
source (Surfline) — sources are never matched against each other. Adding a
new source (e.g. cdip_buoy) should only require a new entry in
COMPARISON_SOURCES below, no other code changes.

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
# Source registry — the single place that knows what's being compared
# ---------------------------------------------------------------------------
# 'kind': 'db' sources are fetched from evaluation.swell_readings.
# 'kind': 'virtual' sources are computed on the fly from another source's rows
# via spec['fn'](row) -> dict of field overrides (used for model outputs —
# nothing registers a virtual source yet, this is the interface contract for
# when models/model_1_empirical.py etc. land).

GROUND_TRUTH = {'id': 'surfline_lotus', 'label': 'Surfline', 'color': '#38bdf8', 'fill': 'rgba(56,189,248,0.08)'}

COMPARISON_SOURCES = [
    {'id': 'ndbc_buoy', 'label': 'NDBC', 'color': '#f97316', 'fill': 'rgba(249,115,22,0.08)', 'kind': 'db'},
    {'id': 'cdip_buoy', 'label': 'CDIP', 'color': '#a78bfa', 'fill': 'rgba(167,139,250,0.08)', 'kind': 'db'},
]

SWELL_FIELDS = [
    'primary_swell_height', 'primary_swell_period', 'primary_swell_direction',
    'secondary_swell_height', 'secondary_swell_period', 'secondary_swell_direction',
]

def display_sources(comparison_sources):
    """Ground truth + comparison sources, in the order charts should render them."""
    return [GROUND_TRUTH] + comparison_sources

def db_source_ids(comparison_sources):
    """Every source id that needs to be fetched from Postgres (ground truth + db-kind sources)."""
    return [GROUND_TRUTH['id']] + [s['id'] for s in comparison_sources if s['kind'] == 'db']


# ---------------------------------------------------------------------------
# DB
# ---------------------------------------------------------------------------

def get_connection():
    db_url = os.environ.get('DATABASE_URL')
    if not db_url:
        print("DATABASE_URL not set.")
        sys.exit(1)
    return psycopg2.connect(db_url, cursor_factory=psycopg2.extras.RealDictCursor)


def fetch_readings(conn, location, source_ids):
    with conn.cursor() as cur:
        cur.execute("""
            SELECT source, timestamp,
                   primary_swell_height, primary_swell_period, primary_swell_direction,
                   secondary_swell_height, secondary_swell_period, secondary_swell_direction
            FROM evaluation.swell_readings
            WHERE location = %s
              AND source = ANY(%s)
            ORDER BY timestamp ASC
        """, (location, source_ids))
        return cur.fetchall()


def fetch_readings_recent(conn, location, source_ids, days=7):
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)
    with conn.cursor() as cur:
        cur.execute("""
            SELECT source, timestamp,
                   primary_swell_height, primary_swell_period, primary_swell_direction
            FROM evaluation.swell_readings
            WHERE location = %s
              AND source = ANY(%s)
              AND timestamp >= %s
            ORDER BY timestamp ASC
        """, (location, source_ids, cutoff))
        return cur.fetchall()


def materialize_virtual_sources(rows, comparison_sources):
    """
    For each 'virtual' comparison source, apply its fn to its base_source's
    rows to produce synthetic rows tagged with the virtual source's id, so
    match_readings/analyze_spot never need to know a source isn't DB-backed.
    """
    synthetic = []
    for spec in comparison_sources:
        if spec.get('kind') != 'virtual':
            continue
        base_rows = [r for r in rows if r['source'] == spec['base_source']]
        for r in base_rows:
            new_row = dict(r)
            new_row.update(spec['fn'](r))
            new_row['source'] = spec['id']
            synthetic.append(new_row)
    return synthetic


def fetch_slapp_stats(conn):
    """Fetch slapp app usage statistics from the main app tables."""
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) FROM auth.users")
            total_users = cur.fetchone()['count']

            cur.execute("""
                SELECT
                    COUNT(*) as total_sessions,
                    ROUND(COALESCE(SUM(EXTRACT(EPOCH FROM (session_ended_at - session_started_at)))/3600.0, 0)::numeric, 1) as total_hours,
                    ROUND(AVG(fun_rating)::numeric, 2) as avg_stoke
                FROM surf_sessions_duplicate
            """)
            row = cur.fetchone()
            total_sessions = row['total_sessions']
            total_hours    = float(row['total_hours']) if row['total_hours'] is not None else 0.0
            avg_stoke      = float(row['avg_stoke'])   if row['avg_stoke']   is not None else None

            cur.execute("""
                SELECT COUNT(*) as week_sessions, COUNT(DISTINCT user_id) as week_active_users
                FROM surf_sessions_duplicate
                WHERE session_started_at >= NOW() - INTERVAL '7 days'
            """)
            week_row = cur.fetchone()
            week_sessions      = week_row['week_sessions']
            week_active_users  = week_row['week_active_users']

            cur.execute("""
                SELECT
                    COALESCE(
                        u.raw_user_meta_data->>'display_name',
                        NULLIF(TRIM(COALESCE(u.raw_user_meta_data->>'first_name','') || ' ' || COALESCE(u.raw_user_meta_data->>'last_name','')), ''),
                        split_part(u.email, '@', 1)
                    ) as display_name,
                    COUNT(*) as session_count
                FROM surf_sessions_duplicate s
                JOIN auth.users u ON s.user_id = u.id
                WHERE s.session_started_at >= NOW() - INTERVAL '7 days'
                GROUP BY u.id, u.raw_user_meta_data, u.email
                ORDER BY session_count DESC
            """)
            week_by_user = [{'display_name': r['display_name'], 'count': r['session_count']}
                            for r in cur.fetchall()]

            cur.execute("""
                SELECT location, COUNT(*) as cnt
                FROM surf_sessions_duplicate
                WHERE session_started_at >= NOW() - INTERVAL '7 days'
                GROUP BY location ORDER BY cnt DESC LIMIT 1
            """)
            top_spot_row = cur.fetchone()
            top_spot = top_spot_row['location'] if top_spot_row else None

            cur.execute("SELECT COUNT(*) FROM session_shakas")
            total_shakas = cur.fetchone()['count']

        return {
            'total_users':       total_users,
            'total_sessions':    total_sessions,
            'total_hours':       total_hours,
            'avg_stoke':         avg_stoke,
            'total_shakas':      total_shakas,
            'week_sessions':     week_sessions,
            'week_active_users': week_active_users,
            'week_by_user':      week_by_user,
            'top_spot':          top_spot,
        }
    except Exception as e:
        print(f"  Warning: could not fetch slapp stats ({e})")
        return None


# ---------------------------------------------------------------------------
# Matching
# ---------------------------------------------------------------------------

def match_readings(rows, ground_truth_id, comparison_id, tolerance_minutes=MATCH_TOLERANCE_MINUTES):
    """
    For every ground-truth row, greedily find the nearest comparison-source
    row within tolerance. Two different comparison sources matched against
    the same ground-truth row do NOT need to agree with each other's matched
    timestamp — each comparison source is scored independently against
    ground truth only, never against other comparison sources.
    """
    truth = [r for r in rows if r['source'] == ground_truth_id]
    comp  = [r for r in rows if r['source'] == comparison_id]
    tolerance_seconds = tolerance_minutes * 60
    pairs = []
    for gt in truth:
        gt_ts = gt['timestamp'].replace(tzinfo=timezone.utc) if gt['timestamp'].tzinfo is None else gt['timestamp']
        best, best_delta = None, float('inf')
        for c in comp:
            c_ts = c['timestamp'].replace(tzinfo=timezone.utc) if c['timestamp'].tzinfo is None else c['timestamp']
            delta = abs((gt_ts - c_ts).total_seconds())
            if delta < best_delta and delta <= tolerance_seconds:
                best_delta = delta
                best = c
        if best:
            pairs.append((gt, best))
    return pairs


def match_all_sources(rows, ground_truth_id, comparison_ids):
    """Run match_readings once per comparison source id. Returns {source_id: [(gt, comp), ...]}."""
    return {cid: match_readings(rows, ground_truth_id, cid) for cid in comparison_ids}


# ---------------------------------------------------------------------------
# Stats helpers (source-agnostic — unchanged by the N-way generalization)
# ---------------------------------------------------------------------------

def direction_delta(ground_truth_val, comparison_val):
    if ground_truth_val is None or comparison_val is None:
        return None
    return (comparison_val - ground_truth_val + 180) % 360 - 180

def safe_delta(comparison_val, ground_truth_val):
    if comparison_val is None or ground_truth_val is None:
        return None
    return float(comparison_val) - float(ground_truth_val)

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
    if row is None:
        return None
    v = row[key]
    return float(v) if v is not None else None

def _source_stats(gt, comp):
    """One comparison source's full stat block, given its (gt, comp) pairs."""
    p_height_deltas, p_period_deltas, p_dir_deltas = [], [], []
    s_height_deltas, s_period_deltas, s_dir_deltas = [], [], []
    scatter_primary, scatter_secondary = [], []

    for gt_row, c_row in comp:
        p_height_deltas.append(safe_delta(c_row['primary_swell_height'],   gt_row['primary_swell_height']))
        p_period_deltas.append(safe_delta(c_row['primary_swell_period'],   gt_row['primary_swell_period']))
        p_dir_deltas.append(direction_delta(gt_row['primary_swell_direction'], c_row['primary_swell_direction']))
        s_height_deltas.append(safe_delta(c_row['secondary_swell_height'], gt_row['secondary_swell_height']))
        s_period_deltas.append(safe_delta(c_row['secondary_swell_period'], gt_row['secondary_swell_period']))
        s_dir_deltas.append(direction_delta(gt_row['secondary_swell_direction'], c_row['secondary_swell_direction']))

        if c_row['primary_swell_height'] is not None and gt_row['primary_swell_height'] is not None:
            scatter_primary.append({'x': fv(c_row, 'primary_swell_height'), 'y': fv(gt_row, 'primary_swell_height')})
        if c_row['secondary_swell_height'] is not None and gt_row['secondary_swell_height'] is not None:
            scatter_secondary.append({'x': fv(c_row, 'secondary_swell_height'), 'y': fv(gt_row, 'secondary_swell_height')})

    px = [p['x'] for p in scatter_primary]
    py = [p['y'] for p in scatter_primary]
    r2_primary, slope_primary, intercept_primary = compute_r2(px, py)

    return {
        'n_pairs': len(comp),
        'stats': {
            'primary_height':      compute_stats(p_height_deltas),
            'primary_period':      compute_stats(p_period_deltas),
            'primary_direction':   compute_stats(p_dir_deltas),
            'secondary_height':    compute_stats(s_height_deltas),
            'secondary_period':    compute_stats(s_period_deltas),
            'secondary_direction': compute_stats(s_dir_deltas),
        },
        'scatter_primary':   scatter_primary,
        'scatter_secondary': scatter_secondary,
        'r2_primary':        r2_primary,
        'slope_primary':     slope_primary,
        'intercept_primary': intercept_primary,
    }

def _build_time_series(rows, ground_truth_id, comparison_ids, matches):
    """
    One shared ground-truth timestamp axis per spot. Each source fills in its
    value where it has a match, None elsewhere — Chart.js spanGaps handles
    the gaps. Keys are named f'{source_id}_{field}' for every source
    (including ground truth), so the JS side can do d[s.id + '_' + field]
    uniformly for any source.
    """
    gt_by_ts = {}
    comp_by_ts = {cid: {} for cid in comparison_ids}
    for cid, pairs in matches.items():
        for gt_row, c_row in pairs:
            ts = gt_row['timestamp']
            gt_by_ts[ts] = gt_row
            comp_by_ts[cid][ts] = c_row

    time_series = []
    for ts in sorted(gt_by_ts.keys()):
        gt_row = gt_by_ts[ts]
        entry = {'ts': ts.isoformat()}
        for field in SWELL_FIELDS:
            entry[f"{ground_truth_id}_{field}"] = fv(gt_row, field)
        for cid in comparison_ids:
            c_row = comp_by_ts[cid].get(ts)
            for field in SWELL_FIELDS:
                entry[f"{cid}_{field}"] = fv(c_row, field)
        time_series.append(entry)
    return time_series

def analyze_spot(location, rows, comparison_sources):
    ids = [s['id'] for s in comparison_sources]
    matches = match_all_sources(rows, GROUND_TRUTH['id'], ids)

    if not any(matches.values()):
        return None

    sources = {}
    for s in comparison_sources:
        cid = s['id']
        block = _source_stats(GROUND_TRUTH['id'], matches[cid])
        block['label'] = s['label']
        block['color'] = s['color']
        sources[cid] = block

    return {
        'location':     location,
        'n_pairs':      max((b['n_pairs'] for b in sources.values()), default=0),
        'sources':      sources,
        'time_series':  _build_time_series(rows, GROUND_TRUTH['id'], ids, matches),
    }


def analyze_spot_recent(location, rows, comparison_sources):
    """Extract matched pairs for the last-N-days primary-height chart."""
    tz = ZoneInfo(SPOT_TIMEZONES.get(location, 'UTC'))
    ids = [s['id'] for s in comparison_sources]
    matches = match_all_sources(rows, GROUND_TRUTH['id'], ids)

    if not any(matches.values()):
        return None

    gt_by_ts = {}
    comp_by_ts = {cid: {} for cid in ids}
    for cid, pairs in matches.items():
        for gt_row, c_row in pairs:
            gt_by_ts[gt_row['timestamp']] = gt_row
            comp_by_ts[cid][gt_row['timestamp']] = c_row

    pair_rows = []
    for ts in sorted(gt_by_ts.keys()):
        gt_row = gt_by_ts[ts]
        gt_ts = ts.replace(tzinfo=timezone.utc) if ts.tzinfo is None else ts
        local_ts = gt_ts.astimezone(tz)
        entry = {
            'date':    local_ts.strftime('%b %-d'),
            'slot':    local_ts.strftime('%-I%p').lower(),
            'tz_abbr': local_ts.strftime('%Z'),
            f"{GROUND_TRUTH['id']}_height": fv(gt_row, 'primary_swell_height'),
        }
        for cid in ids:
            entry[f"{cid}_height"] = fv(comp_by_ts[cid].get(ts), 'primary_swell_height')
        pair_rows.append(entry)

    tz_abbr = pair_rows[-1]['tz_abbr'] if pair_rows else ''
    return {
        'location': location,
        'n_pairs':  max(len(p) for p in matches.values()) if matches else 0,
        'tz_abbr':  tz_abbr,
        'pairs':    pair_rows,
    }


# ---------------------------------------------------------------------------
# HTML renderer
# ---------------------------------------------------------------------------

def render_weekly_section(recent_results, comparison_sources, days=7):
    """Returns the HTML for the Last 7 Days grid of primary height charts."""
    now   = datetime.now(timezone.utc)
    start = now - timedelta(days=days)
    date_range = f"{start.strftime('%b %-d')} → {now.strftime('%b %-d, %Y')}"
    sources = display_sources(comparison_sources)

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

        datasets_js = ''
        for s in sources:
            data_json = json.dumps([p.get(f"{s['id']}_height") for p in pairs])
            datasets_js += f'''
                        {{ label: '{s["label"]}', data: {data_json},
                           borderColor: '{s["color"]}', backgroundColor: '{s["fill"]}',
                           borderWidth: 1.5, pointRadius: 0, tension: 0.3, fill: true, spanGaps: true }},'''

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
                    datasets: [{datasets_js}
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

def render_slapp_section(stats):
    """Render the Slapp app activity section for the weekly report."""
    if not stats:
        return ''

    def stat_card(label, value, unit=''):
        return f'''
        <div class="slapp-card">
            <div class="slapp-card-value">{value}<span class="slapp-card-unit">{unit}</span></div>
            <div class="slapp-card-label">{label}</div>
        </div>'''

    stoke_display = f'{stats["avg_stoke"]:.1f} / 10' if stats['avg_stoke'] is not None else '—'
    hours_display = f'{stats["total_hours"]:.0f}'

    cards_html = (
        stat_card('Registered Users',    stats['total_users'])
      + stat_card('Sessions All-Time',   stats['total_sessions'])
      + stat_card('Hours in the Water',  hours_display, 'h')
      + stat_card('Avg Stoke',           stoke_display)
      + stat_card('Shakas Given',        stats['total_shakas'])
    )

    # This week activity
    week_count = stats['week_sessions']
    if week_count == 0:
        week_body = '<p class="slapp-flat-week">Flat week — no sessions logged. Time to fix some bugs. 🤙</p>'
    else:
        user_lines = ''.join(
            f'<div class="slapp-week-user"><span class="slapp-week-name">{u["display_name"]}</span>'
            f'<span class="slapp-week-count">{u["count"]} session{"s" if u["count"] != 1 else ""}</span></div>'
            for u in stats['week_by_user']
        )
        top_spot_line = (
            f'<div class="slapp-week-spot">Top spot: <span class="slapp-week-spot-name">{stats["top_spot"]}</span></div>'
            if stats['top_spot'] else ''
        )
        week_body = f'''
        <div class="slapp-week-users">{user_lines}</div>
        {top_spot_line}'''

    return f'''
    <section class="slapp-section" id="slapp">
        <div class="section-title">Slapp — App Activity</div>
        <div class="slapp-grid">{cards_html}</div>
        <div class="slapp-week-box">
            <div class="slapp-week-header">This Week
                <span class="slapp-week-meta">{week_count} session{"s" if week_count != 1 else ""} · {stats["week_active_users"]} active user{"s" if stats["week_active_users"] != 1 else ""}</span>
            </div>
            {week_body}
        </div>
    </section>'''

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

def render_html(results, target_spots, comparison_sources, recent_results=None, slapp_stats=None):
    from datetime import datetime
    generated = datetime.now().strftime('%B %d, %Y at %H:%M')
    sources = display_sources(comparison_sources)
    comparison_labels = ' / '.join(s['label'] for s in comparison_sources)

    spot_sections = ''
    summary_rows  = ''

    for r in results:
        loc   = r['location']
        label = SPOT_LABELS.get(loc, loc)
        ts_json = json.dumps(r['time_series'])

        # ── Stats blocks: one per comparison source ──────────────────────
        stats_blocks_html = ''
        for cid, block in r['sources'].items():
            s_label = block['label']
            st = block['stats']

            def stat_row(metric_key, label_text, unit='ft', st=st):
                m = st[metric_key]
                if m['n'] == 0:
                    return f'<tr><td>{label_text}</td><td colspan="3" class="null">no data</td></tr>'
                u = unit
                return f'''<tr>
                    <td>{label_text}</td>
                    <td>{m["mae"]:.2f}{u}</td>
                    <td class="{bias_class(m["bias"])}">{fmt(m["bias"], u)}</td>
                    <td>{m["std"]:.2f}{u}</td>
                </tr>'''

            stats_blocks_html += f'''
                <div class="source-stats-block">
                    <div class="source-stats-label">{s_label} <span class="pair-count">{block["n_pairs"]} matched</span></div>
                    <table class="stats-table">
                        <thead>
                            <tr>
                                <th>Metric</th><th>MAE</th>
                                <th>Bias ({s_label} − Surfline)</th><th>Std Dev</th>
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
                </div>'''

        # ── Scatter source picker (only matters once >1 comparison source exists) ──
        scatter_tabs_html = ''.join(
            f'<button class="tab-btn scatter-src-btn{" active" if i == 0 else ""}" '
            f'data-loc="{loc}" data-src="{cid}" onclick="switchScatterSource(\'{loc}\', \'{cid}\')">{block["label"]}</button>'
            for i, (cid, block) in enumerate(r['sources'].items())
        )
        scatter_data_json = json.dumps({
            cid: {
                'points': block['scatter_primary'],
                'r2': block['r2_primary'], 'slope': block['slope_primary'], 'intercept': block['intercept_primary'],
                'color': block['color'], 'label': block['label'],
            }
            for cid, block in r['sources'].items()
        })
        first_cid = next(iter(r['sources']))
        first_r2 = r['sources'][first_cid]['r2_primary']
        r2_str = f'{first_r2:.2f}' if first_r2 is not None else '—'

        spot_sections += f'''
        <section class="spot-section" id="{loc}">
            <div class="spot-header">
                <h2>{label}</h2>
                <span class="pair-count">{r["n_pairs"]} matched readings</span>
            </div>

            <div class="spot-grid">
                <div class="stats-block">
                    {stats_blocks_html}
                    <div class="legend">
                        <span class="pos-legend">Positive bias → comparison source reads higher than Surfline</span>
                        <span class="neg-legend">Negative bias → comparison source reads lower than Surfline</span>
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
                        <div class="chart-tabs scatter-src-tabs">{scatter_tabs_html}</div>
                        <div class="scatter-meta">
                            <span class="r2-badge" id="r2-badge-{loc}">R² = {r2_str}</span>
                            <span class="fit-eq" id="fit-eq-{loc}"></span>
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
            var tsData      = {ts_json};
            var scatterData = {scatter_data_json};
            var SOURCES     = {json.dumps(sources)};
            var GT_ID       = '{GROUND_TRUTH["id"]}';

            // Chart instances — keyed by role
            var charts = {{}};

            var MONO = "'IBM Plex Mono', monospace";
            var GRID = '#1e293b';
            var TICK = '#475569';

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

            function sourceDatasets(field, withFill) {{
                return SOURCES.map(function(s) {{
                    return lineDataset(
                        s.label,
                        tsData.map(function(d) {{ return d[s.id + '_' + field]; }}),
                        s.color,
                        withFill ? s.fill : null
                    );
                }});
            }}

            // ── PRIMARY: height / period / direction stacked ─────────────
            function buildPrimary() {{
                destroyIfExists('p-ht');
                destroyIfExists('p-per');
                destroyIfExists('p-dir');

                var ctxHt = document.getElementById('chart-p-ht-{loc}').getContext('2d');
                charts['p-ht'] = new Chart(ctxHt, {{
                    type: 'line',
                    data: {{ labels: labels, datasets: sourceDatasets('primary_swell_height', true) }},
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
                    data: {{ labels: labels, datasets: sourceDatasets('primary_swell_period', false) }},
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
                    data: {{ labels: labels, datasets: sourceDatasets('primary_swell_direction', false) }},
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
                    data: {{ labels: labels, datasets: sourceDatasets('secondary_swell_height', true) }},
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
                    data: {{ labels: labels, datasets: sourceDatasets('secondary_swell_period', false) }},
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
                    data: {{ labels: labels, datasets: sourceDatasets('secondary_swell_direction', false) }},
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

            // ── SCATTER (one comparison source at a time, via source tabs) ──
            var currentScatterSrc = Object.keys(scatterData)[0];

            function buildScatter(srcId) {{
                destroyIfExists('sc');
                var d = scatterData[srcId];
                if (!d) return;
                var pts = d.points;
                var allX   = pts.map(function(p) {{ return p.x; }});
                var maxVal = allX.length ? Math.max.apply(null, allX) * 1.1 : 10;
                var refLine = [{{x:0,y:0}}, {{x:maxVal,y:maxVal}}];
                var fitLine = d.slope !== null
                    ? [{{x:0,y:d.intercept}}, {{x:maxVal,y:d.slope*maxVal+d.intercept}}]
                    : [];

                document.getElementById('r2-badge-{loc}').textContent = 'R² = ' + (d.r2 !== null ? d.r2.toFixed(2) : '—');
                document.getElementById('fit-eq-{loc}').textContent = d.slope !== null
                    ? ('y = ' + d.slope.toFixed(2) + 'x ' + (d.intercept >= 0 ? '+' : '') + d.intercept.toFixed(2))
                    : '';

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
                               type: 'line', borderColor: d.color,
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
                                        return d.label + ' ' + c.parsed.x.toFixed(1) + 'ft → SL ' + c.parsed.y.toFixed(1) + 'ft';
                                    }}
                                }}
                            }},
                        }},
                        scales: {{
                            x: {{ ticks: {{ color:TICK, font:{{family:MONO,size:10}}, callback:function(v){{return v+'ft';}} }},
                                  grid:{{color:GRID}}, beginAtZero:true,
                                  title:{{display:true,text:d.label+' (ft)',color:TICK,font:{{family:MONO,size:10}}}} }},
                            y: {{ ticks: {{ color:TICK, font:{{family:MONO,size:10}}, callback:function(v){{return v+'ft';}} }},
                                  grid:{{color:GRID}}, beginAtZero:true,
                                  title:{{display:true,text:'Surfline (ft)',color:TICK,font:{{family:MONO,size:10}}}} }},
                        }}
                    }}
                }});
            }}

            window.switchScatterSource = function(spotId, srcId) {{
                if (spotId !== '{loc}') return;
                currentScatterSrc = srcId;
                var section = document.getElementById('{loc}');
                section.querySelectorAll('.scatter-src-btn').forEach(function(b) {{
                    b.classList.toggle('active', b.getAttribute('data-src') === srcId);
                }});
                buildScatter(srcId);
            }};

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
                    var btns = section.querySelectorAll(':scope > .spot-grid > .chart-block > .chart-tabs > .tab-btn');
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
                        if (!charts['sc']) buildScatter(currentScatterSrc);
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

        # Summary rows — one per (spot, comparison source)
        for cid, block in r['sources'].items():
            st = block['stats']
            ph  = st['primary_height']
            sh  = st['secondary_height']
            pp  = st['primary_period']
            pd_ = st['primary_direction']
            r2  = block['r2_primary']
            r2_disp = f'{r2:.2f}' if r2 is not None else '—'
            summary_rows += f'''<tr>
                <td class="spot-name">{label}</td>
                <td>{block["label"]}</td>
                <td>{ph["mae"] if ph["n"] else "—"}ft</td>
                <td class="{bias_class(ph["bias"])}">{fmt(ph["bias"], "ft") if ph["n"] else "—"}</td>
                <td>{pp["mae"] if pp["n"] else "—"}s</td>
                <td class="{bias_class(pd_["bias"])}">{fmt(pd_["bias"], "°", 0) if pd_["n"] else "—"}</td>
                <td>{sh["mae"] if sh["n"] else "—"}ft</td>
                <td class="{bias_class(sh["bias"])}">{fmt(sh["bias"], "ft") if sh["n"] else "—"}</td>
                <td class="neutral">{r2_disp}</td>
                <td>{block["n_pairs"]}</td>
            </tr>'''

    weekly_html = render_weekly_section(recent_results, comparison_sources) if recent_results else ''
    weekly_nav  = '<a href="#weekly">Last 7 Days</a>' if weekly_html else ''
    slapp_html  = render_slapp_section(slapp_stats)
    slapp_nav   = '<a href="#slapp">App Activity</a>' if slapp_html else ''

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
    .source-stats-block {{ margin-bottom:1.25rem; }}
    .source-stats-block:last-of-type {{ margin-bottom:0; }}
    .source-stats-label {{ font-family:'Syne',sans-serif; font-size:11px; font-weight:600; color:var(--text); margin-bottom:.4rem; display:flex; align-items:baseline; gap:.5rem; }}
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
    .scatter-src-tabs {{ margin-bottom:.25rem; }}
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
    .slapp-section {{ margin-bottom:3rem; }}
    .slapp-grid {{ display:grid; grid-template-columns:repeat(5,1fr); gap:1rem; margin-bottom:1rem; }}
    @media (max-width:900px) {{ .slapp-grid {{ grid-template-columns:repeat(3,1fr); }} }}
    @media (max-width:600px) {{ .slapp-grid {{ grid-template-columns:repeat(2,1fr); }} }}
    .slapp-card {{ background:var(--surface); border:1px solid var(--border); border-radius:4px; padding:1rem 1.25rem; }}
    .slapp-card-value {{ font-family:'Syne',sans-serif; font-size:1.6rem; font-weight:800; color:var(--blue); line-height:1; }}
    .slapp-card-unit {{ font-size:1rem; font-weight:400; color:var(--subtle); margin-left:2px; }}
    .slapp-card-label {{ font-size:10px; color:var(--muted); letter-spacing:.1em; text-transform:uppercase; margin-top:.35rem; }}
    .slapp-week-box {{ background:var(--surface); border:1px solid var(--border); border-radius:4px; padding:1rem 1.25rem; }}
    .slapp-week-header {{ font-family:'Syne',sans-serif; font-size:11px; font-weight:600; color:var(--text); margin-bottom:.75rem; }}
    .slapp-week-meta {{ font-family:'IBM Plex Mono',monospace; font-weight:400; font-size:10px; color:var(--muted); margin-left:.75rem; }}
    .slapp-week-users {{ display:flex; flex-wrap:wrap; gap:.5rem 2rem; margin-bottom:.5rem; }}
    .slapp-week-user {{ display:flex; align-items:baseline; gap:.5rem; }}
    .slapp-week-name {{ color:var(--text); font-size:12px; }}
    .slapp-week-count {{ color:var(--green); font-size:11px; }}
    .slapp-week-spot {{ font-size:11px; color:var(--muted); margin-top:.25rem; }}
    .slapp-week-spot-name {{ color:var(--subtle); }}
    .slapp-flat-week {{ color:var(--muted); font-size:12px; }}
</style>
</head>
<body>

<header>
    <div class="header-label">SLAPP · Wave Data Pipeline</div>
    <h1>{comparison_labels} <span>vs</span> Surfline</h1>
    <p class="header-sub">Comparing public data sources against Surfline LOTUS nearshore estimates</p>
    <div class="header-meta">
        <div class="meta-item"><span class="meta-label">Generated</span><span class="meta-value">{generated}</span></div>
        <div class="meta-item"><span class="meta-label">Spots</span><span class="meta-value">{len(results)}</span></div>
        <div class="meta-item"><span class="meta-label">Bias direction</span><span class="meta-value">source − Surfline</span></div>
        <div class="meta-item"><span class="meta-label">Match window</span><span class="meta-value">±{MATCH_TOLERANCE_MINUTES}min</span></div>
    </div>
</header>

<nav>
    {weekly_nav}
    {slapp_nav}
    <a href="#summary">All-Time Summary</a>
    {"".join(f'<a href="#{r["location"]}">{SPOT_LABELS.get(r["location"], r["location"])}</a>' for r in results)}
</nav>

<main>
    {weekly_html}
    {slapp_html}
    <section class="summary-section" id="summary">
        <div class="section-title">All Spots — Primary &amp; Secondary Swell Comparison</div>
        <table class="summary-table">
            <thead>
                <tr>
                    <th>Spot</th><th>Source</th>
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
    <div>SLAPP evaluation pipeline · public data sources vs Surfline LOTUS</div>
    <div>Generated <span>{generated}</span></div>
</footer>

</body>
</html>'''


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description='Evaluate public data sources vs Surfline LOTUS')
    parser.add_argument('spot', nargs='?', default=None)
    parser.add_argument('--sources', default=None,
                         help='Comma-separated comparison source ids to include (default: all registered)')
    args = parser.parse_args()

    target_spots = [args.spot] if args.spot else SPOTS
    if args.spot and args.spot not in SPOTS:
        print(f"Unknown spot '{args.spot}'. Options: {', '.join(SPOTS)}")
        sys.exit(1)

    comparison_sources = COMPARISON_SOURCES
    if args.sources:
        wanted = set(args.sources.split(','))
        comparison_sources = [s for s in COMPARISON_SOURCES if s['id'] in wanted]
        missing = wanted - {s['id'] for s in comparison_sources}
        if missing:
            print(f"Unknown source id(s): {', '.join(missing)}. Registered: {', '.join(s['id'] for s in COMPARISON_SOURCES)}")
            sys.exit(1)

    ids = [s['id'] for s in comparison_sources]
    fetch_ids = db_source_ids(comparison_sources)

    conn = get_connection()
    print(f"Connected. Analyzing {len(target_spots)} spot(s) against {', '.join(s['label'] for s in comparison_sources)}...\n")
    print("Fetching slapp app stats...")
    slapp_stats = fetch_slapp_stats(conn)

    results = []
    for loc in target_spots:
        rows = fetch_readings(conn, loc, fetch_ids)
        if not rows:
            print(f"  {loc}: no data")
            continue
        rows = rows + materialize_virtual_sources(rows, comparison_sources)
        result = analyze_spot(loc, rows, comparison_sources)
        if result:
            results.append(result)
            summary = ' | '.join(
                f"{block['label']}: {block['n_pairs']} pairs, primary ht MAE={block['stats']['primary_height']['mae']}ft "
                f"bias={block['stats']['primary_height']['bias']}ft R²={block['r2_primary']}"
                for block in result['sources'].values()
            )
            print(f"  {SPOT_LABELS.get(loc, loc)}: {summary}")
        else:
            print(f"  {loc}: no matched pairs")

    print("\nAnalyzing last 7 days...")
    recent_results = []
    for loc in target_spots:
        rows = fetch_readings_recent(conn, loc, fetch_ids)
        if not rows:
            continue
        rows = rows + materialize_virtual_sources(rows, comparison_sources)
        result = analyze_spot_recent(loc, rows, comparison_sources)
        if result:
            recent_results.append(result)
            print(f"  {SPOT_LABELS.get(loc, loc)}: {result['n_pairs']} pairs")

    conn.close()

    if not results:
        print("No results to render.")
        sys.exit(0)

    output_path = os.path.join(os.path.dirname(__file__), 'report.html')
    with open(output_path, 'w') as f:
        f.write(render_html(results, target_spots, comparison_sources, recent_results or None, slapp_stats))

    print(f"\nReport written to {output_path}")


if __name__ == '__main__':
    main()
