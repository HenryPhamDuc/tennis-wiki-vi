#!/usr/bin/env python3
"""Regenerate section index.md files for all categories."""
import re
from pathlib import Path
from datetime import datetime

DOCS = Path(r"C:\Users\Henry\Documents\tennis-wiki\docs")

SECTION_META = {
    'ky-thuat': ('🎾', 'Kỹ thuật Tennis', 'Forehand, backhand, serve, volley, footwork — từ cơ bản đến nâng cao'),
    'co-sinh-hoc': ('🦴', 'Cơ sinh học Tennis', 'Kinetic chain, tensegrity, wave theory, proprioception'),
    'chien-thuat': ('🎯', 'Chiến thuật Tennis', '70% Rule, 3-shot patterns, serve & volley'),
    'tam-ly': ('🧠', 'Tâm lý Tennis', 'Pre-performance routine, breathing, pressure management'),
    'the-luc': ('🏃', 'Thể lực Tennis', 'Proprioception programs, spiral chain, age-50+ safety'),
    'tay-vot': ('👤', 'Tay vợt chuyên nghiệp', 'Phân tích kỹ thuật và chiến thuật của các tay vợt hàng đầu'),
    'cam-nang': ('📚', 'Cẩm nang Tennis', 'Các cẩm nang đầy đủ, hệ thống, từ cơ bản đến chuyên sâu'),
    'tham-khao': ('📖', 'Tài liệu tham khảo', 'Lý thuyết sóng, biomechanics, methodology nâng cao, sách PDF'),
    'wiki': ('🗒️', 'Wiki gốc', 'Các bài viết gốc từ Obsidian vault'),
    'he-thong': ('⚙️', 'Hệ thống tổng thể', 'Các hệ thống tennis toàn diện'),
}

for section, (emoji, title, desc) in SECTION_META.items():
    d = DOCS / section
    if not d.exists():
        d.mkdir(parents=True, exist_ok=True)
    md_files = sorted([f for f in d.iterdir() if f.suffix == '.md' and f.name != 'index.md'])
    # Sort: PDF books first (start with letter or known prefix), then articles
    def sort_key(f):
        try:
            raw = f.read_text(encoding='utf-8', errors='replace')[:500]
            # Get title
            if raw.startswith('---\n'):
                end = raw.find('\n---\n', 4)
                if end > 0:
                    fm = raw[4:end]
                    m = re.search(r'^title:\s*"?(.+?)"?$', fm, re.MULTILINE)
                    if m:
                        return m.group(1).lower()
            return f.stem.lower()
        except Exception:
            return f.stem.lower()

    md_files = sorted(md_files, key=sort_key)

    lines = [
        f'# {emoji} {title}',
        '',
        f'*{desc}*',
        '',
        f'**Tổng số bài viết:** {len(md_files)}',
        '',
        '## Danh sách bài viết',
        '',
    ]
    for f in md_files:
        try:
            raw = f.read_text(encoding='utf-8', errors='replace')
            title_hint = None
            body = raw
            if body.startswith('---\n'):
                end = body.find('\n---\n', 4)
                if end > 0:
                    body = body[end + 5:]
            for ln in body.split('\n'):
                m = re.match(r'^#\s+(.+)$', ln)
                if m:
                    title_hint = m.group(1).strip()
                    break
            display = title_hint or f.stem.replace('-', ' ').title()
        except Exception:
            display = f.stem.replace('-', ' ').title()
        lines.append(f'- [{display}]({f.name})')
    (d / 'index.md').write_text('\n'.join(lines) + '\n', encoding='utf-8')
    print(f"  {section:15s} → {len(md_files)} bài viết")

# Also update the main index.md article count
main_idx = DOCS / 'index.md'
if main_idx.exists():
    text = main_idx.read_text(encoding='utf-8')
    # Update count in 'Về dự án' section
    text = re.sub(
        r'\*\*~?\d+ bài viết\*\*',
        f'**~834 bài viết**',
        text,
        count=1
    )
    main_idx.write_text(text, encoding='utf-8')
    print(f"\nUpdated main index.md")
