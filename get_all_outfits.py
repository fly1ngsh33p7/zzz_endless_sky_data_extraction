#!/usr/bin/env python3
import argparse
import os
import re
import json
from pathlib import Path


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
        match = re.match(r'^\s*outfit\s+"([^"]+)"', line)
        if match:
            name = match.group(1)
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


def parse_outfit_fields(block_lines):
    """Parse the fields of an outfit block into a dictionary."""
    fields = {}
    i = 0
    while i < len(block_lines):
        line = block_lines[i]
        # Skip empty lines (already cleaned)
        if not line:
            i += 1
            continue
        # Skip lines starting with "description"
        if line.startswith("description"):
            i += 1
            continue
        
        # Match key-value pairs like: "key" value or key "value" or key value
        match = re.match(r"^([\w\s]+|\s*\"[^\"]+\")\s+([\w\d\.\-]+|\"[^\"]+\")$", line, re.MULTILINE)
        
        print(match)
        
        if match:
            key = match.group(1).strip().replace(" ", "_").replace('"', '')  # Replace spaces with underscores and remove quotes
            value = match.group(2).strip()
            # Convert numeric values to int or float
            if value.isdigit():
                value = int(value)
            else:
                try:
                    value = float(value)
                except ValueError:
                    pass
            
            # Check if the next line has greater indentation (sub-list or sub-dictionary)
            if i + 1 < len(block_lines) and block_lines[i + 1].startswith("\t" * (block_lines[i].count("\t") + 1)):
                sub_list = []
                i += 1
                while i < len(block_lines) and block_lines[i].startswith("\t" * (block_lines[i - 1].count("\t") + 1)):
                    sub_list.append(block_lines[i])
                    i += 1
                fields[key] = sub_list
                continue
            else:
                fields[key] = value
        else:
            # Handle standalone keywords (e.g., "weapon")
            if i + 1 < len(block_lines) and block_lines[i + 1].startswith("\t" * (block_lines[i].count("\t") + 1)):
                sub_list = []
                i += 1
                while i < len(block_lines) and block_lines[i].startswith("\t" * (block_lines[i - 1].count("\t") + 1)):
                    sub_list.append(block_lines[i])
                    i += 1
                fields[line.replace('"', '').strip()] = sub_list
                continue
            else:
                fields[line.replace('"', '').strip()] = True
        i += 1
    return fields

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
    
    # Write JSON
    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(all_outfits, f, indent=2, ensure_ascii=False)
    
    total_outfits = sum(len(outfits) for outfits in all_outfits.values())
    print(f"Wrote {args.output} ({len(all_outfits)} categories, {total_outfits} outfits)")

if __name__ == "__main__":
    main()