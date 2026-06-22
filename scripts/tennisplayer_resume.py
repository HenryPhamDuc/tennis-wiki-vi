#!/usr/bin/env python3
"""
Fast parallel conversion of remaining docx files to MD.
Uses concurrent.futures.ThreadPoolExecutor with pandoc.
"""
import os
import re
import subprocess
import unicodedata
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

SRC = Path(r"H:\Play Tennis\tennisplayer.net")
DST = Path(r"C:\Users\Henry\Documents\tennis-wiki\docs\tennisplayer")

# Sections still to process (or skip if already done)
SECTIONS = [
    ("Footwork", "Fundamentals/footwork"),
    ("Mental game", "Fundamentals/mental-game"),
    ("Physical Training", "Fundamentals/physical-training"),
    ("High Performance", "Fundamentals/high-performance"),
    ("Advanced Tennis", "Stroke Analysis/advanced-tennis"),
    ("Biomechanics", "Stroke Analysis/biomechanics"),
    ("Heavy Ball", "Stroke Analysis/the-heavy-ball"),
    ("Tour strokes", "Stroke Analysis/tour-strokes"),
    ("Your strokes", "Stroke Analysis/your-strokes"),
    ("Tennis Science", "More/tennis-science"),
]  # Strategy already done in previous run


def slugify(text):
    text = unicodedata.normalize('NFC', text.strip())
    text = re.sub(r'[<>:"/\\|?*]', '', text)
    text = re.sub(r'\s+', '-', text)
    text = re.sub(r'-+', '-', text)
    text = text.strip('-').lower()
    return text[:100]


def convert_one(args):
    docx_path, md_path = args
    if md_path.exists():
        return f"SKIP: {md_path.name}"
    try:
        md_path.parent.mkdir(parents=True, exist_ok=True)
        result = subprocess.run([
            'pandoc', '-f', 'docx', '-t', 'markdown', '--wrap=none',
            str(docx_path), '-o', str(md_path)
        ], capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            # Post-process
            md_text = md_path.read_text(encoding='utf-8', errors='replace')
            title_match = re.search(r'^#\s+(.+?)$', md_text, re.MULTILINE)
            title = title_match.group(1).strip() if title_match else docx_path.stem
            title = re.sub(r'\*+', '', title).strip()

            # Build YAML frontmatter
            lines = ['---',
                     f'title: "{title}"',
                     'source: "tennisplayer.net archive"',
                     'language: en',
                     '---', '']
            # Skip first H1
            content_lines = md_text.split('\n')
            started = False
            for line in content_lines:
                if not started and line.startswith('# '):
                    started = True
                    continue
                lines.append(line)
            md_path.write_text('\n'.join(lines), encoding='utf-8')
            return f"OK: {md_path.name}"
        return f"ERR: {docx_path.name}"
    except Exception as e:
        return f"EXC: {docx_path.name} - {e}"


def main():
    # Collect all docx files in remaining sections
    tasks = []
    for src_folder_name, dst_slug in SECTIONS:
        # Try multiple paths for src
        src_candidates = list(SRC.glob(f"**/{src_folder_name}"))
        if not src_candidates:
            print(f"  [WARN] Source folder not found: {src_folder_name}")
            continue
        src_folder = src_candidates[0]
        # Make sure it's the section folder (not a TOC inside)
        if not src_folder.is_dir():
            continue
        # Skip TOC files
        docx_files = sorted([f for f in src_folder.iterdir()
                            if f.suffix == '.docx' and not f.name.startswith('~$')
                            and 'TOC' not in f.stem])
        if not docx_files:
            print(f"  [INFO] No docx files in {src_folder_name} (TOC only)")
            continue

        dst_folder = DST / dst_slug
        dst_folder.mkdir(parents=True, exist_ok=True)
        print(f"  {dst_slug}: {len(docx_files)} docx files")

        for docx_path in docx_files:
            article_slug = slugify(docx_path.stem)
            md_path = dst_folder / f"{article_slug}.md"
            tasks.append((docx_path, md_path))

    print(f"\n=== Total tasks: {len(tasks)} ===")
    print(f"=== Running parallel (16 workers) ===")

    ok = 0
    skip = 0
    err = 0
    with ThreadPoolExecutor(max_workers=16) as executor:
        futures = {executor.submit(convert_one, t): t for t in tasks}
        for i, fut in enumerate(as_completed(futures), 1):
            result = fut.result()
            if result.startswith("OK"):
                ok += 1
            elif result.startswith("SKIP"):
                skip += 1
            else:
                err += 1
                if err <= 5:
                    print(f"  {result}")
            if i % 50 == 0:
                print(f"  Progress: {i}/{len(tasks)} (ok={ok}, skip={skip}, err={err})")

    print(f"\n=== DONE: ok={ok}, skip={skip}, err={err} ===")


if __name__ == '__main__':
    main()
