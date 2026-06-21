#!/usr/bin/env python3
"""
Phase 4: Convert VN_Tennis_Vault_v3_Final → tennis-wiki docs

Source: C:/Users/Henry/Documents/MY VAULT/Documents/Obsidian Vault/tennis-vault/VN_Tennis_Vault_v3_Final/VN_Tennis_Vault
Target: C:/Users/Henry/Documents/tennis-wiki/docs/

Strategy:
- Use existing YAML frontmatter (Vietnamese field names)
- Convert snake_case YAML to standard English field names
- Map subdirs to existing tennis-wiki categories
- Dedup vs existing 834 articles by content hash
- Skip hub file (Kho Tri Thức Tennis.md) — already a hub concept
"""
import os
import re
import sys
import json
import hashlib
from pathlib import Path
from datetime import datetime
import yaml

SRC = Path(r"C:\Users\Henry\Documents\MY VAULT\Documents\Obsidian Vault\tennis-vault\VN_Tennis_Vault_v3_Final\VN_Tennis_Vault")
DOCS = Path(r"C:\Users\Henry\Documents\tennis-wiki\docs")

# Subdir → tennis-wiki subdir mapping
SUBDIR_MAP = {
    'Bài tập': 'ky-thuat',              # Drills → Kỹ thuật
    'Chiến thuật': 'chien-thuat',         # Tactics
    'Kỹ Thuật': 'ky-thuat',              # Technique
    'THần Kinh Học': 'tam-ly',           # Neuroscience → Psychology
    'Thể lực': 'the-luc',                # Fitness
    'Tài liệu gốc': 'tham-khao',         # Original material → References
    'Volley': 'ky-thuat',                # Volley → Kỹ thuật
}


def slugify(text):
    """Make URL-safe Vietnamese slug (preserve Vietnamese chars)."""
    # Remove path separators, quotes
    text = re.sub(r'[\\/:*?"<>|]', '', text)
    # Replace spaces with hyphens
    text = re.sub(r'\s+', '-', text.strip())
    text = re.sub(r'-{2,}', '-', text)
    return text.strip('-').lower()


def parse_vietnamese_yaml(text):
    """Parse Vietnamese YAML frontmatter (uses snake_case keys)."""
    if not text.startswith('---\n'):
        return None, text
    end = text.find('\n---', 4)
    if end < 0:
        return None, text
    fm_text = text[4:end]
    try:
        fm = yaml.safe_load(fm_text) or {}
    except yaml.YAMLError as e:
        return None, text
    body = text[end + 4:].lstrip('\n')
    return fm, body


def build_standard_yaml(fm, slug, source_path, cat, body_preview):
    """Build standard English-keyed YAML frontmatter from Vietnamese source."""
    title = fm.get('tiêu_đề') or fm.get('tên_gốc') or slug.replace('-', ' ').title()
    en_title = fm.get('tên_gốc') or fm.get('english_title') or ''
    category_type = fm.get('loại') or ''
    level = fm.get('mức_độ') or ''
    tags = fm.get('thẻ') or []
    related = fm.get('liên_quan_đến') or []
    author = fm.get('tác_giả') or 'Henry Pham (Phạm Đức Hải)'
    source = fm.get('nguồn') or ''
    sub_cat = fm.get('danh_mục') or ''
    desc = fm.get('mô_tả') or ''
    date_created = fm.get('ngày_tạo') or fm.get('ngày_phát_hành') or '2025-01-01'

    lines = ['---']
    lines.append(f'title: "{title}"')
    if en_title and en_title != title:
        lines.append(f'original_title: "{en_title}"')
    lines.append('language: vi')
    lines.append('vault: VN_Tennis_Vault_v3_Final')
    lines.append(f'created: {date_created}')
    if category_type:
        lines.append(f'category_type: "{category_type}"')
    if level:
        lines.append(f'level: "{level}"')
    if sub_cat:
        lines.append(f'sub_category: "{sub_cat}"')
    if desc:
        lines.append(f'description: "{desc[:300]}"')
    if tags:
        # Convert to JSON-style list for safety
        tag_str = ', '.join(json.dumps(str(t), ensure_ascii=False) for t in tags)
        lines.append(f'tags: [{tag_str}]')
    if author:
        lines.append(f'author: "{author}"')
    if source:
        lines.append(f'source: "{source}"')
    if related:
        rel_str = ', '.join(json.dumps(str(r), ensure_ascii=False) for r in related)
        lines.append(f'related: [{rel_str}]')
    lines.append(f'vault_path: "{source_path}"')
    lines.append('---')
    return '\n'.join(lines)


def main():
    files = sorted(SRC.rglob("*.md"))
    print(f"Source files: {len(files)}")

    # 1. Compute hashes of existing tennis-wiki docs (for dedup)
    print("Loading existing docs for dedup...")
    existing_hashes = set()
    existing_slugs = set()
    for f in DOCS.rglob("*.md"):
        if f.name == 'index.md':
            continue
        try:
            text = f.read_text(encoding='utf-8', errors='replace')
            norm = re.sub(r'\s+', ' ', text).strip()
            h = hashlib.md5(norm.encode('utf-8', errors='ignore')).hexdigest()
            existing_hashes.add(h)
            existing_slugs.add(f.stem.lower())
        except Exception:
            pass
    print(f"  Existing articles: {len(existing_hashes)}")

    # 2. Build page index for wiki-link resolution
    page_index = {}
    for f in files:
        if f.name == 'Kho Tri Thức Tennis.md':
            continue
        rel = f.relative_to(SRC)
        if len(rel.parts) < 2:
            continue
        sub = rel.parts[0]
        slug = slugify(f.stem)
        page_index[slug] = {
            'source': f,
            'sub': sub,
            'cat': SUBDIR_MAP.get(sub, 'tham-khao'),
        }
    print(f"  Page index: {len(page_index)}")

    # 3. Process each file
    print("\nProcessing files...")
    written = []
    skipped = []
    for f in files:
        if f.name == 'Kho Tri Thức Tennis.md':
            skipped.append({'file': str(f), 'reason': 'hub file (skip)'})
            continue
        rel = f.relative_to(SRC)
        if len(rel.parts) < 2:
            continue
        sub = rel.parts[0]
        slug = slugify(f.stem)

        # Slug dedup
        if slug in existing_slugs:
            skipped.append({'file': str(f), 'reason': f'slug exists: {slug}'})
            continue

        # Read content
        try:
            text = f.read_text(encoding='utf-8', errors='replace')
        except Exception as e:
            print(f"  err reading {f.name}: {e}")
            continue

        # Content hash dedup
        norm = re.sub(r'\s+', ' ', text).strip()
        h = hashlib.md5(norm.encode('utf-8', errors='ignore')).hexdigest()
        if h in existing_hashes:
            skipped.append({'file': str(f), 'reason': 'content hash exists'})
            continue

        # Parse Vietnamese YAML
        fm, body = parse_vietnamese_yaml(text)
        if not fm:
            # No frontmatter — add one
            title = f.stem.replace('-', ' ').title()
            fm = {'tiêu_đề': title}

        # Determine category
        cat = SUBDIR_MAP.get(sub, 'tham-khao')

        # Rewrite wiki-links ([[Page]] → MkDocs link)
        def repl(m):
            inner = m.group(1)
            if '|' in inner:
                target, alias = inner.split('|', 1)
            else:
                target, alias = inner, None
            target_name = os.path.basename(target).replace('.md', '')
            target_slug = slugify(target_name)
            if target_slug in page_index:
                target_cat = page_index[target_slug]['cat']
                if target_cat == cat:
                    link = f"{target_slug}.md"
                else:
                    link = f"../{target_cat}/{target_slug}.md"
                display = alias if alias else target_name
                return f'[{display}]({link})'
            return f'_{target_name}_'
        body = re.sub(r'\[\[([^\]]+)\]\]', repl, body)

        # Build new YAML
        new_fm = build_standard_yaml(fm, slug, str(f.relative_to(SRC.parent)), cat, body[:500])
        full_doc = new_fm + '\n\n' + body

        # Save
        out = DOCS / cat / f'{slug}.md'
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(full_doc, encoding='utf-8')
        written.append({'src': str(f), 'out': str(out), 'cat': cat, 'slug': slug})
        existing_hashes.add(h)  # Prevent intra-batch dup
        existing_slugs.add(slug)

    # Stats
    from collections import Counter
    cat_count = Counter(w['cat'] for w in written)
    print(f"\n=== Results ===")
    print(f"  Written: {len(written)}")
    print(f"  Skipped: {len(skipped)}")
    for c, n in cat_count.most_common():
        print(f"    {c:15s} {n:3d}")

    if skipped:
        print(f"\n  Skip reasons:")
        from collections import Counter
        reasons = Counter(s['reason'] for s in skipped)
        for r, n in reasons.most_common():
            print(f"    {n:3d}: {r}")

    # Save manifest
    with open(r"C:\Users\Henry\Documents\tennis-wiki\scripts\v3_manifest.json", 'w', encoding='utf-8') as f:
        json.dump({'written': written, 'skipped': skipped}, f, ensure_ascii=False, indent=2)
    print(f"\nManifest saved")


if __name__ == "__main__":
    main()
