#!/usr/bin/env python3
"""
Phase 4: Extract text from NEW PDFs and build markdown pages.

Strategy per PDF:
- Extract first 2-3 pages as text (intro/abstract)
- If PDF ≤ 30 pages: extract full text
- If 30 < pages ≤ 100: extract first 30 pages
- If > 100 pages: extract first 20 pages + last 5 pages (skip middle)
- Build Vietnamese metadata + summary in YAML frontmatter
- Save body in English (preserving original)
- Add a brief Vietnamese intro paragraph at the top
- Place in category subdir based on earlier categorization
"""
import os
import sys
import re
import json
import hashlib
import subprocess
from pathlib import Path
from datetime import datetime
from concurrent.futures import ProcessPoolExecutor, as_completed
import time

PDF_NEW = json.load(open(r"C:\Users\Henry\Documents\tennis-wiki\scripts\pdf_new_only.json", encoding='utf-8'))

DOCS_DIR = Path(r"C:\Users\Henry\Documents\tennis-wiki\docs\pdf-sach-tennis")
DOCS_DIR.mkdir(parents=True, exist_ok=True)

# Vietnamese topic mapping (English -> Vietnamese category)
CAT_TO_SUBDIR = {
    'ky-thuat': 'ky-thuat',         # Kỹ thuật
    'co-sinh-hoc': 'co-sinh-hoc',   # Cơ sinh học
    'chien-thuat': 'chien-thuat',   # Chiến thuật
    'tam-ly': 'tam-ly',             # Tâm lý
    'the-luc': 'the-luc',           # Thể lực
    'tham-khao': 'tham-khao',       # Tham khảo
}

# Vietnamese topic name → categories
TOPIC_VI = {
    'forehand': 'Forehand',
    'backhand': 'Backhand',
    'volley': 'Volley',
    'serve': 'Giao bóng',
    'return': 'Trả giao bóng',
    'footwork': 'Bộ pháp',
    'split step': 'Split step',
    'topspin': 'Topspin',
    'slice': 'Slice',
    'biomechanics': 'Cơ sinh học',
    'kinetic': 'Chuỗi động lực',
    'federer': 'Roger Federer',
    'nadal': 'Rafael Nadal',
    'djokovic': 'Novak Djokovic',
    'alcaraz': 'Carlos Alcaraz',
    'sinner': 'Jannik Sinner',
    'wimbledon': 'Wimbledon',
    'tactic': 'Chiến thuật',
    'mental': 'Tâm lý',
    'fitness': 'Thể lực',
    'anatomy': 'Giải phẫu',
    'training': 'Huấn luyện',
    'drill': 'Bài tập',
    'conditioning': 'Thể lực',
    'balance': 'Thăng bằng',
    'vision': 'Tầm nhìn',
    'string': 'Dây vợt',
}


def vi_topics(topics_en):
    """Convert English topics to Vietnamese display names."""
    seen = set()
    vi = []
    for t in topics_en:
        vi_name = TOPIC_VI.get(t, t.title())
        if vi_name and vi_name not in seen:
            vi.append(vi_name)
            seen.add(vi_name)
    return vi


def vi_title_from_name(name):
    """Convert English filename to a cleaner Vietnamese display title."""
    # Remove extension
    name = re.sub(r'\.pdf$', '', name, flags=re.IGNORECASE)
    # Remove PDFDrive markers
    name = re.sub(r'\(\s*PDFDrive\s*\)', '', name, flags=re.IGNORECASE)
    name = re.sub(r'\(\d+\)', '', name)
    # Replace common tennis terms with Vietnamese where natural
    replacements = {
        r'\bTennis\b': 'Tennis',
        r'\btennis\b': 'Tennis',
        r'\bForehand\b': 'Forehand',
        r'\bBackhand\b': 'Backhand',
        r'\bVolley\b': 'Volley',
        r'\bServe\b': 'Serve',
        r'\bBiomechanics?\b': 'Cơ Sinh Học',
        r'\bAnatomy\b': 'Giải Phẫu',
        r'\bTraining\b': 'Huấn Luyện',
        r'\bDrill\b': 'Bài Tập',
        r'\bPractice\b': 'Thực Hành',
        r'\bTactic(s)?\b': 'Chiến Thuật',
        r'\bStrategy\b': 'Chiến Lược',
        r'\bModern\b': 'Hiện Đại',
        r'\bAdvanced\b': 'Nâng Cao',
        r'\bComplete\b': 'Toàn Tập',
        r'\bUltimate\b': 'Tối Thượng',
        r'\bEssential\b': 'Cốt Lõi',
        r'\bMaster(ing)?\b': 'Làm Chủ',
        r'\bGuide\b': 'Cẩm Nang',
        r'\bFundamental(s)?\b': 'Nền Tảng',
        r'\bTechnique\b': 'Kỹ Thuật',
        r'\bTechniques\b': 'Kỹ Thuật',
        r'\bFitness\b': 'Thể Lực',
        r'\bConditioning\b': 'Thể Lực',
        r'\bMovement\b': 'Chuyển Động',
        r'\bMental\b': 'Tâm Lý',
        r'\bPsychology\b': 'Tâm Lý Học',
        r'\bFocus\b': 'Tập Trung',
        r'\bVisual\b': 'Thị Giác',
        r'\bVision\b': 'Tầm Nhìn',
        r'\bBalance\b': 'Thăng Bằng',
        r'\bStrength\b': 'Sức Mạnh',
        r'\bPower\b': 'Sức Mạnh',
        r'\bSpeed\b': 'Tốc Độ',
        r'\bAgility\b': 'Nhanh Nhẹn',
        r'\bEndurance\b': 'Sức Bền',
        r'\bFlexibility\b': 'Linh Hoạt',
        r'\bInjury\b': 'Chấn Thương',
        r'\bRecovery\b': 'Phục Hồi',
        r'\bNutrition\b': 'Dinh Dưỡng',
        r'\bString(s|ing)?\b': 'Dây Vợt',
        r'\bRacket\b': 'Vợt',
        r'\bRacquet\b': 'Vợt',
    }
    for pat, repl in replacements.items():
        name = re.sub(pat, repl, name)
    # Clean up multiple spaces and dashes
    name = re.sub(r'\s+', ' ', name).strip()
    name = re.sub(r'\s*-\s*', ' - ', name)
    name = re.sub(r'_+', ' ', name)
    # Title case
    name = re.sub(r'\w\S*', lambda m: m.group(0).capitalize(), name)
    return name


def extract_pdf_text(pdf_path, max_pages=None):
    """Extract text from PDF, with page limit if specified."""
    try:
        if max_pages:
            cmd = ['pdftotext', '-l', str(max_pages), '-layout', str(pdf_path), '-']
        else:
            cmd = ['pdftotext', '-layout', str(pdf_path), '-']
        result = subprocess.run(cmd, capture_output=True, timeout=120)
        return result.stdout.decode('utf-8', errors='replace') if result.returncode == 0 else ''
    except Exception as e:
        return f'[EXTRACTION ERROR: {e}]'


def build_page(pdf_meta):
    """Build one markdown page from PDF metadata."""
    path = Path(pdf_meta['path'])
    name = path.name
    pages = pdf_meta['pages']
    size_kb = pdf_meta['size'] // 1024
    topics = pdf_meta.get('topics', [])
    cats = pdf_meta.get('categories', ['tham-khao'])

    # Determine primary subdir
    primary_cat = cats[0] if cats else 'tham-khao'
    subdir = CAT_TO_SUBDIR.get(primary_cat, 'tham-khao')

    # Vietnamese title
    vi_title = vi_title_from_name(name)

    # English title (from filename)
    en_title = re.sub(r'[_\.]+', ' ', re.sub(r'\.pdf$', '', name)).strip()

    # Extract text
    if pages <= 30:
        text = extract_pdf_text(path)
    elif pages <= 100:
        text = extract_pdf_text(path, max_pages=30)
    else:
        text = extract_pdf_text(path, max_pages=20)
        # Also try to get the last few pages
        try:
            last_cmd = ['pdftotext', '-f', str(max(1, pages - 5)), '-layout', str(path), '-']
            last = subprocess.run(last_cmd, capture_output=True, timeout=30)
            if last.returncode == 0:
                text += '\n\n---\n\n[Cuối tài liệu]\n\n' + last.stdout.decode('utf-8', errors='replace')
        except Exception:
            pass

    # Build summary from first 1500 chars
    summary_en = text[:1500].strip() if text else ''
    summary_en = re.sub(r'\s+', ' ', summary_en)[:600]

    # Vietnamese summary (short intro)
    vi_topics_list = vi_topics(topics)
    vi_intro = f"## Giới Thiệu\n\n"
    vi_intro += f"**{vi_title}** — tài liệu {pages} trang từ thư viện sách tennis.\n\n"
    if vi_topics_list:
        vi_intro += f"**Chủ đề chính:** {', '.join(vi_topics_list[:6])}\n\n"
    if summary_en:
        vi_intro += f"**Tóm tắt nội dung (trích từ tài liệu gốc):** {summary_en}\n\n"
    vi_intro += f"**Lưu ý:** Nội dung dưới đây được trích xuất tự động từ PDF gốc tiếng Anh, giữ nguyên ngôn ngữ để bảo toàn độ chính xác kỹ thuật.\n\n---\n\n"

    # Build YAML
    yaml_lines = ['---']
    yaml_lines.append(f'title: "{vi_title}"')
    yaml_lines.append(f'original_title: "{en_title}"')
    yaml_lines.append(f'language: vi')
    yaml_lines.append(f'vault: Tennis Wiki-Vietnamese')
    yaml_lines.append(f'created: {datetime.now().strftime("%Y-%m-%d")}')
    if vi_topics_list:
        yaml_lines.append(f'tags: [{", ".join(json.dumps(t, ensure_ascii=False) for t in vi_topics_list[:8])}]')
    yaml_lines.append(f'category: "{subdir}"')
    yaml_lines.append(f'source_pdf: "{name}"')
    yaml_lines.append(f'pdf_pages: {pages}')
    yaml_lines.append(f'pdf_size_kb: {size_kb}')
    yaml_lines.append(f'pdf_path: "H:\\\\Play Tennis\\\\Books pdf\\\\{name}"')
    yaml_lines.append('---')

    body = '\n'.join(yaml_lines) + '\n\n'
    body += f'# 🎾 {vi_title}\n\n'
    body += vi_intro

    # Add English original text
    body += '## Nội Dung Gốc (Tiếng Anh)\n\n'
    body += '```\n'
    body += text[:200000] if text else '[No text extracted - PDF may be image-based]'
    body += '\n```\n'

    # Save
    safe_name = re.sub(r'[^\w\-]+', '-', name.replace('.pdf', ''))[:80]
    slug = re.sub(r'-+', '-', safe_name).strip('-').lower()
    if not slug:
        slug = 'pdf-' + hashlib.md5(name.encode()).hexdigest()[:8]

    out_path = DOCS_DIR / subdir / (slug + '.md')
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(body, encoding='utf-8')
    return out_path, subdir, slug, len(body)


def main():
    print(f"Processing {len(PDF_NEW)} NEW PDFs...", file=sys.stderr)
    start = time.time()

    written = []
    errors = []
    for i, p in enumerate(PDF_NEW, 1):
        try:
            out, sub, slug, body_len = build_page(p)
            written.append({'pdf': p['path'], 'output': str(out), 'subdir': sub, 'slug': slug, 'body_len': body_len})
            if i % 20 == 0 or i == len(PDF_NEW):
                elapsed = time.time() - start
                rate = i / elapsed
                eta = (len(PDF_NEW) - i) / rate if rate else 0
                print(f"  [{i}/{len(PDF_NEW)}] {rate:.2f}/s ETA={eta:.0f}s", file=sys.stderr)
        except Exception as e:
            errors.append({'pdf': p['path'], 'error': str(e)})

    print(f"\n=== Done ===")
    print(f"  Written: {len(written)}")
    print(f"  Errors:  {len(errors)}")

    # Stats by subdir
    from collections import Counter
    cat_count = Counter(w['subdir'] for w in written)
    print(f"  By subdir:")
    for cat, count in cat_count.most_common():
        print(f"    {cat:20s} {count:3d}")

    # Save manifest
    out_manifest = r"C:\Users\Henry\Documents\tennis-wiki\scripts\pdf_written.json"
    with open(out_manifest, 'w', encoding='utf-8') as f:
        json.dump({'written': written, 'errors': errors}, f, ensure_ascii=False, indent=2)
    print(f"\nManifest saved: {out_manifest}")


if __name__ == "__main__":
    main()
