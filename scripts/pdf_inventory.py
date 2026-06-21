#!/usr/bin/env python3
"""
Phase 1: Fast inventory of H:/Play Tennis/Books pdf (Python-only)
- pypdf for page count, pdftotext for content
"""
import os
import sys
import re
import json
import hashlib
import subprocess
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor, as_completed
import time
import pypdf

PDF_DIR = Path(r"H:\Play Tennis\Books pdf")

# Tennis topic keywords
TENNIS_KEYWORDS = {
    'tennis': 3, 'forehand': 2, 'backhand': 2, 'volley': 2, 'serve': 1,
    'racket': 2, 'racquet': 2, 'baseline': 1, 'court': 1, 'topspin': 2,
    'footwork': 2, 'split step': 2, 'biomechanic': 1, 'kinetic chain': 2,
    'nadal': 3, 'federer': 3, 'djokovic': 3, 'alcaraz': 3, 'sinner': 3,
    'wimbledon': 3, 'usta': 3, 'atp': 2, 'wta': 2,
    # Body/biomechanics signals
    'muscle': 0, 'joint': 0, 'tendon': 0, 'stretch': 0,
    'rotational': 1, 'sport science': 1, 'kinetic': 0,
    'core strength': 0, 'balance training': 0,
    # Off-topic
    'figure drawing': -5, 'perspective drawing': -5, 'illustration': -5,
    'cooking': -10, 'recipe': -10,
    'novel': -10, 'fiction': -10, 'language learning': -10,
    'spanish': -5, 'french language': -5, 'german': -5, 'japanese': -5,
    'yoga asana': -3, 'meditation': -3,
    'marketing': -10, 'seo': -10, 'business strategy': -10,
    'investing': -10, 'cryptocurrency': -10,
    'weight loss': -5, 'diet': -5,
    'bodybuilding': -3, 'powerlifting': -3,
}


def classify_text(text):
    if not text:
        return 0
    text_lower = text.lower()
    score = 0
    for kw, weight in TENNIS_KEYWORDS.items():
        if kw in text_lower:
            score += weight
    return score


def extract_first_page(pdf_path):
    try:
        sz = pdf_path.stat().st_size
        # Get page count via pypdf
        try:
            with open(pdf_path, 'rb') as f:
                reader = pypdf.PdfReader(f)
                page_count = len(reader.pages)
        except Exception:
            page_count = 0
        # Extract text via pdftotext
        result = subprocess.run(
            ['pdftotext', '-l', '5', '-layout', str(pdf_path), '-'],
            capture_output=True, timeout=30
        )
        text = result.stdout.decode('utf-8', errors='replace')[:8000] if result.returncode == 0 else ''
        # Content hash (normalized first 5KB)
        norm = re.sub(r'\s+', ' ', text).strip()[:5000]
        h = hashlib.md5(norm.encode('utf-8', errors='ignore')).hexdigest()[:16]
        return (str(pdf_path), sz, page_count, text, h)
    except subprocess.TimeoutExpired:
        return (str(pdf_path), pdf_path.stat().st_size, 0, '', 'TIMEOUT')
    except Exception as e:
        return (str(pdf_path), 0, 0, '', f'ERROR: {e}')


def main():
    pdf_files = sorted([p for p in PDF_DIR.rglob("*.pdf") if p.is_file()])
    print(f"Found {len(pdf_files)} PDF files", file=sys.stderr)

    inventory = {}
    start = time.time()
    with ProcessPoolExecutor(max_workers=6) as ex:
        futures = {ex.submit(extract_first_page, p): p for p in pdf_files}
        for i, fut in enumerate(as_completed(futures), 1):
            path, sz, pages, text, h = fut.result()
            score = classify_text(text)
            inventory[path] = {
                'size': sz,
                'pages': pages,
                'score': score,
                'hash': h,
                'first_chars': text[:600] if text else '',
            }
            if i % 50 == 0 or i == len(pdf_files):
                elapsed = time.time() - start
                rate = i / elapsed
                eta = (len(pdf_files) - i) / rate if rate else 0
                print(f"  [{i}/{len(pdf_files)}] {rate:.1f}/s ETA={eta:.0f}s", file=sys.stderr)

    out = r"C:\Users\Henry\Documents\tennis-wiki\scripts\pdf_inventory.json"
    with open(out, 'w', encoding='utf-8') as f:
        json.dump(inventory, f, ensure_ascii=False, indent=2)

    tennis = sum(1 for v in inventory.values() if v['score'] >= 2)
    maybe = sum(1 for v in inventory.values() if 0 < v['score'] < 2)
    off = sum(1 for v in inventory.values() if v['score'] <= 0)
    print(f"\n=== Classification ===")
    print(f"  Tennis (score >= 2): {tennis}")
    print(f"  Maybe (0 < score < 2): {maybe}")
    print(f"  Off-topic (score <= 0): {off}")
    print(f"  Total: {len(inventory)}")
    print(f"\nInventory saved to: {out}")


if __name__ == "__main__":
    main()
