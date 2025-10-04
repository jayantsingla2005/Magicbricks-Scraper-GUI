#!/usr/bin/env python3
"""
Playwright-based field-by-field validation for MagicBricks properties.
- Reads two CSVs (Gurgaon, Mumbai)
- Samples 15 URLs from each with basic diversity constraints
- Opens each URL in headful Chromium via Playwright
- Captures screenshot + HTML snapshot for audit
- Compares selected CSV fields against page text presence (normalized)
- Writes a JSON + Markdown report under reports/

Note: This validator uses robust string-in-page checks to avoid brittle selectors.
"""

import csv
import json
import os
import random
import re
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Tuple

from playwright.sync_api import sync_playwright

REPO_ROOT = Path(__file__).resolve().parents[1]
REPORTS_DIR = REPO_ROOT / 'reports' / 'validation'
REPORTS_DIR.mkdir(parents=True, exist_ok=True)

SELECTED_FIELDS = [
    'title','price','area','property_type','bathrooms','balcony','furnishing',
    'floor_details','locality','society','status','facing','parking',
    'owner_name','contact_options','description','photo_count'
]

@dataclass
class URLSample:
    city: str
    property_url: str
    property_type: str
    is_premium: str
    owner_name: str

@dataclass
class URLResult:
    city: str
    property_url: str
    screenshot: str
    html_snapshot: str
    comparisons: Dict[str, Dict[str, Any]]  # field -> {csv_value, found, notes}


def read_csv_rows(csv_path: Path) -> List[Dict[str, str]]:
    with open(csv_path, newline='', encoding='utf-8') as f:
        return list(csv.DictReader(f))


def normalize_text(s: str) -> str:
    s = (s or '').strip().lower()
    s = re.sub(r"\s+", " ", s)
    return s


def normalize_price(s: str) -> str:
    s = normalize_text(s)
    # unify lakh/crore variants
    s = s.replace(' lacs', ' lac').replace(' lakhs', ' lac').replace(' lakh', ' lac')
    s = s.replace(' crores', ' cr').replace(' crore', ' cr')
    s = s.replace('₹', '').strip()
    return s


def field_normalizer(field: str, val: str) -> str:
    if field == 'price':
        return normalize_price(val)
    return normalize_text(val)


def stratified_sample(rows: List[Dict[str, str]], city: str, k: int) -> List[URLSample]:
    # Try: 12 apartments, 2 houses, 1 plot; fallback to random if not enough.
    ap = [r for r in rows if normalize_text(r.get('property_type','')).find('apart')!=-1]
    house = [r for r in rows if normalize_text(r.get('property_type','')).find('house')!=-1]
    plot = [r for r in rows if normalize_text(r.get('property_type','')).find('plot')!=-1]

    picks: List[Dict[str,str]] = []
    picks += random.sample(ap, min(12, len(ap)))
    picks += random.sample(house, min(2, len(house)))
    if plot:
        picks += [random.choice(plot)]
    # pad to k
    remaining = [r for r in rows if r not in picks]
    if len(picks) < k:
        picks += random.sample(remaining, min(k-len(picks), len(remaining)))
    picks = picks[:k]

    samples: List[URLSample] = []
    for r in picks:
        url = r.get('property_url') or r.get('url') or ''
        if not url:
            continue
        samples.append(URLSample(
            city=city,
            property_url=url,
            property_type=r.get('property_type',''),
            is_premium=str(r.get('is_premium','')),
            owner_name=r.get('owner_name','')
        ))
    return samples


def compare_fields(page_text: str, row: Dict[str,str]) -> Dict[str, Dict[str, Any]]:
    results: Dict[str, Dict[str, Any]] = {}
    norm_page = normalize_text(page_text)
    for f in SELECTED_FIELDS:
        v = row.get(f, '')
        if not v:
            results[f] = { 'csv_value': v, 'found': None, 'notes': 'CSV empty' }
            continue
        nv = field_normalizer(f, v)
        found = nv in norm_page
        results[f] = { 'csv_value': v, 'found': bool(found) }
        if not found:
            results[f]['notes'] = 'value not found in page text'
    return results


def run_validation(gurgaon_csv: Path, mumbai_csv: Path) -> Tuple[List[URLResult], Dict[str, Any]]:
    g_rows = [r for r in read_csv_rows(gurgaon_csv) if (r.get('property_url') or '').startswith('http')]
    m_rows = [r for r in read_csv_rows(mumbai_csv) if (r.get('property_url') or '').startswith('http')]

    g_samples = stratified_sample(g_rows, 'gurgaon', 15)
    m_samples = stratified_sample(m_rows, 'mumbai', 15)

    samples = g_samples + m_samples
    random.shuffle(samples)

    results: List[URLResult] = []

    ts = datetime.now().strftime('%Y%m%d_%H%M%S')
    run_dir = REPORTS_DIR / f'run_{ts}'
    run_dir.mkdir(parents=True, exist_ok=True)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()
        for i, s in enumerate(samples, 1):
            try:
                page.goto(s.property_url, timeout=60000, wait_until='networkidle')
                page.wait_for_timeout(1500)
                screenshot_path = str(run_dir / f"{i:02d}_{s.city}.png")
                html_path = str(run_dir / f"{i:02d}_{s.city}.html")
                page.screenshot(path=screenshot_path, full_page=True)
                page_content = page.content()
                with open(html_path, 'w', encoding='utf-8') as hf:
                    hf.write(page_content)
                page_text = page.inner_text('body')
                # Find CSV row by URL
                row = next((r for r in (g_rows if s.city=='gurgaon' else m_rows)
                            if (r.get('property_url') or '') == s.property_url), None)
                comparisons = compare_fields(page_text, row or {})
                results.append(URLResult(
                    city=s.city,
                    property_url=s.property_url,
                    screenshot=os.path.relpath(screenshot_path, REPO_ROOT),
                    html_snapshot=os.path.relpath(html_path, REPO_ROOT),
                    comparisons=comparisons
                ))
            except Exception as e:
                # Record failure with minimal info
                results.append(URLResult(
                    city=s.city,
                    property_url=s.property_url,
                    screenshot='',
                    html_snapshot='',
                    comparisons={'__error__': {'csv_value': '', 'found': False, 'notes': str(e)}}
                ))
        context.close()
        browser.close()

    # Aggregate metrics
    field_totals: Dict[str, int] = {f: 0 for f in SELECTED_FIELDS}
    field_matches: Dict[str, int] = {f: 0 for f in SELECTED_FIELDS}
    examples: Dict[str, List[Dict[str, str]]] = {f: [] for f in SELECTED_FIELDS}

    for r in results:
        for f in SELECTED_FIELDS:
            comp = r.comparisons.get(f)
            if not comp or comp.get('found') is None:
                continue
            field_totals[f] += 1
            if comp.get('found'):
                field_matches[f] += 1
            else:
                if len(examples[f]) < 3:
                    examples[f].append({'url': r.property_url, 'csv': comp.get('csv_value','')})

    completeness = {f: (100.0*field_matches[f]/field_totals[f] if field_totals[f] else None)
                    for f in SELECTED_FIELDS}

    report = {
        'timestamp': ts,
        'gurgaon_csv': str(gurgaon_csv),
        'mumbai_csv': str(mumbai_csv),
        'totals': {'urls': len(results)},
        'completeness_percent': completeness,
        'mismatch_examples': examples
    }

    # Save JSON and Markdown
    json_path = run_dir / 'validation_report.json'
    md_path = run_dir / 'validation_report.md'
    with open(json_path, 'w', encoding='utf-8') as jf:
        json.dump({'report': report, 'results': [asdict(r) for r in results]}, jf, ensure_ascii=False, indent=2)

    def md_line(k,v):
        return f"- {k}: {v if v is not None else 'N/A'}\n"

    with open(md_path, 'w', encoding='utf-8') as mf:
        mf.write(f"# Validation Report ({ts})\n\n")
        mf.write(md_line('URLs validated', len(results)))
        mf.write("\n## Field Completeness (%)\n")
        for f in SELECTED_FIELDS:
            mf.write(md_line(f, f"{completeness[f]:.1f}" if completeness[f] is not None else 'N/A'))
        mf.write("\n## Example Mismatches (up to 3 each)\n")
        for f in SELECTED_FIELDS:
            if examples[f]:
                mf.write(f"\n### {f}\n")
                for ex in examples[f]:
                    mf.write(f"- {ex['url']} | CSV: {ex['csv']}\n")

    print(f"[DONE] Report saved to: {json_path} and {md_path}")
    return results, report


if __name__ == '__main__':
    g = REPO_ROOT / 'magicbricks_gurgaon_full_20251002_193730.csv'
    m = REPO_ROOT / 'magicbricks_mumbai_full_20251002_233131.csv'
    run_validation(g, m)

