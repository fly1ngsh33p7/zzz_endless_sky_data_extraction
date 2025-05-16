import re

regex = r"^([\s\w]+|\s*\"[^\"]+\")\s+([\w\d\.\-]+|\"[^\"]+\"|\`[^\`]+\`)$"

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
	description `Celebration Modules have long since become associated with the Coalition's great sporting events; trained Heliarch fightercraft engage in "spectral dogfights," where the bright swathes of colour put on a great spectacle for the crowds during the downtime between athletic competitions.`
	description "	To reduce potential complications with starlets colliding with ships, the rockets contain a small proximity sensor that forces them to explode a distance away from potential victims."
""")

block_lines = test_str.splitlines()
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

# Print the fieldsing dictionary
print(fields)