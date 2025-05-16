# coding=utf8
# the above tag defines encoding for this document and is for Python 2.x compatibility

import re

regex = r"^([\w\s]+|\s*\"[^\"]+\")\s+([\w\d\.\-]+|\"[^\"]+\")$"

test_str = ("""
outfit "W-120 Nitrogen Thruster"
	cost 19500
	category "Engines"
	thumbnail "outfit/small rebels thruster"
	"mass" 25
	"outfit space" -15
	"engine capacity" -25
	"thrust" 17.8
	"thrusting energy" 3.8
	"thrusting heat" 4.2
	"flare sprite" "effect/nitrogen flare/small"
		"frame rate" 11
	"flare sound" "atomic small"
""")

matches = re.finditer(regex, test_str, re.MULTILINE)

for matchNum, match in enumerate(matches, start=1):
    
    print ("Match {matchNum} was found at {start}-{end}: {match}".format(matchNum = matchNum, start = match.start(), end = match.end(), match = match.group()))
    
    for groupNum in range(0, len(match.groups())):
        groupNum = groupNum + 1
        
        print ("Group {groupNum} found at {start}-{end}: {group}".format(groupNum = groupNum, start = match.start(groupNum), end = match.end(groupNum), group = match.group(groupNum)))

# Note: for Python 2.7 compatibility, use ur"" to prefix the regex and u"" to prefix the test string and substitution.
