#!/usr/bin/env python3
"""
Convert Cam Nang folder → tennis-wiki docs/cam-nang/

Source: C:/Users/Henry/Documents/MY VAULT/Documents/Obsidian Vault/tennis-vault/Cam Nang
Target: C:/Users/Henry/Documents/tennis-wiki/docs/cam-nang/

Strategy:
- 53 .docx files in "Advanced Manual Coauthor by Claude/" → 11 chapter articles (consolidated)
- 6 PDF files in root → 6 standalone articles
- Each gets Vietnamese YAML frontmatter + full content
- Dedup against existing 892 articles
"""
import os
import re
import sys
import json
import hashlib
import subprocess
import shutil
from pathlib import Path
from datetime import datetime
from collections import defaultdict
import yaml

SRC = Path(r"C:\Users\Henry\Documents\MY VAULT\Documents\Obsidian Vault\tennis-vault\Cam Nang")
DOCS_DIR = Path(r"C:\Users\Henry\Documents\tennis-wiki\docs\cam-nang")
DOCS_DIR.mkdir(parents=True, exist_ok=True)

PANDOC = r"C:\Program Files\Pandoc\pandoc.exe"


def slugify(text):
    text = re.sub(r'[\\/:*?"<>|]', '', text)
    text = re.sub(r'\s+', '-', text.strip())
    text = re.sub(r'-{2,}', '-', text)
    return text.strip('-').lower()


def pandoc_to_md(docx_path):
    """Convert docx to markdown via pandoc."""
    try:
        result = subprocess.run(
            [PANDOC, str(docx_path), '-t', 'markdown_strict', '--wrap=none'],
            capture_output=True, timeout=120
        )
        if result.returncode == 0:
            return result.stdout.decode('utf-8', errors='replace')
        return f'[PANDOC ERROR: {result.stderr.decode()[:200]}]'
    except Exception as e:
        return f'[CONVERSION ERROR: {e}]'


def pdf_to_md(pdf_path, max_pages=20):
    """Convert PDF to markdown via pdftotext + pypdf."""
    try:
        result = subprocess.run(
            ['pdftotext', '-l', str(max_pages), '-layout', str(pdf_path), '-'],
            capture_output=True, timeout=120
        )
        return result.stdout.decode('utf-8', errors='replace') if result.returncode == 0 else ''
    except Exception as e:
        return f'[ERROR: {e}]'


def build_yaml(title, **kwargs):
    """Build YAML frontmatter."""
    lines = ['---']
    lines.append(f'title: "{title}"')
    lines.append('language: vi')
    lines.append('vault: Cam Nang')
    lines.append(f'created: {datetime.now().strftime("%Y-%m-%d")}')
    for k, v in kwargs.items():
        if isinstance(v, list):
            v_str = ', '.join(json.dumps(str(x), ensure_ascii=False) for x in v)
            lines.append(f'{k}: [{v_str}]')
        else:
            lines.append(f'{k}: "{v}"')
    lines.append('---')
    return '\n'.join(lines)


def main():
    print("=== Loading existing docs for dedup ===")
    existing_hashes = set()
    existing_slugs = set()
    for f in DOCS_DIR.parent.rglob("*.md"):
        if f.name == 'index.md' or 'cam-nang' in f.parts:
            continue  # Skip cam-nang and indexes
        try:
            text = f.read_text(encoding='utf-8', errors='replace')
            norm = re.sub(r'\s+', ' ', text).strip()
            h = hashlib.md5(norm.encode('utf-8', errors='ignore')).hexdigest()
            existing_hashes.add(h)
            existing_slugs.add(f.stem.lower())
        except Exception:
            pass
    print(f"  Existing: {len(existing_hashes)} articles")

    written = []
    skipped = []

    # === PART 1: Process 53 docx files in Advanced Manual subdir ===
    print("\n=== Part 1: 53 docx files in Advanced Manual ===")
    advanced_dir = SRC / "Advanced Manual Coauthor by Claude"
    docx_files = sorted(advanced_dir.glob("tennis_manual_ch*.docx"))
    print(f"  Found: {len(docx_files)} docx files")

    # Group by chapter
    by_chapter = defaultdict(list)
    for f in docx_files:
        m = re.match(r'tennis_manual_(ch\d+)_s(\d+)\.(\d+)\.docx', f.name)
        if m:
            ch = int(m.group(1)[2:])
            sec = int(m.group(2))
            sub = int(m.group(3))
            by_chapter[ch].append((sec, sub, f))
    for ch in by_chapter:
        by_chapter[ch].sort()

    print(f"  Chapters: {len(by_chapter)} (ch1-ch{max(by_chapter.keys())})")

    # Process each chapter → one consolidated article
    chapter_titles = {
        1: 'The Kinetic Chain & Biomechanical Foundations',
        2: 'Stroke Mechanics — Forehand, Backhand, Serve, Volley',
        3: 'Footwork & Movement Systems',
        4: 'Mental Game & Cognitive Architecture',
        5: 'Tactical Patterns & Match Strategy',
        6: 'Physical Conditioning & Recovery',
        7: 'Periodization & Long-term Planning',
        8: 'Elite Player Analysis & Case Studies',
        9: 'Coaching Methodology & Communication',
        10: 'Advanced Concepts — Wave Theory, Tai Chi, Dantian',
        11: 'Integration & Mastery',
    }

    for ch, items in sorted(by_chapter.items()):
        title = chapter_titles.get(ch, f'Chapter {ch}')
        slug = f'advanced-manual-ch{ch:02d}-{slugify(title.split(" — ")[0].split(" & ")[0])[:30]}'

        # Skip if exists
        if slug in existing_slugs:
            skipped.append({'file': f'ch{ch}', 'reason': f'slug exists: {slug}'})
            continue

        # Concatenate all sections
        all_content = f"# Chapter {ch}: {title}\n\n"
        all_content += f"> **Từ cuốn sách:** *Advanced Tennis Manual — Coauthor by Claude* (Tennis Future Lab)\n\n"
        all_content += f"> **Chương {ch}/11** — {title}\n\n---\n\n"

        for sec, sub, f in items:
            md = pandoc_to_md(f)
            all_content += md + '\n\n---\n\n'

        # YAML
        yaml = build_yaml(
            title=f'Chapter {ch}: {title}',
            vault_path=f'Advanced Manual Coauthor by Claude/{f.name}',
            source_type='consolidated_docx',
            chapter=ch,
            sections=len(items),
            tags=['cẩm-nang', 'advanced-manual', f'chapter-{ch}'],
            category='cam-nang',
        )

        out = DOCS_DIR / f'{slug}.md'
        out.write_text(yaml + '\n\n' + all_content, encoding='utf-8')
        # Add hash to existing for intra-batch dedup
        norm = re.sub(r'\s+', ' ', (yaml + all_content)).strip()
        existing_hashes.add(hashlib.md5(norm.encode('utf-8', errors='ignore')).hexdigest())
        existing_slugs.add(slug)
        written.append({'out': str(out), 'src': f'ch{ch}', 'type': 'chapter', 'sections': len(items)})
        print(f"  ✓ Chapter {ch}: {len(items)} sections → {slug}.md")

    # === PART 2: Process 6 PDFs in root ===
    print("\n=== Part 2: 6 PDF files in root ===")
    pdf_files = sorted([f for f in SRC.glob("*.pdf")])
    print(f"  Found: {len(pdf_files)} PDF files")

    for pdf in pdf_files:
        name = pdf.stem
        slug = slugify(name)[:80]
        if not slug:
            slug = 'pdf-' + hashlib.md5(name.encode()).hexdigest()[:8]

        if slug in existing_slugs:
            skipped.append({'file': pdf.name, 'reason': f'slug exists: {slug}'})
            continue

        # Extract PDF text
        text = pdf_to_md(pdf, max_pages=50)
        if not text or len(text) < 100:
            text = '[No text extracted - PDF may be image-based or empty]'

        # Build content
        # Clean up: take first 30K chars for now
        if len(text) > 30000:
            text = text[:30000] + '\n\n[... trích đoạn, nội dung đầy đủ xem file PDF gốc]'

        vi_title = pdf.stem.replace('_', ' ').title()
        # Vietnamese-friendly title translation
        vi_title = re.sub(r'\bTennis\b', 'Tennis', vi_title, flags=re.IGNORECASE)
        vi_title = re.sub(r'\bVolley\b', 'Volley', vi_title, flags=re.IGNORECASE)
        vi_title = re.sub(r'\bModern\b', 'Hiện Đại', vi_title, flags=re.IGNORECASE)
        vi_title = re.sub(r'\bThe Art of\b', 'Nghệ Thuật', vi_title, flags=re.IGNORECASE)
        vi_title = re.sub(r'\bElite\b', 'Elite', vi_title, flags=re.IGNORECASE)
        vi_title = re.sub(r'\bComplete\b', 'Toàn Tập', vi_title, flags=re.IGNORECASE)
        vi_title = re.sub(r'\bFormulas?\b', 'Công Thức', vi_title, flags=re.IGNORECASE)

        # Detect size
        size_kb = pdf.stat().st_size // 1024

        yaml = build_yaml(
            title=vi_title,
            vault_path=f'Cam Nang/{pdf.name}',
            source_type='pdf_extract',
            source_pdf=pdf.name,
            pdf_size_kb=size_kb,
            tags=['cẩm-nang', 'pdf', 'tổng-hợp'],
            category='cam-nang',
        )

        body = f"# {vi_title}\n\n"
        body += f"> **Nguồn:** `{pdf.name}` ({size_kb} KB)\n\n"
        body += f"> **Loại:** PDF — trích xuất tự động\n\n---\n\n"
        body += "## Nội Dung Trích Xuất\n\n"
        body += "```\n" + text + "\n```\n"

        out = DOCS_DIR / f'{slug}.md'
        out.write_text(yaml + '\n\n' + body, encoding='utf-8')
        norm = re.sub(r'\s+', ' ', (yaml + body)).strip()
        existing_hashes.add(hashlib.md5(norm.encode('utf-8', errors='ignore')).hexdigest())
        existing_slugs.add(slug)
        written.append({'out': str(out), 'src': pdf.name, 'type': 'pdf', 'kb': size_kb})
        print(f"  ✓ {pdf.name} ({size_kb}KB) → {slug}.md")

    print(f"\n=== Results ===")
    print(f"  Written: {len(written)}")
    print(f"  Skipped: {len(skipped)}")

    # Save manifest
    with open(r"C:\Users\Henry\Documents\tennis-wiki\scripts\camnang_manifest.json", 'w', encoding='utf-8') as f:
        json.dump({'written': written, 'skipped': skipped}, f, ensure_ascii=False, indent=2)
    print(f"\nManifest saved")


if __name__ == "__main__":
    main()
