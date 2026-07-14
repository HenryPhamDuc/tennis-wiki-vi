#!/usr/bin/env python3
"""
HTML Reformat Script for tennis-wiki-vi docs/cam-nang/tfl/
Mode A: Pretty-print soup HTML (indentation, ASCII art in <pre>)
Mode B: Add DOCTYPE/head/style, convert single-cell tables to cards
No box-shadow, no tinted backgrounds (Henry's flat CSS preference)
"""

import sys
import re
from bs4 import BeautifulSoup

# Default target file
SRC = r"C:\Users\Henry\GITHUB\tennis-wiki-vi\docs\cam-nang\tfl\Modern_Tennis_Handbook.html"

FLAT_CSS = """
:root {
  --text: #1f2937;
  --muted: #6b7280;
  --border: #e5e7eb;
  --brand: #14285a;
  --accent: #fcd34d;
}
* { box-sizing: border-box; }
body {
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
  line-height: 1.7;
  color: var(--text);
  max-width: 900px;
  margin: 0 auto;
  padding: 24px 16px;
}
h1, h2, h3, h4 { line-height: 1.3; margin: 1.5em 0 0.5em; }
h1 { font-size: 2em; border-bottom: 2px solid var(--brand); padding-bottom: 8px; }
h2 { font-size: 1.5em; }
a { color: var(--brand); text-decoration: underline; }
table { width: 100%; border-collapse: collapse; margin: 1.5em 0; }
th, td { border: 1px solid var(--border); padding: 10px 14px; text-align: left; vertical-align: top; }
th { font-weight: 600; }
.card {
  border: 1px solid var(--border);
  border-radius: 6px;
  padding: 16px 20px;
  margin: 1.5em 0;
}
.card.cover { text-align: center; }
.card ascii { display: block; overflow-x: auto; }
pre.ascii {
  font-family: "Consolas", "Monaco", monospace;
  font-size: 0.85em;
  line-height: 1.4;
  white-space: pre;
  overflow-x: auto;
  border: 1px solid var(--border);
  border-radius: 4px;
  padding: 12px 16px;
  margin: 1em 0;
}
.step-num {
  width: 56px;
  text-align: center;
  color: var(--brand);
  border-right: 4px solid var(--accent);
  font-weight: 700;
  font-size: 1.4em;
  vertical-align: middle;
}
.step-body { padding: 14px 18px; }
table tr { display: table; width: 100%; }
footer.cc-license {
  color: var(--muted);
  font-size: 0.88em;
  border-top: 1px solid var(--border);
  margin-top: 32px;
  padding-top: 14px;
}
"""

def detect_language(soup):
    """Detect language from visible text content (not filename)"""
    visible = soup.get_text(" ", strip=True)
    has_vi = bool(re.search(r"[ăâđêôơưĂÂĐÊÔƠƯáàảãạắằẳẵặấầẩẫậéèẻẽẹếềểễệíìỉĩịóòỏõọốồổỗộớờởỡợúùủũụứừửữựýỳỷỹỵ]", visible))
    return "vi" if has_vi else "en"

def is_ascii_art_paragraph(p):
    """Check if a paragraph is ASCII art (box-drawing chars)"""
    text = p.get_text(" ", strip=True)
    if len(text) < 20:
        return False
    box_chars = set("─│┌┐└┘┼╔╕╓║╗╣╬╠╚╝╞╡╤╧╪═")
    box_count = sum(1 for c in text if c in box_chars)
    return box_count / len(text) > 0.5

def lift_ascii_art(soup):
    """Find consecutive ASCII art paragraphs and lift into single <pre class=\"ascii\">"""
    paragraphs = soup.find_all("p")
    ascii_blocks = []
    current_block = []
    
    for p in paragraphs:
        if is_ascii_art_paragraph(p):
            current_block.append(p.get_text("", strip=True))  # No spaces between chars
        else:
            if current_block:
                ascii_blocks.append("\n".join(current_block))
                current_block = []
    
    if current_block:
        ascii_blocks.append("\n".join(current_block))
    
    # Remove original ASCII paragraphs
    for p in paragraphs:
        if is_ascii_art_paragraph(p):
            p.decompose()
    
    return ascii_blocks

def convert_single_cell_tables(soup):
    """Convert single-cell tables to <div class=\"card\">"""
    tables = soup.find_all("table")
    converted = 0
    
    for tbl in tables:
        rows = tbl.find_all("tr")
        cells = tbl.find_all(["td", "th"])
        
        # Single-cell table: 1 row, 1 cell
        if len(rows) == 1 and len(cells) == 1:
            cell = cells[0]
            card = soup.new_tag("div", attrs={"class": "card cover"})
            # Move cell content into card
            for child in cell.children:
                card.append(child.extract() if hasattr(child, 'extract') else child)
            tbl.replace_with(card)
            converted += 1
    
    return converted

def tag_step_tables(soup):
    """Tag numbered step tables (1-row × 2-col with <strong>N</strong> on left)"""
    tables = soup.find_all("table")
    tagged = 0
    
    for tbl in tables:
        rows = tbl.find_all("tr")
        if len(rows) >= 1:
            for row in rows:
                cells = row.find_all(["td", "th"])
                if len(cells) == 2:
                    left = cells[0]
                    # Check if left cell is just a number
                    left_text = left.get_text(" ", strip=True)
                    if left_text.isdigit() or (left.find("strong") and left.find("strong").get_text(" ", strip=True).isdigit()):
                        left.name = "td"
                        right = cells[1]
                        right.name = "td"
                        left["class"] = "step-num"
                        right["class"] = "step-body"
                        tagged += 1
                        break  # Only tag once per table
    
    return tagged

def reformat(src=None):
    src = src or SRC
    print(f"Reading {src}")
    
    with open(src, "r", encoding="utf-8") as f:
        original = f.read()
    
    original_lines = len(original.splitlines())
    
    # Parse with html5lib (lenient for soup HTML)
    soup = BeautifulSoup(original, "html5lib")
    
    # Detect language from content
    lang = detect_language(soup)
    print(f"Detected language: {lang}")
    
    # Extract title from first h1
    h1 = soup.find("h1")
    title = h1.get_text(" ", strip=True) if h1 else "Tennis WIKI"
    
    # Lift ASCII art
    ascii_blocks = lift_ascii_art(soup)
    print(f"ASCII art blocks lifted: {len(ascii_blocks)}")
    
    # Insert <pre> blocks for ASCII art
    if ascii_blocks:
        for block in ascii_blocks:
            pre = soup.new_tag("pre", attrs={"class": "ascii"})
            pre.string = block
            if h1:
                h1.insert_after(pre)
            else:
                # Insert at top of body
                body = soup.find("body")
                if body:
                    body.insert(0, pre)
    
    # Convert single-cell tables to cards
    cards_converted = convert_single_cell_tables(soup)
    print(f"Single-cell tables converted to cards: {cards_converted}")
    
    # Tag step tables
    steps_tagged = tag_step_tables(soup)
    print(f"Step tables tagged: {steps_tagged}")
    
    # Build the full HTML document
    doctype = "<!DOCTYPE html>"
    html_tag = f'<html lang="{lang}">'
    
    head = soup.new_tag("head")
    meta_charset = soup.new_tag("meta", attrs={"charset": "UTF-8"})
    meta_viewport = soup.new_tag("meta", attrs={"name": "viewport", "content": "width=device-width, initial-scale=1.0"})
    title_tag = soup.new_tag("title")
    title_tag.string = title
    style = soup.new_tag("style")
    style.string = FLAT_CSS.strip()
    
    head.append(meta_charset)
    head.append(meta_viewport)
    head.append(title_tag)
    head.append(style)
    
    # Find or create <html> wrapper
    html_wrapper = soup.find("html")
    if not html_wrapper:
        html_wrapper = soup.new_tag("html", attrs={"lang": lang})
        # Move all body content into html_wrapper
        for child in list(soup.children):
            if child.name not in ["head", "html"]:
                html_wrapper.append(child.extract())
        soup.append(html_wrapper)
    
    # Ensure head is first
    if soup.find("head"):
        soup.find("head").decompose()
    html_wrapper.insert(0, head)
    
    # Ensure body exists
    body = html_wrapper.find("body")
    if not body:
        body = soup.new_tag("body")
        for child in list(html_wrapper.children):
            if child.name not in ["head", "html"]:
                body.append(child.extract())
        html_wrapper.append(body)
    
    # Pretty-print output
    output = doctype + "\n" + str(soup.prettify(formatter="html5"))
    
    # Decode box-drawing entities back to actual characters
    box_entities = {
        "&boxh;": "─", "&boxv;": "│", "&boxdr;": "┌", "&boxdl;": "┐",
        "&boxur;": "└", "&boxul;": "┘", "&boxvr;": "├", "&boxvl;": "┤",
        "&boxhd;": "┬", "&boxhu;": "┴", "&boxvh;": "┼", "&boxH;": "═",
        "&boxV;": "║", "&boxdR;": "╔", "&boxdL;": "╗", "&boxuR;": "╚",
        "&boxuL;": "╝", "&boxvR;": "╠", "&boxvL;": "╣", "&boxHd;": "╦",
        "&boxHu;": "╩", "&boxVh;": "╬", "&boxDR;": "╓", "&boxDL;": "╖",
        "&boxUR;": "╙", "&boxUL;": "╜", "&boxVR;": "╞", "&boxVL;": "╡",
        "&boxdH;": "╤", "&boxuH;": "╧", "&boxVH;": "╪", "&boxDH;": "╥",
        "&boxUH;": "╨",
    }
    for entity, char in box_entities.items():
        output = output.replace(entity, char)
    
    # Write back to source file
    with open(src, "w", encoding="utf-8") as f:
        f.write(output)
    
    output_lines = len(output.splitlines())
    print(f"Output: {output_lines} lines ({output.count(chr(10))} newlines)")
    print(f"Lines: {original_lines} → {output_lines}")
    print(f"Written: {src}")
    
    return {
        "original_lines": original_lines,
        "output_lines": output_lines,
        "ascii_blocks": len(ascii_blocks),
        "cards_converted": cards_converted,
        "steps_tagged": steps_tagged,
    }

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        reformat(sys.argv[1])
    else:
        reformat()