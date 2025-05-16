import re  # Reguläre Ausdrücke
import json  # JSON-Modul importieren

# Regex für einfache Key-Value-Zeilen
regex = r"^([\s\w]+|\s*\"[^\"]+\")\s+([\w\d\.\-]+|\"[^\"]+\"|\`[^\`]+\`)$"

def parse_key_value(line):  
    match = re.match(regex, line)  # Regex-Match  
    if not match:  
        return None  # kein KV  
    key = match.group(1).strip().strip('"`')  # Key säubern  
    raw = match.group(2).strip().strip('"`')  # Wert säubern  
    return key, raw  # Tuple zurück

def convert_value(raw):  
    if raw is None:  
        return True  # nur Key → True  
    if raw.isdigit():  
        return int(raw)  # int  
    try:  
        return float(raw)  # float  
    except ValueError:  
        return raw  # String

def parse_indented_block(lines, start_idx, indent):  
    items = []  # Ergebnis-Liste  
    i = start_idx  # Startindex  
    while i < len(lines):  
        line = lines[i]  # aktuelle Zeile  
        curr_indent = len(line) - len(line.lstrip())  # Einrückung  
        if curr_indent <= indent:  
            break  # Ende Unterblock  
        stripped = line.strip()  # Inhalt ohne Leerzeichen  
        kv = parse_key_value(stripped)  # Key-Value?  
        if kv:  
            key, raw = kv  # entpacken  
            if (i + 1 < len(lines) and  
               (len(lines[i+1]) - len(lines[i+1].lstrip())) > curr_indent):  # tiefer eingerückt  
                nested, new_i = parse_indented_block(lines, i+1, curr_indent)  # rekursiv  
                sub_dict = {"name": convert_value(raw)}  # Basis-Dict  
                for entry in nested:  # Einträge mergen  
                    if isinstance(entry, dict):  
                        sub_dict.update(entry)  # mergen  
                    else:  
                        sub_dict[entry] = True  # Boolean-Flag  
                items.append({key: [sub_dict]})  # in Liste packen  
                i = new_i  # Index anpassen  
            else:  
                items.append({key: convert_value(raw)})  # simples KV  
                i += 1  # weiter  
        else:  
            items.append(stripped.strip('"`'))  # reine Werte  
            i += 1  # weiter  
    return items, i  # Liste und neuer Index

def parse_block(block_str):  
    lines = block_str.splitlines()  # Zeilen aufteilen  
    fields = {}  # Ergebnis-Dict  
    i = 0  # Startindex  
    while i < len(lines):  
        line = lines[i]  # aktuelle Zeile  
        if not line.strip():  
            i += 1; continue  # leere Zeile überspringen  
        curr_indent = len(line) - len(line.lstrip())  # aktuelle Einrückung  
        next_indent = (len(lines[i+1]) - len(lines[i+1].lstrip())  
                       if i+1 < len(lines) else None)  # Einrückung nächste  
        stripped = line.strip()  # Inhalt  
        kv = parse_key_value(stripped)  # Key-Value?

        if kv and (next_indent is None or next_indent <= curr_indent):  # einfaches KV  
            key, raw = kv  # entpacken  
            value = convert_value(raw)  # konvertieren  
            if key in fields and isinstance(fields[key], str):  
                fields[key] += "\n\n" + str(value)  # Duplikat-String  
            elif key in fields:  
                raise ValueError(f"Duplicate key '{key}' with non-string value")  # Fehler  
            else:  
                fields[key] = value  # speichern  
            i += 1  # weiter

        elif next_indent is not None and next_indent > curr_indent:  # Unterblock  
            key = stripped.strip('"`')  # Block-Key  
            items, new_i = parse_indented_block(lines, i+1, curr_indent)  # Unterblock parsen  
            # Falls nur Strings: Liste, ansonsten flaches Dict  
            if items and all(isinstance(it, str) for it in items):  
                fields[key] = items  # Liste von Strings  
            else:  
                sub = {}  # flaches Dict  
                for entry in items:  # Einträge mergen  
                    if isinstance(entry, dict):  
                        for k, v in entry.items():  
                            # ein-Element-Listen von Dicts auflösen  
                            if isinstance(v, list) and len(v)==1 and isinstance(v[0], dict):  
                                sub[k] = v[0]  # unwrap  
                            else:  
                                sub[k] = v  # übernehmen  
                    else:  
                        sub[entry] = True  # reine Keys als Flag  
                fields[key] = sub  # speichern  
            i = new_i  # Index anpassen

        else:  
            fields[stripped.strip('"`')] = True  # standalone-Key  
            i += 1  # weiter

    return fields

def main():  # Hauptfunktion aufrufen  
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
"""
)  # Testdaten  
    
    fields = parse_block(test_str)  # Parsing aufrufen  
    # JSON-Daten auf der Konsole ausgeben
    print(json.dumps(fields, ensure_ascii=False, indent=4))

if __name__ == "__main__":  # Skriptstart  
    main()
