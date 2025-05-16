import re

regex = r"^([\s\w]+|\s*\"[^\"]+\")\s+([\w\d\.\-]+|(\"|\`)[^\"]+(\"|\`))$"

# test_str = ("""
# 	cost 19500
# 	category "Engines"
# 	thumbnail "outfit/small rebels thruster"
# 	"mass" 25
# 	"outfit space" -15
# 	"engine capacity" -25
# 	"thrust" 17.8
# 	"thrusting energy" 3.8
# 	"thrusting heat" 4.2
# 	"flare sprite" "effect/nitrogen flare/small"
# 		"frame rate" 11
# 	"flare sound" "atomic small"
# """)
test_str = ("""
	category "Guns"
	licenses
		Remnant
		Test1
		Test2
	cost 471000
	thumbnail "outfit/inhibitor cannon"
	"mass" 16
	"outfit space" -16
	"weapon capacity" -16
	"gun ports" -1
	weapon
		sprite "projectile/inhibitor"
			"frame rate" 10
			"no repeat"
		sound "inhibitor"
		"hit effect" "inhibitor impact" 3
		"inaccuracy" .5
		"velocity" 36
		"random velocity" .5
		"lifetime" 24
		"reload" 13
		"cluster"
		"firing energy" 26
		"firing heat" 45.5
		"firing force" 13
		"shield damage" 26
		"hull damage" 19.5
		"hit force" 39
		"slowing damage" .5
""")

lines = test_str.splitlines()
result = {}
i = 0

while i < len(lines):
    line = lines[i]
    stripped_line = line.strip()
    if not stripped_line:
        i += 1
        continue

    # Match key-value pairs
    match = re.match(regex, stripped_line)
    if match:
        key = match.group(1).strip().replace('"', '').replace('`', '')  # Normalize the key
        value = match.group(2).strip().replace('"', '').replace('`', '')  # Remove quotes from the value

        # Convert numeric values to int or float
        if value.isdigit():
            value = int(value)
        else:
            try:
                value = float(value)
            except ValueError:
                pass

        result[key] = value
        i += 1
        continue

    # Handle standalone keys followed by indented values
    current_indent = len(line) - len(line.lstrip())
    if i + 1 < len(lines):
        next_line = lines[i + 1]
        next_indent = len(next_line) - len(next_line.lstrip())
        if next_indent > current_indent:  # Check if the next line is more indented
            key = stripped_line.replace('"', '').strip()
            values = []
            i += 1
            while i < len(lines):
                next_line = lines[i]
                next_indent = len(next_line) - len(next_line.lstrip())
                if next_indent == current_indent + 1:  # Collect values with one more indentation
                    values.append(next_line.strip().replace('"', ''))
                    i += 1
                elif next_indent == current_indent:  # Stop if indentation matches the current level
                    break
                else:  # Skip lines with unexpected indentation
                    i += 1
            result[key] = values
            continue

    # If no match, treat as a standalone key
    result[stripped_line.replace('"', '').strip()] = True
    i += 1

# Print the resulting dictionary
print(result)