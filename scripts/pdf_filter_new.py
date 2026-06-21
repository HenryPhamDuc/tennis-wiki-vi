#!/usr/bin/env python3
"""
Phase 3: Compare PDF content with existing vault articles.
A PDF is considered "duplicate" if it covers the same topic as an existing article
(we'll skip those — user wants only NEW articles).
"""
import json
import re
import hashlib
from pathlib import Path
from collections import defaultdict

# Load existing vault slugs
EXISTING = Path(r"C:\Users\Henry\Documents\MY VAULT\Documents\Obsidian Vault\tennis-vault\Tennis Wiki-Vietnamese")
existing_slugs = set()
for d in EXISTING.iterdir():
    if not d.is_dir() or d.name.startswith(('00', '_')):
        continue
    for f in d.glob("*.md"):
        existing_slugs.add(f.stem.lower())

print(f"Existing vault slugs: {len(existing_slugs)}")

# Load PDF inventory
pdfs = json.load(open(r"C:\Users\Henry\Documents\tennis-wiki\scripts\pdf_unique.json", encoding='utf-8'))
print(f"Unique tennis PDFs: {len(pdfs)}")

# Build a simple keyword index for existing vault
# For each existing article, get keywords from filename
existing_keywords = set()
for slug in existing_slugs:
    # Split slug into tokens
    tokens = re.findall(r'[a-zA-Z]{3,}', slug.lower())
    existing_keywords.update(tokens)

print(f"Existing keywords (≥3 chars): {len(existing_keywords)}")

# Stop words to ignore
STOP = {
    'the', 'and', 'for', 'with', 'from', 'how', 'your', 'into', 'all', 'one',
    'two', 'new', 'top', 'best', 'guide', 'introduction', 'part', 'chapter',
    'tips', 'plan', 'level', 'modern', 'advanced', 'volume', 'session',
    'tennis', 'coaching', 'complete', 'ultimate', 'essential', 'master',
    'racket', 'racquet',
    'com', 'org', 'net', 'pdf', 'docx', 'file', 'http', 'https',
    'preview', 'magazine', 'issue', 'edition', 'library',
    'photo', 'photos', 'image', 'images', 'pic', 'pics',
    'openweb', 'gemini', 'chatgpt', 'claude', 'ollama', 'grok', 'meta', 'openai',
    'vi', 'en',
    'page', 'pages', 'section', 'drill', 'drills', 'training', 'practice',
    'biomechanics', 'biomechanical',
    'tfl', 'rpm', 'anatomy', 'physiology',
}


def pdf_topic_keywords(item):
    """Extract topic keywords from PDF name + first chars."""
    name = Path(item['path']).name.lower()
    text = (name + ' ' + item.get('first_chars', '')).lower()
    # Strong topic signals
    topics = set()
    # Specific tennis strokes
    for kw in ['forehand', 'backhand', 'volley', 'serve', 'return', 'footwork',
               'split step', 'overhead', 'lob', 'dropshot', 'slice', 'topspin',
               'groundstroke', 'approach shot']:
        if kw in text:
            topics.add(kw)
    # Topics
    for kw in ['biomechanics', 'kinetic', 'kinematic', 'rotation', 'wrist', 'shoulder',
               'core', 'pelvis', 'spine', 'balance', 'vision', 'mental', 'tactic',
               'strategy', 'pattern', 'fitness', 'conditioning', 'flexibility',
               'endurance', 'speed', 'agility', 'power', 'strength', 'endurance',
               'recovery', 'injury', 'tendon', 'muscle', 'biomechanic', 'biomechanical',
               'anatomy', 'posture', 'grip', 'racket', 'racquet', 'string',
               'tension', 'physics', 'neuroscience', 'psychology', 'mindset',
               'cognition', 'federer', 'nadal', 'djokovic', 'alcaraz', 'sinner',
               'wimbledon', 'us open', 'australian open', 'french open', 'roland garros',
               'coach', 'training', 'practice', 'drill', 'conditioning']:
        if kw in text:
            topics.add(kw)
    return topics


def matches_existing(item):
    """Check if a PDF covers topics already well-covered in vault."""
    pdf_topics = pdf_topic_keywords(item)
    # Heuristic: if 3+ of the PDF's core topics appear in the existing keywords set
    # AND the PDF is short (likely a single-topic paper that overlaps)
    common = pdf_topics & existing_keywords
    # Short PDFs (≤ 10 pages) with 3+ matching topics = likely duplicate
    if item['pages'] <= 10 and len(common) >= 3:
        return True, common
    # Medium PDFs (≤ 30 pages) with 5+ matching topics = likely duplicate
    if item['pages'] <= 30 and len(common) >= 5:
        return True, common
    # Long PDFs (any size) with 8+ matching topics = likely fully covered
    if len(common) >= 8:
        return True, common
    return False, common


# Score each PDF
for p in pdfs:
    dup, common = matches_existing(p)
    p['matches_existing'] = len(common)
    p['likely_duplicate'] = dup
    p['topics'] = list(pdf_topic_keywords(p))

# Stats
truly_new = [p for p in pdfs if not p['likely_duplicate']]
likely_dup = [p for p in pdfs if p['likely_duplicate']]

print()
print(f"=== Dedup vs existing vault ===")
print(f"  Truly new (NOT in existing): {len(truly_new)}")
print(f"  Likely duplicate of existing: {len(likely_dup)}")
print()
print("Top 30 NEW PDFs by quality (rank):")
for i, p in enumerate(truly_new[:30], 1):
    name = Path(p['path']).name
    print(f"  {i:2d}. pages={p['pages']:3d}  topics={p['matches_existing']:2d}  {name[:80]}")

print()
print("First 10 LIKELY DUPLICATES (skipped):")
for p in likely_dup[:10]:
    name = Path(p['path']).name
    print(f"  - {name[:80]}  (matches {p['matches_existing']} existing topics)")

# Save the new list
out = r"C:\Users\Henry\Documents\tennis-wiki\scripts\pdf_new_only.json"
with open(out, 'w', encoding='utf-8') as f:
    json.dump(truly_new, f, ensure_ascii=False, indent=2)
print(f"\nSaved {len(truly_new)} NEW PDFs to {out}")

# Total pages estimate
total_pages = sum(p['pages'] for p in truly_new)
total_size = sum(p['size'] for p in truly_new) / 1024 / 1024
print(f"Total pages in NEW: {total_pages:,}")
print(f"Total size: {total_size:.1f} MB")
