#!/usr/bin/env python3
"""
Convert Players/ folder → tennis-wiki docs/tay-vot/

Source: C:/Users/Henry/Documents/MY VAULT/Documents/Obsidian Vault/tennis-vault/Players
Target: C:/Users/Henry/Documents/tennis-wiki/docs/tay-vot/

2 MD files = full articles
15 PDFs = link-only articles
"""
import os
import re
import sys
import json
import hashlib
from pathlib import Path
from datetime import datetime

SRC = Path(r"C:\Users\Henry\Documents\MY VAULT\Documents\Obsidian Vault\tennis-vault\Players")
DOCS = Path(r"C:\Users\Henry\Documents\tennis-wiki\docs\tay-vot")
DOCS.mkdir(parents=True, exist_ok=True)


def slugify(text):
    text = re.sub(r'[\\/:*?"<>|]', '', text)
    text = re.sub(r'\s+', '-', text.strip())
    text = re.sub(r'-{2,}', '-', text)
    return text.strip('-').lower()


def main():
    # Read MD files
    md_files = sorted(SRC.rglob("*.md"))
    pdf_files = sorted(SRC.rglob("*.pdf"))
    print(f"Source: {len(md_files)} MD, {len(pdf_files)} PDF")

    # Existing slugs
    existing = set()
    for f in DOCS.rglob("*.md"):
        if f.name != "index.md":
            existing.add(f.stem.lower())
    print(f"Existing in tay-vot/: {len(existing)}")

    # Build page index for cross-category wiki-links
    page_index = {}
    for f in DOCS.parent.rglob("*.md"):
        if f.name == 'index.md':
            continue
        s = slugify(f.stem)
        cat = f.parent.name
        page_index[s] = {'source': f, 'cat': cat}
    print(f"Page index: {len(page_index)}")

    written = []

    # Process MD files (full articles)
    print("\n=== Processing MD files (full articles) ===")
    for f in md_files:
        text = f.read_text(encoding='utf-8', errors='replace')
        norm = re.sub(r'\s+', ' ', text).strip()

        # Determine slug from filename
        slug = slugify(f.stem)
        if slug in existing:
            print(f"  skip (exists): {slug}")
            continue

        # Extract title from first H1 or filename
        title_match = re.search(r'^#\s+(.+)$', text, re.MULTILINE)
        if title_match:
            title = title_match.group(1).strip()
        else:
            title = f.stem

        # Determine sub-category
        rel = f.relative_to(SRC)
        sub = rel.parts[0]  # e.g. "Federer"

        # Build YAML
        lines = ['---']
        lines.append(f'title: "{title}"')
        lines.append('language: vi')
        lines.append('vault: Players')
        lines.append(f'created: {datetime.now().strftime("%Y-%m-%d")}')
        if 'English-Vietnamese' in f.stem or 'english-vietnamese' in f.stem.lower():
            lines.append('subtitle: "English-Vietnamese Edition"')
            lines.append('tags: ["federer", "tay-vợt", "adaptation", "english-vietnamese"]')
        else:
            lines.append('tags: ["federer", "tay-vợt", "phân-tích"]')
        lines.append('category: "tay-vot"')
        lines.append(f'sub_player: "{sub}"')
        lines.append(f'vault_path: "{rel}"')
        lines.append('---')
        yaml = '\n'.join(lines)

        # Rewrite wiki-links
        def repl(m):
            inner = m.group(1)
            if '|' in inner:
                target, alias = inner.split('|', 1)
            else:
                target, alias = inner, None
            target_name = os.path.basename(target).replace('.md', '')
            target_slug = slugify(target_name)
            if target_slug in page_index:
                target_cat = page_index[target_slug].get('cat', 'tay-vot')
                if target_cat == 'tay-vot':
                    link = f"{target_slug}.md"
                else:
                    link = f"../{target_cat}/{target_slug}.md"
                display = alias if alias else target_name
                return f'[{display}]({link})'
            return f'_{target_name}_'

        body = re.sub(r'\[\[([^\]]+)\]\]', repl, text)

        out = DOCS / f'{slug}.md'
        out.write_text(yaml + '\n\n' + body, encoding='utf-8')
        existing.add(slug)
        written.append({'type': 'md', 'src': str(f), 'out': str(out), 'sub': sub, 'slug': slug})
        print(f"  ✓ {slug}.md ({len(text)} bytes)")

    # Process PDFs (link-only)
    print("\n=== Processing PDFs (link-only) ===")
    for f in pdf_files:
        slug = slugify(f.stem)
        if slug in existing:
            print(f"  skip (exists): {slug}")
            continue

        rel = f.relative_to(SRC)
        sub = rel.parts[0]
        size_kb = f.stat().st_size // 1024

        # Copy PDF
        pdf_dest = DOCS / f.name
        if not pdf_dest.exists():
            pdf_dest.write_bytes(f.read_bytes())
            print(f"  PDF: {f.name} ({size_kb} KB)")

        # Build link-only article
        title = f.stem
        lines = ['---']
        lines.append(f'title: "{title}"')
        lines.append('language: vi')
        lines.append('vault: Players')
        lines.append(f'created: {datetime.now().strftime("%Y-%m-%d")}')
        lines.append('source_type: "pdf_link"')
        lines.append(f'source_pdf: "{f.name}"')
        lines.append(f'pdf_size_kb: "{size_kb}"')
        lines.append('category: "tay-vot"')
        lines.append(f'sub_player: "{sub}"')
        lines.append(f'vault_path: "{rel}"')
        lines.append('tags: ["tay-vợt", "pdf", "link-only", "federer" if "federer" in f.stem.lower() else "sinner"]')
        lines.append('note: "Bản PDF gốc; chỉ giữ link download, không trích xuất nội dung."')
        lines.append('---')
        yaml = '\n'.join(lines)

        body = f"""# {title}

> **Loại:** PDF gốc (giữ nguyên định dạng)
> **Ngôn ngữ:** Tiếng Anh / song ngữ
> **Dung lượng:** {size_kb} KB

---

## Tải Xuống / Đọc File Gốc

📄 **[{f.name}]({f.name.replace(' ', '%20')})** — Bản PDF đầy đủ, {size_kb} KB.

> **Ghi chú:** Đây là file PDF gốc, giữ nguyên định dạng và font chữ. Tải xuống để đọc nội dung đầy đủ, bao gồm hình ảnh minh họa và các biểu đồ kỹ thuật.

---

## Thông Tin Chung

- **Tên file:** `{f.name}`
- **Tác giả:** Henry Pham (Phạm Đức Hải) — Tennis Future Lab
- **Tay vợt:** {sub}
- **Ngôn ngữ:** Tiếng Anh / song ngữ Anh-Việt
- **Dung lượng:** {size_kb} KB

---

## Các Bài Viết Liên Quan Trong Wiki

- [[Roger Federer Forehand Guide]] — Phân tích forehand Federer
- [[Roger Federer Backhand Guide]] — Phân tích backhand 1 tay
- [[Roger Federer Serve Guide]] — Phân tích serve
- [[Federer Adaptation System — English-Vietnamese]] — Hệ thống thích nghi
- [[Federer Tennis]] — Phân tích tổng quan
- [[USTA High Performance: Federer 3 Forehands]] — 3 forehand models
- [[Federer Vision Technique]] — Kỹ thuật nhìn bóng
- [[The Roger Federer Story — Quest for Perfection]] — Tiểu sử
- [[Federer Code Book]] — Code book (nếu có)
- [[Jannik Sinner — Forehand Model]] — Forehand Sinner

---

> **Khuyến nghị:** Để đọc nội dung đầy đủ với hình ảnh, biểu đồ kỹ thuật và phân tích chi tiết, vui lòng tải file PDF gốc. Bản PDF giữ nguyên định dạng, font chữ chuẩn và có thể in ra để tham khảo offline.
"""

        out = DOCS / f'{slug}.md'
        out.write_text(yaml + '\n\n' + body, encoding='utf-8')
        existing.add(slug)
        written.append({'type': 'pdf-link', 'src': str(f), 'out': str(out), 'sub': sub, 'slug': slug})
        print(f"  ✓ {slug}.md (PDF link, {size_kb} KB)")

    # Save manifest
    with open(r"C:\Users\Henry\Documents\tennis-wiki\scripts\players_manifest.json", 'w', encoding='utf-8') as f:
        json.dump(written, f, ensure_ascii=False, indent=2)
    print(f"\nTotal written: {len(written)}")


if __name__ == "__main__":
    main()
