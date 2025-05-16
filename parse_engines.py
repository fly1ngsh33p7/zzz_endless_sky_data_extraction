import argparse
import json
from pathlib import Path
import re

def parse_outfit_blocks(file_path):
    outfits = []
    lines = file_path.read_text(encoding='utf-8').splitlines()
    i = 0
    while i < len(lines):
        line = lines[i]
        m = re.match(r'^\s*outfit\s+"([^"]+)"', line)
        if m:
            name = m.group(1)
            block = []
            i += 1
            # capture indented block lines
            while i < len(lines) and re.match(r'^\s', lines[i]):
                block.append(lines[i])
                i += 1
            outfits.append((name, block))
        else:
            i += 1
    return outfits


def extract_engine_data(name, block_lines):
    # Define a set of keys to ignore during parsing
    ignore_keys = {
        "afterburner effect",
        "thumbnail",
        "flare sprite",
        "flare sound",
        "steering flare sprite",
        "steering flare sound",
        "frame rate",
        "scale",
        "Unplunderable",
        "Display Name",
        "Unique",
        "reinstall",
        "reverse flare sprite",
        "reverse flare sound",
    }

    # Check category
    if not any(re.match(r'^\s*category\s+"Engines"', ln) for ln in block_lines):
        return None

    data = {'name': name}
    i = 0
    # parse licenses separately
    licenses = []
    while i < len(block_lines):
        ln = block_lines[i]
        # licenses block
        if re.match(r'^\s*licenses', ln):
            indent = len(ln) - len(ln.lstrip())
            i += 1
            while i < len(block_lines):
                sub = block_lines[i]
                sub_indent = len(sub) - len(sub.lstrip())
                if sub.strip() == '' or sub_indent <= indent:
                    break
                licenses.append(sub.strip().strip('"'))
                i += 1
            data['licenses'] = licenses
            continue
        # key-value pairs
        kv = re.match(r'^\s*"([^"]+)"\s+"?([^"]+)"?', ln)
        if kv:
            key = kv.group(1)
            val = kv.group(2)
            # Skip ignored keys
            if key in ignore_keys:
                i += 1
                continue
            # try convert numeric
            try:
                if '.' in val:
                    num = float(val)
                else:
                    num = int(val)
                data[key] = num
            except ValueError:
                data[key] = val
        # simple directives: cost without quotes
        m2 = re.match(r'^\s*"?cost"?\s+(\d+)', ln)
        if m2:
            data['cost'] = int(m2.group(1))
        i += 1

    return data


def collect_engines(directories):
    engines = []
    for d in directories:
        path = Path(d)
        for file in path.rglob('*.txt'):
            try:
                outfits = parse_outfit_blocks(file)
            except Exception as e:
                print(f"Failed to parse {file}: {e}")
                continue
            for name, block in outfits:
                engine = extract_engine_data(name, block)
                if engine:
                    # engine['source'] = str(file)
                    engines.append(engine)
    return engines


def main():
    parser = argparse.ArgumentParser(description='Collect engine outfits from Endless Sky config files')
    parser.add_argument('dirs', nargs='*', default=['.'], help='Directories to search (default: current directory (mod directory))') # game directory "/home/thomas/.var/app/com.valvesoftware.Steam/.local/share/Steam/steamapps/common/Endless Sky"
    parser.add_argument('-o', '--output', default='engines.json', help='Output JSON file')
    args = parser.parse_args()

    engines = collect_engines(args.dirs)
    with open(args.output, 'w', encoding='utf-8') as f:
        json.dump(engines, f, indent=2)
    print(f"Collected {len(engines)} engines. Data written to {args.output}")

if __name__ == '__main__':
    main()
