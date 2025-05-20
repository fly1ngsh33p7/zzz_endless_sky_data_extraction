#!/usr/bin/env python3
import argparse
import os
import re
import json
from pathlib import Path

# key_pattern = re.compile(
#     r"""
#     [\s\w]+
#     |
#     \s*\"[^\"]+\"
#     |
#     \s*\`[^\`]+\`
#     """,
#     re.VERBOSE
# )
key_pattern = r"\s*[\w]+|\s*\"[^\"]+\"|\s*\`[^\`]+\`"
value_pattern = r"[-+]?(?:\d+\.\d*|\.\d+|\d+)(?:[eE][+-]?\d+)?|\"[^\"]+\"|\`[^\`]+\`" 
# does NOT properly match 
#thumbnail outfit/license
# it's parsed to JSON as "thumbnail outfit/license": true 

regex = re.compile(
    rf"^({key_pattern})\s+({value_pattern})$"
)

def remove_comments_from_lines(lines):
    """Remove comments (everything after '#') from all lines."""
    cleaned_lines = []
    for line in lines:
        # Split the line at the first '#' and take the part before it
        line_without_comment = line.split('#', 1)[0].rstrip()
        # Add the line to the result if it's not empty
        if line_without_comment:
            cleaned_lines.append(line_without_comment)
    return cleaned_lines

def parse_outfits(file_path):
    outfits_by_category = {}
    # Read and clean lines (remove comments and empty lines)
    lines = remove_comments_from_lines(file_path.read_text(encoding='utf-8').splitlines())
    i = 0
    while i < len(lines):
        line = lines[i]
        match = re.match(r'^\s*outfit\s+("([^"]+)"|`([^`]+)`)', line)
        if match:
            name = match.group(1).strip().replace('"', '').replace('`', '').replace('\'', '')
            block = []
            i += 1
            # Capture indented block lines
            while i < len(lines) and re.match(r'^\s', lines[i]):
                block.append(lines[i])
                i += 1
            
            # Extract category and store the outfit
            category = extract_category_data(block)
            if category is not None:
                if category not in outfits_by_category:
                    outfits_by_category[category] = []
                outfit_data = parse_outfit_fields(block)
                outfit_data["name"] = name
                outfits_by_category[category].append(outfit_data)
        else:
            i += 1
    return outfits_by_category


def parse_key_value(line):  # Key-Value-Paar extrahieren  
    match = re.match(regex, line)  # Regex-Match durchführen  
    if not match:  
        return None  # kein Key-Value  
    key = match.group(1).strip().replace('"', '').replace('`', '').replace('\'', '')  # Key säubern  
    raw = match.group(2).strip().replace('"', '').replace('`', '').replace('\'', '')  # rohen Wert säubern  
    return key, raw  # Tuple zurückgeben  

def convert_value(raw):  # Wert in int/float oder Bool konvertieren  
    if raw is None:  
        return True  # nur Key → True  
    if raw.isdigit():  
        return int(raw)  # int  
    try:  
        return float(raw)  # float  
    except ValueError:  
        return raw.replace('"', '').replace('`', '').replace('\'', '')  # String

def parse_indented_block(lines, start_idx, indent):  # rekursiver Unterblock-Parser  
    items = []  # Liste der Einträge  
    i = start_idx  # Startindex  
    while i < len(lines):  
        line = lines[i]  # aktuelle Zeile  
        curr_indent = len(line) - len(line.lstrip())  # Einrückung berechnen  
        if curr_indent <= indent:  
            break  # Ende des Blocks  
        stripped = line.strip()  # Inhalt ohne Leerzeichen  
        kv = parse_key_value(stripped)  # Key-Value prüfen  
        if kv:  
            key, raw = kv  # entpacken  
            # weiterer Unterblock?  
            if i + 1 < len(lines) and (len(lines[i+1]) - len(lines[i+1].lstrip())) > curr_indent:  
                nested, new_i = parse_indented_block(lines, i+1, curr_indent)  # rekursiv  
                sub = {"name": convert_value(raw)}  # Basis-Dict  
                for entry in nested:  
                    if isinstance(entry, dict):  
                        sub.update(entry)  # zusammenführen  
                    else:  
                        sub[entry] = True  # reine Keys als Flag  
                items.append({key: [sub]})  # Liste mit einem Dict  
                i = new_i  # Index setzen  
            else:  
                items.append({key: convert_value(raw)})  # simples KV  
                i += 1  # nächstes  
        else:  
            items.append(stripped.replace('"', '').replace('`', '').replace('\'', ''))  # reine Werte  
            i += 1  # nächstes  
    return items, i  # Einträge und neuer Index

def parse_outfit_fields(block_lines):
    fields = {}  # Ergebnis-Dict  
    i = 0  # Startindex  
    while i < len(block_lines):  
        line = block_lines[i]  # aktuelle Zeile  
        stripped = line.strip()  # getrimmter Inhalt  
        if not stripped:  
            i += 1; continue  # leere Zeilen überspringen  
        curr_indent = len(line) - len(line.lstrip())  # aktuelle Einrückung  
        next_indent = (len(block_lines[i+1]) - len(block_lines[i+1].lstrip())  
                       if i+1 < len(block_lines) else None)  # nächste Einrückung  
        kv = parse_key_value(stripped)  # Key-Value prüfen  

        if kv and (next_indent is None or next_indent <= curr_indent):  # einfaches KV  
            key, raw = kv  # entpacken  
            value = convert_value(raw)  # konvertieren  
            if key in fields and isinstance(fields[key], str):  
                fields[key] += "\n\n" + str(value)  # String-Duplikat zusammenführen  
            elif key in fields:  
                if value == fields[key]:
                    print(f"Warning: duplicate key '{key}' with identical not-string Values ({value})!")
                else:
                    print(f"\nError: Duplicate key '{key}' with different not-string Values ({value} vs {fields[key]}), keeping {value}!\nDetails: {fields}\n")
                    # raise ValueError(f"Duplicate key '{key}' with different not-string Values!\nParsed until error: {fields}\n")  # FIXME: is this a Fatal Error?  
            else:  
                fields[key] = value  # speichern  
            i += 1  # nächstes  

        elif next_indent is not None and next_indent > curr_indent:  # verschachtelter Block  
            key = stripped.strip().replace('"', '').replace('`', '').replace('\'', '')  # Block-Key  
            items, new_i = parse_indented_block(block_lines, i+1, curr_indent)  # Unterblock parsen  
            # Flatten: Strings bleiben Liste, Dict-Listen auflösen  
            if items and all(isinstance(it, str) for it in items):  
                fields[key] = items  # Liste von Strings  
            else:  
                sub = {}  # flaches Dict  
                for entry in items:  
                    if isinstance(entry, dict):  
                        for k, v in entry.items():  
                            # ein-Element-Listen von Dicts auspacken  
                            if isinstance(v, list) and len(v) == 1 and isinstance(v[0], dict):  
                                sub[k] = v[0]  
                            else:  
                                sub[k] = v  
                    else:  
                        sub[entry] = True  # reine Keys  
                fields[key] = sub  # speichern  
            i = new_i  # Index setzen  

        else:  
            fields[stripped.strip().replace('"', '').replace('`', '').replace('\'', '')] = True  # nur Key → True  
            i += 1  # nächstes  

    return fields  # gefülltes Dict zurückgeben

def extract_category_data(block_lines):
    # Filter block_lines to include only lines indented with at most one tab character
    filtered_lines = [line.lstrip('\t') for line in block_lines if line.startswith('\t') and not line.startswith('\t\t')]
    
    # Check category
    for line in filtered_lines:
        match = re.match(r'^category\s+"([^"]+)"', line)
        if match:
            return match.group(1)
    return None


def collect_outfits(directories):
    all_outfits = {}
    for d in directories:
        path = Path(d)
        for file in path.rglob('*.txt'):
            try:
                outfits_by_category = parse_outfits(file)
                for category, outfits in outfits_by_category.items():
                    if category not in all_outfits:
                        all_outfits[category] = []
                    all_outfits[category].extend(outfits)
            except Exception as e:
                print(f"Failed to parse {file}: {e}")
                continue
    return all_outfits


def main():
    parser = argparse.ArgumentParser(
        description="Extract all outfits from .txt files and organize them by category"
    )
    parser.add_argument(
        "folders", nargs="+",
        help="One or more folders to scan recursively for .txt files"
    )
    parser.add_argument(
        "--output", "-O", default="outfits.json",
        help="Where to write the JSON output"
    )
    args = parser.parse_args()
    
    print(args.folders)
    
    # Gather all outfits organized by category
    all_outfits = collect_outfits(args.folders)
    
    # Merge similarly written categories # THIS COULD BE UNWANTED BEHAVIOUR!!
    if "Special" in all_outfits and "Specials" in all_outfits:
        all_outfits["Special"].extend(all_outfits.pop("Specials"))
    if "Systems" in all_outfits and "Systems" in all_outfits:
        all_outfits["Systems"].extend(all_outfits.pop("System"))
    if "Ammunition" in all_outfits and "Ammo" in all_outfits:
        all_outfits["Ammunition"].extend(all_outfits.pop("Ammo"))
    
    
    # Write JSON
    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(all_outfits, f, indent=2, ensure_ascii=False)
    
    total_outfits = sum(len(outfits) for outfits in all_outfits.values())
    print(f"Wrote {args.output} ({len(all_outfits)} categories, {total_outfits} outfits)")

if __name__ == "__main__":
    main()