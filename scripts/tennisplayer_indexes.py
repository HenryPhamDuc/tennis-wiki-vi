#!/usr/bin/env python3
"""
Generate tennisplayer/index.md (hub) + per-section index pages.
Reads master TOC + 15 section TOCs to build hierarchy.
"""
import zipfile, xml.etree.ElementTree as ET, re
from pathlib import Path
from collections import OrderedDict
from urllib.parse import unquote
import unicodedata
import os

SRC = Path(r"H:\Play Tennis\tennisplayer.net")
DST = Path(r"C:\Users\Henry\Documents\tennis-wiki\docs\tennisplayer")


def read_toc(path):
    if not Path(path).exists():
        return []
    z = zipfile.ZipFile(path)
    doc_xml = z.read('word/document.xml').decode('utf-8')
    rels_xml = z.read('word/_rels/document.xml.rels').decode('utf-8')
    rels = {}
    for m in re.finditer(r'<Relationship\s+Id="([^"]+)"\s+Type="[^"]+"\s+Target="([^"]+)"', rels_xml):
        rels[m.group(1)] = m.group(2)
    root = ET.fromstring(doc_xml)
    para_list = []
    for para in root.iter('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}p'):
        text_parts = []
        link_target = None
        for child in para.iter():
            tag = child.tag.split('}')[-1]
            if tag == 't':
                text_parts.append(child.text or '')
            elif tag == 'hyperlink':
                rid = child.attrib.get('{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id')
                if rid:
                    link_target = rels.get(rid)
        text = ''.join(text_parts)
        if text.strip() or link_target:
            para_list.append((text, link_target))
    return para_list


def normalize_link(link):
    if not link:
        return ""
    if link.startswith("file:///"):
        link = link[8:]
    elif link.startswith("file://"):
        link = link[7:]
    return unquote(link)


def slugify(text):
    text = unicodedata.normalize('NFC', text.strip())
    text = re.sub(r'[<>:"/\\|?*]', '', text)
    text = re.sub(r'\s+', '-', text)
    text = re.sub(r'-+', '-', text)
    text = text.strip('-').lower()
    return text[:100]


# Master TOC structure (manually mapped to dst slugs)
SECTIONS = OrderedDict([
    ("Ultimate Fundamentals", ("Fundamentals", "ultimate-fundamentals",
        r"H:\Play Tennis\tennisplayer.net\Fundamentals\Ultimate Fundamentals\Ultimate Fundamentals TOC.docx")),
    ("Ultimate Drill Games", ("Fundamentals", "ultimate-drill-games",
        r"H:\Play Tennis\tennisplayer.net\Fundamentals\Ultimate Drill Games\Ultimate Drill Games TOC.docx")),
    ("Teaching Systems", ("Fundamentals", "teaching-systems",
        r"H:\Play Tennis\tennisplayer.net\Fundamentals\Teaching Systems\Teaching SystemsTOC.docx")),
    ("Famous Coaches (and Players)", ("Fundamentals", "famous-coaches",
        r"H:\Play Tennis\tennisplayer.net\Fundamentals\Famous Coaches\Famous Coaches TOC.docx")),
    ("Classic Lessons", ("Fundamentals", "classic-lessons",
        r"H:\Play Tennis\tennisplayer.net\Fundamentals\Classic Lessons\Classic Lessons TOC.docx")),
    ("Footwork", ("Fundamentals", "footwork",
        r"H:\Play Tennis\tennisplayer.net\Fundamentals\Footwork\Footwork TOC.docx")),
    ("Strategy and Statistics", ("Fundamentals", "strategy-and-statistics",
        r"H:\Play Tennis\tennisplayer.net\Fundamentals\Strategy\Strategy TOC.docx")),
    ("Mental Game", ("Fundamentals", "mental-game",
        r"H:\Play Tennis\tennisplayer.net\Fundamentals\Mental game\Mental game TOC.docx")),
    ("Physical Training", ("Fundamentals", "physical-training",
        r"H:\Play Tennis\tennisplayer.net\Fundamentals\Physical Training\Physical Training TOC.docx")),
    ("High Performance", ("Fundamentals", "high-performance",
        r"H:\Play Tennis\tennisplayer.net\Fundamentals\High Performance\High Performance TOC.docx")),
    ("Advanced Tennis", ("Stroke Analysis", "advanced-tennis",
        r"H:\Play Tennis\tennisplayer.net\Stroke Analysis\Advanced Tennis\Advanced Tennis TOC.docx")),
    ("Science of Biomechanics", ("Stroke Analysis", "science-of-biomechanics",
        r"H:\Play Tennis\tennisplayer.net\Stroke Analysis\Biomechanics\Science of Biomechanics TOC.docx")),
    ("Mysteries of the Heavy Ball", ("Stroke Analysis", "mysteries-of-the-heavy-ball",
        r"H:\Play Tennis\tennisplayer.net\Stroke Analysis\The Heavy Ball\The Heavy Ball TOC.docx")),
    ("Tour Strokes", ("Stroke Analysis", "tour-strokes",
        r"H:\Play Tennis\tennisplayer.net\Stroke Analysis\Tour strokes\Tour strokes TOC.docx")),
    ("Tennis Science", ("More", "tennis-science",
        r"H:\Play Tennis\tennisplayer.net\More\Tennis Science\Tennis Science TOC.docx")),
])


# Read master TOC
master_toc = read_toc(str(SRC / "TennisplayerTOC.docx"))


# ============================================================
# Generate HUB INDEX (tennisplayer/index.md)
# ============================================================

hub_md = ['---']
hub_md.append('title: "Tennisplayer.net Archive"')
hub_md.append('subtitle: "Hub for the legendary tennisplayer.net teaching library"')
hub_md.append('language: en')
hub_md.append('vault: tennisplayer.net archive')
hub_md.append('created: 2026-06-21')
hub_md.append('updated: 2026-06-21')
hub_md.append('source: "tennisplayer.net (John Yandell, 2002-2022)"')
hub_md.append('---')
hub_md.append('')
hub_md.append('# Tennisplayer.net Archive')
hub_md.append('')
hub_md.append('> **A teaching archive from tennisplayer.net** — founded and edited by John Yandell (2002-2022), one of the most influential online tennis teaching resources in the world. This archive preserves the **Fundamentals**, **Stroke Analysis**, and **More** sections — 15 sub-libraries of detailed articles, lessons, drills, and player portraits by the world\'s top coaches.')
hub_md.append('')
hub_md.append('## Browse by Section')
hub_md.append('')

# Count articles per section
by_category = OrderedDict([('Fundamentals', []), ('Stroke Analysis', []), ('More', [])])
total_articles = 0
for title, (cat, slug, _) in SECTIONS.items():
    section_dir = DST / slug
    if section_dir.exists():
        count = len([f for f in section_dir.iterdir() if f.suffix == '.md' and f.name != 'index.md'])
    else:
        count = 0
    total_articles += count
    by_category[cat].append((title, slug, count))

hub_md.append(f'**Total articles:** {total_articles} across 15 sub-libraries')
hub_md.append('')

for cat, sections in by_category.items():
    if not sections:
        continue
    total_in_cat = sum(c for _, _, c in sections)
    hub_md.append(f'### {cat} ({total_in_cat} articles across {len(sections)} sub-libraries)')
    hub_md.append('')
    for title, slug, count in sections:
        hub_md.append(f'- **[{title}]({slug}/index.md)** — {count} articles')
    hub_md.append('')

hub_md.append('## About this Archive')
hub_md.append('')
hub_md.append('**Tennisplayer.net** was founded by John Yandell and grew into one of the most comprehensive free online tennis teaching libraries. After 20+ years, the site contains thousands of articles, videos, and forum discussions contributed by coaches and players worldwide.')
hub_md.append('')
hub_md.append('**Authors featured:**')
hub_md.append('')
hub_md.append('- **John Yandell** — Editor-in-Chief')
hub_md.append('- **Bob Hansen** — Footwork pioneer')
hub_md.append('- **Michael Friedman** — Teaching systems')
hub_md.append('- **Jim Loehr** — Mental toughness')
hub_md.append('- **Craig Kain** — Strategy')
hub_md.append('- **Toly Rusakov** — Biomechanics')
hub_md.append('- **Doug King** — High Performance')
hub_md.append('- **Andy Durham** — Statistics')
hub_md.append('- **Paul Hanori, MD** — Sports medicine')
hub_md.append('')
hub_md.append('## Reading Notes')
hub_md.append('')
hub_md.append('- All articles are in **English**')
hub_md.append('- Articles have been converted from the original `.docx` files via pandoc')
hub_md.append('- Embedded images from the Word documents are preserved where present')
hub_md.append('- Article ordering follows the original TOC of each sub-library')
hub_md.append('')

hub_path = DST / 'index.md'
hub_path.write_text('\n'.join(hub_md), encoding='utf-8')
print(f"Wrote {hub_path} ({len(hub_md)} lines)")


# ============================================================
# Generate SECTION INDEX PAGES (per sub-library)
# ============================================================

def build_section_index(title, cat, slug, toc_path):
    """Build section index page from TOC + actual MD files in dst folder."""
    paras = read_toc(toc_path)
    section_dir = DST / slug
    md_files = sorted([f.stem for f in section_dir.iterdir()
                      if f.suffix == '.md' and f.name != 'index.md'])

    sec_md = ['---']
    sec_md.append(f'title: "{title}"')
    sec_md.append(f'category: "{cat}"')
    sec_md.append('language: en')
    sec_md.append(f'source: "tennisplayer.net /{cat}/{title}"')
    sec_md.append('created: 2026-06-21')
    sec_md.append('updated: 2026-06-21')
    sec_md.append('---')
    sec_md.append('')
    sec_md.append(f'# {title}')
    sec_md.append('')
    sec_md.append(f'**Articles:** {len(md_files)}')
    sec_md.append(f'**Parent hub:** [Tennisplayer.net Archive](../index.md)')
    sec_md.append('')

    # Find section overview (paragraphs with no links before first linked article)
    overview_lines = []
    found_first_link = False
    toc_articles = []  # List of (slug, title) in TOC order

    for text, link in paras:
        if link:
            norm = normalize_link(link)
            fname = os.path.basename(norm).replace('.docx', '').replace('.html', '')
            article_slug = slugify(fname)
            # Skip TOC links (TOC files don't have article slugs)
            if 'TOC' in fname.upper():
                continue
            toc_articles.append((article_slug, fname, text))
            found_first_link = True
        else:
            if not found_first_link and text.strip() and 'TOC' not in text.upper() and 'Top of Form' not in text:
                # Skip first "Section Overview" type labels
                if text.strip().lower() not in ['section overview', title.lower()]:
                    # Could be the overview paragraph
                    pass

    # Group by subsection: walk TOC paragraphs, treating non-linked text as subsection header
    current_section = "Articles"
    section_items = []
    sections_built = OrderedDict()
    found_first_link = False

    for text, link in paras:
        if link:
            norm = normalize_link(link)
            fname = os.path.basename(norm).replace('.docx', '').replace('.html', '')
            article_slug = slugify(fname)
            if 'TOC' in fname.upper():
                continue
            found_first_link = True
            # Check if this slug exists in md_files
            if article_slug in md_files:
                # Use the TOC text as display name (cleaner than filename)
                display_name = text.strip() if text.strip() else fname
                display_name = re.sub(r'^John Yandell\s*$', '', display_name, flags=re.IGNORECASE).strip()
                if not display_name:
                    display_name = fname
                section_items.append((article_slug, display_name, fname))
        else:
            if found_first_link:
                # This could be a subsection header
                text_clean = text.strip()
                if text_clean and text_clean.lower() not in ['section overview', title.lower(),
                    'top of form'] and not text_clean.startswith('http'):
                    # Flush current section
                    if section_items:
                        sections_built[current_section] = section_items
                    current_section = text_clean
                    section_items = []

    # Flush final
    if section_items:
        sections_built[current_section] = section_items

    # If we got no subsections, all articles under "Articles"
    if not sections_built and md_files:
        # Build from md_files in sorted order
        sections_built["Articles"] = []
        for stem in md_files:
            # Try to find display name from TOC
            display = stem.replace('-', ' ').title()
            for slug, fname, txt in toc_articles:
                if slug == stem:
                    display = txt.strip() if txt.strip() else fname
                    break
            sections_built["Articles"].append((stem, display, stem))

    # Render sections
    for sec_name, items in sections_built.items():
        if not items:
            continue
        sec_md.append(f'## {sec_name}')
        sec_md.append('')
        for article_slug, display_name, fname in items:
            sec_md.append(f'- [{display_name}]({article_slug}.md)')
        sec_md.append('')

    sec_md.append('---')
    sec_md.append('')
    sec_md.append(f'**Source:** [{title} TOC](https://www.tennisplayer.net/) (John Yandell, 2002-2022)')
    sec_md.append('')

    out = DST / slug / 'index.md'
    out.write_text('\n'.join(sec_md), encoding='utf-8')
    print(f"Wrote {out} ({len(md_files)} articles)")


for title, (cat, slug, toc_path) in SECTIONS.items():
    build_section_index(title, cat, slug, toc_path)


print("\n=== DONE ===")
