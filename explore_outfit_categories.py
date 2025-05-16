#!/usr/bin/env python3
import argparse
import os
import re
import json
from pathlib import Path


def parse_outfit_blocks(file_path):
    categories = set()
    lines = file_path.read_text(encoding='utf-8').splitlines()
    i = 0
    while i < len(lines):
        line = lines[i]
        match = re.match(r'^\s*outfit\s+"([^"]+)"', line)
        if match:
            name = match.group(1)
            block = []
            i += 1
            # capture indented block lines
            while i < len(lines) and re.match(r'^\s', lines[i]):
                block.append(lines[i])
                i += 1
            
            # extract category of block
            category = extract_category_data(block)
            
            if category is not None:
                categories.add(category)
        else:
            i += 1
    return categories

def collect_categories(directories):
    categories = set()
    for d in directories:
        path = Path(d)
        for file in path.rglob('*.txt'):
            try:
                category_of_block = parse_outfit_blocks(file)
                
                # Ensure category_of_block is not empty
                if category_of_block:
                    # Add all categories from the set
                    categories.update(category_of_block)
            except Exception as e:
                print(f"Failed to parse {file}: {e}")
                continue
    return categories


def extract_category_data(block_lines):
    # Filter block_lines to include only lines indented with at most one tab character
    filtered_lines = [line.lstrip('\t') for line in block_lines if line.startswith('\t') and not line.startswith('\t\t')]
    
    # Check category
    for line in filtered_lines:
        match = re.match(r'^category\s+"([^"]+)"', line)
        if match:
            return match.group(1)
    return None

def main():
    parser = argparse.ArgumentParser(
        description="Extract outfit category names from .txt files"
    )
    parser.add_argument(
        "folders", nargs="+",
        help="One or more folders to scan recursively for .txt files"
    )
    parser.add_argument(
        "--output", "-O", default="outfit_categories.json",
        help="Where to write the JSON output"
    )
    args = parser.parse_args()
    
    print(args.folders)
    
    # Gather all (outfit, category) pairs
    categories = collect_categories(args.folders)
    
    # All outfits
    data = list(categories)
    
    # Write JSON
    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print(f"Wrote {args.output} ({len(data)} categories)")

if __name__ == "__main__":
    main()
