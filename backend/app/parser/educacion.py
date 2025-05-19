import json
import re
import dateparser

# Patrón para fechas completas (con o sin mes) y con grupos capturables
date_pattern = re.compile(
    r'\('
        r'('  # Grupo 1: fecha inicial
            r'\d{4}'  # Año suelto
            r'|(?:enero|febrero|marzo|abril|mayo|junio|julio|agosto|septiembre|octubre|noviembre|diciembre)(?:\s+de)?\s+\d{4}'
            r'|(?:janvier|février|mars|avril|mai|juin|juillet|août|septembre|octobre|novembre|décembre)(?:\s+de)?\s+\d{4}'
            r'|(?:januar|februar|märz|april|mai|juni|juli|august|september|oktober|november|dezember)(?:\s+de)?\s+\d{4}'
            r'|(?:january|february|march|april|may|june|july|august|september|october|november|december)(?:\s+de)?\s+\d{4}'
        r')'
    r'\s*-\s*'
        r'('  # Grupo 2: fecha final
            r'\d{4}'
            r'|(?:enero|febrero|marzo|abril|mayo|junio|julio|agosto|septiembre|octubre|noviembre|diciembre)(?:\s+de)?\s+\d{4}'
            r'|(?:janvier|février|mars|avril|mai|juin|juillet|août|septembre|octobre|novembre|décembre)(?:\s+de)?\s+\d{4}'
            r'|(?:januar|februar|märz|april|mai|juni|juli|august|september|oktober|november|dezember)(?:\s+de)?\s+\d{4}'
            r'|(?:january|february|march|april|may|june|july|august|september|october|november|december)(?:\s+de)?\s+\d{4}'
            r'|presente|actualidad|present'
        r')'
    r'\)',
    flags=re.IGNORECASE
)

# Patrón para fechas sueltas tipo (2019)
single_year_pattern = re.compile(r'\(\s*\d{4}\s*\)')

IDIOMAS_FECHA = ['es', 'en', 'fr', 'de']

def has_month(date_str: str) -> bool:
    return bool(re.search(r'[A-Za-z]', date_str))


def intento_parsear_ignorando_palabra_intermedia(fecha_raw: str) -> str:
    """
    Si hay un patrón como 'janvier du 2020', elimina la palabra intermedia
    y vuelve a intentar con dateparser.
    """
    patron = re.compile(r'([A-Za-záéíóúüñç]{5,})\s([a-z]{1,4})\s(\d{4})', re.IGNORECASE)
    match = patron.search(fecha_raw)
    if match:
        palabra1, _, anio = match.groups()
        corregido = f"{palabra1} {anio}"
        parsed = dateparser.parse(corregido, languages=IDIOMAS_FECHA)
        if parsed:
            return parsed.strftime("%m-%Y")
    return ""


def format_fecha(fecha_raw: str) -> str:
    fecha_raw = fecha_raw.replace(" du ", " de ").strip().lower()

    if not has_month(fecha_raw):
        return fecha_raw

    parsed = dateparser.parse(fecha_raw, languages=IDIOMAS_FECHA)
    if parsed:
        return parsed.strftime("%m-%Y")

    # Regla adicional: quitar palabra intermedia
    resultado = intento_parsear_ignorando_palabra_intermedia(fecha_raw)
    if resultado:
        return resultado

    return ""  # si todo falla

def parse_entry_education(entry: str) -> dict:
    lines = entry.strip().split('\n')
    institution = lines[0].strip() if lines else ''
    degree_part = ' '.join(line.strip() for line in lines[1:]) if len(lines) > 1 else ''

    match = date_pattern.search(degree_part)
    if not match or len(match.groups()) < 2:
        result = {'Institution': institution, 'Degree': degree_part}
        if not result.get('Degree', '').strip() or result['Degree'].strip() in ['·', '-']:
            result.pop('Degree', None)
        return result

    start_raw = match.group(1).strip()
    end_raw = match.group(2).strip().lower()
    degree = degree_part[:match.start()].strip()
    degree = re.sub(r'\s*[·\-]\s*$', '', degree)

    start_formatted = format_fecha(start_raw)
    end_formatted = "Present" if end_raw in ['present', 'presente', 'actualidad'] else format_fecha(end_raw)

    print(f"[DEBUG] Regex OK → start: '{start_raw}' → '{start_formatted}', end: '{end_raw}' → '{end_formatted}'")

    result = {
        'Institution': institution,
        'Start': start_formatted,
        'End': end_formatted
    }
    if degree:
        result['Degree'] = degree
    return result

def merge_adjacent_entries(entries: list) -> list:
    merged = []
    i = 0
    while i < len(entries):
        current = entries[i]
        if 'Start' not in current and 'End' not in current:
            if i + 1 < len(entries):
                next_entry = entries[i + 1]
                if 'Start' not in next_entry and 'End' not in next_entry:
                    degree_info = next_entry.get('Institution', '')
                    if 'Degree' in current:
                        current['Degree'] = (current['Degree'] + " " + degree_info).strip()
                    else:
                        current['Degree'] = degree_info
                    i += 2
                    merged.append(current)
                    continue
        merged.append(current)
        i += 1
    return merged

def process_education_layer2(data: dict) -> bool:
    if 'Education' not in data or not isinstance(data['Education'], str):
        return False

    if not date_pattern.search(data['Education']):
        return False

    fragments = [frag.strip() for frag in re.split(r'\n\s*\n', data['Education']) if frag.strip()]
    new_entries = []
    i = 0
    while i < len(fragments):
        if date_pattern.search(fragments[i]):
            new_entries.append(parse_entry_education(fragments[i]))
            i += 1
        elif single_year_pattern.search(fragments[i]):
            if new_entries:
                prev_degree = new_entries[-1].get('Degree', '')
                combined = (prev_degree + " " + fragments[i]).strip()
                new_entries[-1] = parse_entry_education(new_entries[-1]['Institution'] + "\n" + combined)
            else:
                new_entries.append(parse_entry_education(fragments[i]))
            i += 1
        else:
            if (i + 1) < len(fragments) and date_pattern.search(fragments[i + 1]):
                combined = fragments[i] + "\n" + fragments[i + 1]
                new_entries.append(parse_entry_education(combined))
                i += 2
            else:
                new_entries.append(parse_entry_education(fragments[i]))
                i += 1

    new_entries = merge_adjacent_entries(new_entries)

    for entry in new_entries:
        keys_to_remove = [k for k, v in entry.items() if v is None or (isinstance(v, str) and v.strip() == '')]
        for k in keys_to_remove:
            del entry[k]

    if new_entries:
        data['Education'] = new_entries
        return True
    return False

def process(data: dict, log: bool = False) -> dict:
    process_education_layer2(data)
    return data
