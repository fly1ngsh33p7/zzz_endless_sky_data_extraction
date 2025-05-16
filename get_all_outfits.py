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
    regex = r"^([\s\w]+|\s*\"[^\"]+\")\s+([\w\d\.\-]+|\"[^\"]+\"|\`[^\`]+\`)$"
    
    fields = {}
    i = 0
    while i < len(block_lines):
        line = block_lines[i]
        stripped_line = line.strip()
        if not stripped_line:
            i += 1
            continue

        # Match key-value pairs
        match = re.match(regex, stripped_line)
        if match:
            key = match.group(1).strip().replace('"', '').replace('`', '')
            value = match.group(2).strip().replace('"', '').replace('`', '')

            # Convert numeric values to int or float
            if value.isdigit():
                value = int(value)
            else:
                try:
                    value = float(value)
                except ValueError:
                    pass

            fields[key] = value
            i += 1
            continue

        # Handle standalone keys followed by indented values
        current_indent = len(line) - len(line.lstrip())
        if i + 1 < len(block_lines):
            next_line = block_lines[i + 1]
            next_indent = len(next_line) - len(next_line.lstrip())
            if next_indent > current_indent:  # Check if the next line is more indented
                key = stripped_line.replace('"', '').strip()
                sub_dict = {}
                values = []
                i += 1
                while i < len(block_lines):
                    next_line = block_lines[i]
                    next_indent = len(next_line) - len(next_line.lstrip())
                    if next_indent == current_indent + 1:  # Collect values with one more indentation
                        # Check if the line matches a key-value pair
                        sub_match = re.match(regex, next_line.strip())
                        if sub_match:
                            sub_key = sub_match.group(1).strip().replace('"', '')
                            sub_value = sub_match.group(2).strip().replace('"', '')
                            # Convert numeric values to int or float
                            if sub_value.isdigit():
                                sub_value = int(sub_value)
                            else:
                                try:
                                    sub_value = float(sub_value)
                                except ValueError:
                                    pass
                            sub_dict[sub_key] = sub_value
                        else:
                            values.append(next_line.strip().replace('"', ''))
                        i += 1
                    elif next_indent == current_indent:  # Stop if indentation matches the current level
                        break
                    else:  # Skip block_lines with unexpected indentation
                        i += 1
                # Add either a dictionary or a list based on the content
                fields[key] = sub_dict if sub_dict else values
                continue

        # If no match, treat as a standalone key
        fields[stripped_line.replace('"', '').strip()] = True
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