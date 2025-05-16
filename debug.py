import re

regex = r"^([\w\s]+|\s*\"[^\"]+\")\s+([\w\d\.\-]+|\"[^\"]+\")$"

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
    line = lines[i].strip()
    if not line:
        i += 1
        continue

    # Match key-value pairs
    match = re.match(regex, line)
    if match:
        key = match.group(1).strip().replace('"', '')  # Normalize the key
        value = match.group(2).strip().replace('"', '')  # Remove quotes from the value

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
    if i + 1 < len(lines) and lines[i + 1].startswith('\t'):
        key = line.replace('"', '').strip()
        values = []
        i += 1
        while i < len(lines) and lines[i].startswith('\t'):
            values.append(lines[i].strip().replace('"', ''))
            i += 1
        result[key] = values
    else:
        result[line.replace('"', '').strip()] = True
        i += 1

# Print the resulting dictionary
print(result)