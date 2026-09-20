"""Render a forecast report from a run's own artifacts, and nothing else.

`render(run_dir)` reads brief.json, profile.json, summary.json, results.csv and run.json from
one applied run and writes `report.md` plus `claims.json`. Every number in the report is a
claim with a source (file and key), so an assistant's interpretation can be checked against
the evidence and a reader can trace any figure back to the run. The assistant may add
judgment around the report; it may not add numbers to it.
"""
from pathlib import Path
import json
import numpy as np
import pandas as pd

STATUS_TEXT = {
    'passed': 'The method ran and was validated as the chapter describes.',
    'provisional': 'Something ran, but a check the chapter requires could not be done; see "Not done".',
    'needs_evidence': 'No forecast was produced. The evidence below would unlock one.',
}


class Claims:
    def __init__(self):
        self.items = []

    def add(self, label, value, source, key):
        self.items.append(dict(label=label, value=value, source=source, key=key))
        return value

    def num(self, label, value, source, key, fmt='{:,.4g}'):
        if value is None or (isinstance(value, float) and not np.isfinite(value)):
            return 'not available'
        self.add(label, value, source, key)
        return fmt.format(value)


def _load(run_dir):
    run_dir = Path(run_dir)
    def read(name, default=None):
        p = run_dir / name
        return json.loads(p.read_text()) if p.exists() else default
    summary = read('summary.json')
    if summary is None:
        raise FileNotFoundError(f'{run_dir} has no summary.json; run `run.py apply` first')
    table = pd.read_csv(run_dir / 'results.csv') if (run_dir / 'results.csv').exists() else pd.DataFrame()
    return run_dir, read('brief.json'), summary.get('profile') or read('profile.json'), summary, table, read('run.json', {})


def _forecast_block(table, summary, claims, units):
    """The forecast numbers a decision-maker reads: per period, with the band the tool actually produced."""
    if table.empty:
        return ['No results table.']
    cols = set(table.columns)
    point = next((c for c in ('forecast', 'prediction', 'median', 'nowcast', 'units', 'MinT', 'OLS', 'bottom_up') if c in cols), None)
    if 'node' in cols and point in ('MinT', 'OLS', 'bottom_up') and 'timestamp' in cols:
        lines = [f'Reconciled forecasts ({point}) by node; every column adds up across the hierarchy.', '', '| Node | Periods | Sum |', '|---|---|---|']
        for node, g in table.groupby('node'):
            lines.append(f'| {node} | {len(g)} | {claims.num(f"{node} total", float(g[point].sum()), "results.csv", f"sum({point}[{node}])")} |')
        return lines
    if point is None or 'timestamp' not in cols and 'month' not in cols:
        return [f'`results.csv` has {len(table)} rows with columns {list(table.columns)}; see the chapter skill for their meaning.']
    lo, hi = next(((a, b) for a, b in (('band_lower', 'band_upper'), ('conformal_lower', 'conformal_upper'), ('lower', 'upper'), ('scenario_low', 'scenario_high'), ('empirical_q10', 'empirical_q90'), ('q10', 'q90')) if a in cols and b in cols), (None, None))
    nominal = float(summary.get('nominal', 0.8))
    when = 'timestamp' if 'timestamp' in cols else 'month'
    rows = table if 'peak' not in cols else table[table.peak == table.peak.iloc[len(table) // 2]]
    lines = [f'| Period | Forecast ({units}) |' + (f' Range ({lo} to {hi}) |' if lo else ''), '|---|---|' + ('---|' if lo else '')]
    for i, r in rows.head(24).iterrows():
        label = str(r[when])[:10]
        val = claims.num(f'forecast {label}', float(r[point]), 'results.csv', f'{point}[{i}]')
        band = f' {claims.num(f"lower {label}", float(r[lo]), "results.csv", f"{lo}[{i}]")} to {claims.num(f"upper {label}", float(r[hi]), "results.csv", f"{hi}[{i}]")} |' if lo else ''
        lines.append(f'| {label} | {val} |{band}')
    total = float(rows[point].sum())
    lines.append('')
    lines.append(f'Sum over the {len(rows)} periods shown: {claims.num("forecast total", total, "results.csv", f"sum({point})")} {units}.')
    if 'break_scenario' in cols:
        bs = summary.get('break_scenario') or {}
        lines.append('')
        lines.append(f'Level-shift scenario (`break_scenario` column, re-levelled by {claims.num("shift", float(bs.get("shift", 0)), "summary.json", "break_scenario.shift")}): total {claims.num("scenario total", float(rows["break_scenario"].sum()), "results.csv", "sum(break_scenario)")} {units}' + (f', range {claims.num("scenario low total", float(rows["break_scenario_low"].sum()), "results.csv", "sum(break_scenario_low)")} to {claims.num("scenario high total", float(rows["break_scenario_high"].sum()), "results.csv", "sum(break_scenario_high)")}' if 'break_scenario_low' in cols else '') + '. Per period: ' + ', '.join(claims.num(f'scenario {str(r[when])[:10]}', float(r['break_scenario']), 'results.csv', f'break_scenario[{i}]') for i, r in rows.head(24).iterrows()) + '.')
    if lo:
        cov = summary.get('test_interval_coverage') or summary.get('coverage')
        if isinstance(cov, dict):
            sel = summary.get('selected'); cov = cov.get(sel) if sel in cov else None
        if lo == 'band_lower':
            cc = summary.get('conformal_test_coverage'); method = summary.get('band_method')
            lines.append(f'The range is the band the tool delivers (`band_lower/upper`, method: {method}). ' + (summary.get('band_note') or '') + '.' + (f' On the holdout the conformal band covered {claims.num("conformal holdout coverage", float(cc), "summary.json", "conformal_test_coverage")}' if cc is not None else '') + (f' and the model\'s own band {claims.num("measured coverage", float(cov), "summary.json", "test_interval_coverage")}' if cov is not None else '') + f', against a nominal {claims.num("nominal level", nominal, "summary.json", "nominal", fmt="{:.0%}")}.')
        elif lo.startswith('conformal'):
            cc = summary.get('conformal_test_coverage')
            lines.append(f'The band is a split-conformal band at nominal {claims.num("nominal level", nominal, "summary.json", "nominal", fmt="{:.0%}")}, built from the selected model\'s residuals at the selection origins' + (f'; it covered {claims.num("conformal holdout coverage", float(cc), "summary.json", "conformal_test_coverage")} of the holdout' if cc is not None else '') + '.' + (f' The model\'s own band covered {claims.num("measured coverage", float(cov), "summary.json", "test_interval_coverage")} of the holdout.' if cov is not None else ''))
        elif lo.startswith('scenario'):
            lines.append('The range is a scenario band from in-sample errors of the placeholder rule; no coverage was measured.')
        elif cov is not None:
            cc = summary.get('conformal_test_coverage')
            lines.append(f'The band is the model\'s own {lo}/{hi}; its measured coverage on the holdout was {claims.num("measured coverage", float(cov), "summary.json", "test_interval_coverage")} against a nominal {claims.num("nominal level", nominal, "summary.json", "nominal", fmt="{:.0%}")}.' + (f' The conformal band covered {claims.num("conformal holdout coverage", float(cc), "summary.json", "conformal_test_coverage")}, so the model band is shown.' if cc is not None else ''))
    return lines


def _validation_block(summary, claims):
    lines = []
    lb = summary.get('leaderboard')
    if isinstance(lb, list) and lb and not all(isinstance(r, dict) for r in lb):
        lines.append('Method ranking on the holdout: ' + ', '.join(map(str, lb)) + '.'); lb = None
    if isinstance(lb, list) and lb:
        keys = [k for k in ('mae', 'rmse', 'mase', 'rmsse', 'interval_coverage') if k in lb[0]]
        lines += ['| Model | ' + ' | '.join(k.upper() if k != 'interval_coverage' else '80% band coverage' for k in keys) + ' |', '|---|' + '---|' * len(keys)]
        for r in lb[:8]:
            lines.append(f'| {r["model"]} | ' + ' | '.join(claims.num(f'{r["model"]} {k}', r.get(k), 'summary.json', f'leaderboard.{r["model"]}.{k}') for k in keys) + ' |')
        naive = next((r for r in lb if r['model'] in ('Seasonal naive', 'Naive')), None); best = lb[0]
        if naive and best is not naive and naive.get('mae') and best.get('mae'):
            lines.append('')
            lines.append(f'Selected {best["model"]} against the {naive["model"]} baseline: validation MAE {claims.num("selected mae", best["mae"], "summary.json", "leaderboard[0].mae")} vs {claims.num("baseline mae", naive["mae"], "summary.json", "leaderboard.naive.mae")}, a {claims.num("gain over baseline", 1 - best["mae"] / naive["mae"], "summary.json", "derived", fmt="{:.0%}")} improvement at the selection origins.')
    tm = summary.get('test_mae')
    if isinstance(tm, dict) and summary.get('selected') in tm:
        lines.append(f'Final holdout MAE (scored once, never used for selection): {claims.num("holdout mae", tm[summary["selected"]], "summary.json", f"test_mae.{summary["selected"]}")}.')
    elif isinstance(tm, (int, float)):
        lines.append(f'Final holdout MAE: {claims.num("holdout mae", tm, "summary.json", "test_mae")}' + (f' against baseline {claims.num("baseline holdout mae", summary["baseline_mae"], "summary.json", "baseline_mae")}.' if summary.get('baseline_mae') is not None else '.'))
    for key, label in (('validation', 'validation origins'), ('holdout', 'holdout comparison'), ('ablation', 'feature ablation'), ('placebo_space', 'placebo in space'), ('coverage', 'coverage')):
        v = summary.get(key)
        if isinstance(v, list) and v and isinstance(v[0], dict):
            lines.append(f'{label.capitalize()}: {claims.num(f"{key} rows", len(v), "summary.json", f"len({key})", fmt="{:d}")} rows in summary.json under `{key}`.')
    return lines or ['No validation table in this summary; the method does not produce one.']


def _evidence_block(summary, claims):
    """Every scalar number the tool returned, so a chapter whose evidence is a handful of policy metrics still reports them with a source."""
    skip = {'chapter', 'horizon', 'season', 'brief', 'profile', 'leaderboard', 'validation', 'validation_predictions', 'test_mae', 'test_interval_coverage', 'nominal'}
    lines = []
    for key, value in summary.items():
        if key in skip:
            continue
        if isinstance(value, bool) or value is None:
            continue
        if isinstance(value, (int, float)):
            lines.append(f'- {key}: {claims.num(key, value, "summary.json", key)}')
        elif isinstance(value, dict) and value and all(isinstance(v, (int, float)) and not isinstance(v, bool) for v in value.values()) and len(value) <= 12:
            lines.append(f'- {key}: ' + ', '.join(f'{k} {claims.num(f"{key}.{k}", v, "summary.json", f"{key}.{k}")}' for k, v in value.items()))
    return lines or ['- no further scalar evidence']


def _profile_block(profile, claims):
    if not profile or 'observations' not in profile:
        return ['No data profile was produced for this input type.']
    p = profile; s = p['seasonality']; i = p['intermittency']
    lines = [f'{claims.num("observations", p["observations"], "profile.json", "observations", fmt="{:d}")} observations from {p.get("start")} to {p.get("end")}, frequency {p["frequency"].get("frequency")}' + ('' if p['frequency'].get('regular') else ' with gaps') + '.',
             f'Season {claims.num("season", p["season"], "profile.json", "season", fmt="{:d}")} ' + ('detected from the data' if s.get('periods') else 'assumed from the frequency; no seasonal cycle was detected') + '.',
             f'Demand class: {i["quadrant"]} ({claims.num("zero share", i["zero_share"], "profile.json", "intermittency.zero_share", fmt="{:.0%}")} zeros). Trend: {p["trend"].get("direction")}. Outliers flagged: {claims.num("outliers", p["outliers"].get("count", 0), "profile.json", "outliers.count", fmt="{:d}")}.',
             f'Route chosen by the profile: {p["route"]}.']
    if p.get('warnings'):
        lines += ['', 'Profile warnings:'] + [f'- {w}' for w in p['warnings']]
    return lines


def render(run_dir, write=True):
    run_dir, brief, profile, summary, table, record = _load(run_dir)
    claims = Claims()
    units = summary.get('units') or (brief or {}).get('units') or ''
    status = summary.get('status', 'unknown')
    lines = ['# Forecast report', '']
    if brief:
        lines += ['## The decision', '', f'**{brief.get("target")}** ({brief.get("units")}), to decide: {brief.get("decision")}.',
                  f'Horizon {claims.num("horizon", int(brief.get("horizon") or summary.get("horizon") or 0), "brief.json", "horizon", fmt="{:d}")} periods ({brief.get("frequency")}), data up to {brief.get("as_of") or "(unstated)"}. Outcome known: {brief.get("outcome_date") or "(unstated)"}.',
                  f'Costs: too high, {brief.get("cost_of_over") or "unstated"}; too low, {brief.get("cost_of_under") or "unstated"}.', f'Known in advance: {brief.get("known_in_advance") or "unstated"}. Audience: {brief.get("audience") or "unstated"}.', '']
    else:
        lines += ['## The decision', '', 'No brief was attached to this run. The number below has no recorded decision, cost asymmetry or scoring date; attach one with `run.py apply --brief`.', '']
    lines += ['## Status', '', f'**{status}**: {STATUS_TEXT.get(status, "")}', '', f'Method: {summary.get("method")}', '', '## The forecast', '']
    lines += _forecast_block(table, summary, claims, units)
    lines += ['', '## What the evidence says', '', summary.get('interpretation', ''), '', '### Validation', ''] + _validation_block(summary, claims)
    lines += ['', '### Evidence in the summary', ''] + _evidence_block(summary, claims)
    lines += ['', '## The data', ''] + _profile_block(profile, claims)
    if brief and profile and profile.get('end') and brief.get('as_of') and str(brief['as_of'])[:10] > str(profile['end']):
        lines += ['', f'Note: the brief allows data up to {brief["as_of"]} but the last observation is {profile["end"]}; the forecast starts after the last observation, not after the cutoff.']
    lines += ['', '## Assumptions', ''] + [f'- {a}' for a in summary.get('assumptions', [])] or ['- none recorded']
    lines += ['', '## Not done', ''] + ([f'- {a}' for a in summary.get('not_done', [])] or ['- nothing recorded'])
    if summary.get('required_evidence'):
        lines += ['', '## Evidence needed', ''] + [f'- {a}' for a in summary['required_evidence']]
    lines += ['', '## Provenance', '', f'Run created {record.get("created_at", "(unknown)")}; chapter {summary.get("chapter")}; input `{Path(record.get("input_path", "?")).name}` (sha256 {str(record.get("input_sha256", ""))[:12]}); config sha256 {str(record.get("config_sha256", ""))[:12]}; scoring date {record.get("outcome_due") or "(unstated)"}.',
              f'Files: results.csv, summary.json, diagnostic.png, run.json' + (', brief.json' if brief else '') + (', profile.json' if profile else '') + '. Every number above is listed in claims.json with its source.']
    if (run_dir / 'diagnostic.png').exists():
        lines += ['', '![diagnostic](diagnostic.png)']
    text = '\n'.join(lines) + '\n'
    if write:
        (run_dir / 'report.md').write_text(text)
        (run_dir / 'claims.json').write_text(json.dumps(claims.items, indent=2, default=float) + '\n')
    return text, claims.items


def load_claims(*run_dirs):
    """Claims from several runs (rendering each that has none yet), so an interpretation that draws on two runs can be checked."""
    out = []
    for d in run_dirs:
        d = Path(d)
        if not (d / 'claims.json').exists():
            render(d)
        out += json.loads((d / 'claims.json').read_text())
    return out


def declared_assumptions(text):
    """Judgment numbers the author declares: every number on a line beginning `Assumption:` (or inside a
    section headed `## Assumptions`) becomes a claim with source `assumption` and the line as its key.
    A judgment written down with its reason is legitimate; one hidden in a sentence as if it were a result is not."""
    import re
    out = []; in_block = False; continuing = False
    for line in text.splitlines():
        stripped = line.strip()
        if re.match(r'^#+\s*assumptions?\b', stripped, re.I):
            in_block = True; continuing = False; continue
        if stripped.startswith('#'):
            in_block = False; continuing = False
        starts = stripped.lower().startswith('assumption:') or (in_block and stripped.startswith(('-', '*')))
        if not starts and continuing and stripped and not stripped.startswith(('-', '*', '#')):
            body = stripped                                  # a wrapped assumption paragraph continues until a blank line
        elif starts:
            body = re.sub(r'^(assumption:|[-*])\s*', '', stripped, flags=re.I); continuing = True
        else:
            continuing = False; continue
        for m in re.finditer(r'(?<![\w.])-?\d[\d,]*\.?\d*(?![\w.])', re.sub(r'\d{4}-\d{2}-\d{2}', ' ', body)):
            try:
                out.append(dict(label='declared assumption', value=float(m.group(0).replace(',', '')), source='assumption', key=body[:120]))
            except ValueError:
                pass
    return out


def check_claims(text, claims, tolerance=0.02, assumptions=True):
    """Numbers in `text` (an assistant's interpretation, say) that no claim supports.

    Dates, hashes, years, chapter references and integers up to 31 are ignored; a percentage
    matches a claim stored as a fraction. Numbers on lines beginning `Assumption:` (or under a
    `## Assumptions` heading) count as declared judgment when `assumptions` is true. Anything
    else must be within `tolerance` of a claim."""
    import re
    claims = list(claims) + (declared_assumptions(text) if assumptions else [])
    values = [float(c['value']) for c in claims if isinstance(c['value'], (int, float))]
    clean = re.sub(r'\d{4}-\d{2}-\d{2}(T[\d:.+]+)?', ' ', text)
    clean = re.sub(r'\b[0-9a-f]{8,}\b', ' ', clean)
    clean = re.sub(r'\bchapters? \d+(?:, ?\d+)*(?: (?:or|and) \d+)?', ' ', clean, flags=re.I)
    found = []
    quantity_before = re.compile(r'\b(order|ordering|commit|committing|forecast|forecasts|total|totals|sum|sums|stock|buy)\s*$', re.I)
    quantity_after = re.compile(r'^\s*(units?|cases|visits|items|parts|dollars|usd|percent|%|per\b)', re.I)
    for m in re.finditer(r'(?<![\w.])-?\d[\d,]*\.?\d*(?![\w.])', clean):
        token = m.group(0).rstrip('.,')
        try:
            v = float(token.replace(',', ''))
        except ValueError:
            continue
        if v.is_integer() and abs(v) <= 31:
            continue
        if v.is_integer() and 1900 <= v <= 2100 and ',' not in token and not (quantity_after.match(clean[m.end():m.end() + 12]) or (quantity_before.search(clean[max(0, m.start() - 14):m.start()]) and not re.search(r'\b(in|since|until|before|after|by|from|through|of|for)\s*$', clean[max(0, m.start() - 8):m.start()], re.I))):
            continue                                                # a year, not a quantity
        if not any(abs(v - c) <= tolerance * max(1.0, abs(c)) or (abs(c) <= 1 and abs(v - c * 100) <= 1) for c in values):
            found.append(m.group(0))
    return found
