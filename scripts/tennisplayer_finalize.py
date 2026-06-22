#!/usr/bin/env python3
"""Process remaining edge case folders: Biomechanics, The Heavy Ball, Your strokes."""
import os
import re
import subprocess
import unicodedata
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

SRC = Path(r"H:\Play Tennis\tennisplayer.net")
DST = Path(r"C:\Users\Henry\Documents\tennis-wiki\docs\tennisplayer")


def slugify(text):
    text = unicodedata.normalize('NFC', text.strip())
    text = re.sub(r'[<>:"/\\|?*]', '', text)
    text = re.sub(r'\s+', '-', text)
    text = re.sub(r'-+', '-', text)
    text = text.strip('-').lower()
    return text[:100]


def convert_one(args):
    docx_path, md_path, section_title = args
    if md_path.exists():
        return f"SKIP: {md_path.name}"
    try:
        md_path.parent.mkdir(parents=True, exist_ok=True)
        result = subprocess.run([
            'pandoc', '-f', 'docx', '-t', 'markdown', '--wrap=none',
            str(docx_path), '-o', str(md_path)
        ], capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            md_text = md_path.read_text(encoding='utf-8', errors='replace')
            title_match = re.search(r'^#\s+(.+?)$', md_text, re.MULTILINE)
            title = title_match.group(1).strip() if title_match else docx_path.stem
            title = re.sub(r'\*+', '', title).strip()

            lines = ['---',
                     f'title: "{title}"',
                     f'section: "{section_title}"',
                     'source: "tennisplayer.net archive"',
                     'language: en',
                     '---', '']
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


# Edge case folders (exact case)
TARGETS = [
    ("Stroke Analysis/Biomechanics", "Fundamentals/science-of-biomechanics", "Science of Biomechanics"),
    ("Stroke Analysis/The Heavy Ball", "Stroke Analysis/mysteries-of-the-heavy-ball", "Mysteries of the Heavy Ball"),
    ("Stroke Analysis/Your strokes", "Stroke Analysis/your-strokes", "Your Strokes"),
]


def main():
    tasks = []
    for src_rel, dst_slug, section_title in TARGETS:
        src_folder = SRC / src_rel
        if not src_folder.exists():
            print(f"  [WARN] Not found: {src_rel}")
            continue
        docx_files = sorted([f for f in src_folder.iterdir()
                            if f.suffix == '.docx' and not f.name.startswith('~$')])
        if not docx_files:
            print(f"  [INFO] No docx files in {src_rel}")
            continue
        print(f"  {src_rel}: {len(docx_files)} docx files")

        dst_folder = DST / dst_slug
        dst_folder.mkdir(parents=True, exist_ok=True)
        for docx_path in docx_files:
            article_slug = slugify(docx_path.stem)
            md_path = dst_folder / f"{article_slug}.md"
            tasks.append((docx_path, md_path, section_title))

    print(f"\n=== Total tasks: {len(tasks)} ===")
    ok = skip = err = 0
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
                if err <= 3:
                    print(f"  {result}")
            if i % 30 == 0:
                print(f"  Progress: {i}/{len(tasks)} (ok={ok}, skip={skip}, err={err})")

    print(f"\n=== DONE: ok={ok}, skip={skip}, err={err} ===")


if __name__ == '__main__':
    main()
