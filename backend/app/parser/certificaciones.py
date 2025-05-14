import json
import os

def procesar_certificaciones(certificaciones, log=False):
    conectores_universales = {
        '-', ',', '·',
        # Español
        'de', 'en', 'para', 'y', 'a', 'con', 'por', 'sin', 'sobre', 'hacia',
        'entre', 'hasta', 'según', 'mediante', 'durante', 'bajo', 'contra', 'desde',
        'o', 'ni', 'pero', 'aunque', 'porque', 'como', 'si', 'cuando', 'mientras',
        'donde', 'aun', 'sino', 'mas', 'salvo', 'excepto', 'versus',
        # English
        'for', 'to', 'of', 'with', 'by', 'at', 'from', 'into', 'during', 'about',
        'through', 'over', 'under', 'against', 'across', 'among', 'and', 'or',
        'nor', 'but', 'although', 'as', 'if', 'when', 'while', 'where', 'since',
        'until', 'per', 'via', 'plus', 'minus', 'upon', 'amidst',
        # Français
        'à', 'dans', 'chez', 'vers', 'et', 'ou', 'mais', 'car', 'lorsque',
        'quoique', 'depuis', 'jusqu', 'malgré',
        # Italiano
        'di', 'da', 'su', 'tra', 'fra', 'sotto', 'verso', 'senza', 'però',
        'perché', 'mentre', 'dove', 'nonostante', 'fino', 'presso', 'oltre',
        # Deutsch
        'von', 'zu', 'für', 'mit', 'bei', 'nach', 'durch', 'über', 'unter',
        'zwischen', 'während', 'um', 'an', 'auf', 'denn', 'weil',
        'obwohl', 'als', 'bis', 'seit', 'aus', 'ohne', 'entlang', 'trotz',
        'jenseits', 'anstatt', 'innerhalb'
    }

    procesadas = []
    i = 0
    n = len(certificaciones)

    while i < n:
        actual = certificaciones[i].strip()
        if not actual:
            i += 1
            continue

        if procesadas and actual and actual[0].islower():
            if procesadas[-1][-1].isspace():
                procesadas[-1] += actual.lstrip()
            else:
                procesadas[-1] += " " + actual
            i += 1
            continue

        opener, closer = None, None
        if '(' in actual and ')' not in actual:
            opener, closer = '(', ')'
        elif "'" in actual and actual.count("'") % 2 != 0:
            opener, closer = "'", "'"

        if opener:
            temp = [actual]
            i += 1
            while i < n:
                current_item = certificaciones[i].strip()
                temp.append(current_item)
                if closer in current_item or i == n - 1:
                    i += 1
                    break
                i += 1
            procesadas.append(' '.join(temp))
            continue

        if actual.startswith('(') and actual.endswith(')'):
            if procesadas:
                procesadas[-1] += ' ' + actual
            else:
                procesadas.append(actual)
            i += 1
            continue

        palabras = actual.split()
        if palabras and palabras[-1].lower() in conectores_universales:
            if i + 1 < n:
                procesadas.append(f"{actual} {certificaciones[i+1].strip()}")
                i += 2
            else:
                procesadas.append(actual)
                i += 1
            continue

        if palabras and palabras[0].lower() in conectores_universales:
            if procesadas:
                procesadas[-1] += f" {actual}"
            else:
                procesadas.append(actual)
            i += 1
            continue

        if len(palabras) == 1:
            if procesadas:
                procesadas[-1] += f" {actual}"
            else:
                procesadas.append(actual)
            i += 1
            continue

        if actual.startswith((',', '-')):
            if procesadas:
                procesadas[-1] += actual
            else:
                procesadas.append(actual)
            i += 1
            continue

        if actual.endswith((',', '-')):
            if i + 1 < n:
                procesadas.append(actual + certificaciones[i+1].strip())
                i += 2
            else:
                procesadas.append(actual)
                i += 1
            continue

        procesadas.append(actual)
        i += 1

    return procesadas


def process(data, log=False):
    if "Certifications" in data and isinstance(data["Certifications"], list):
        data["Certifications"] = procesar_certificaciones(data["Certifications"], log=log)
    return data
