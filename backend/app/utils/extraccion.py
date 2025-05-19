import re
import json
from unicodedata import normalize

def normalize_text(text):
    """Corrige problemas de encoding y normaliza el texto"""
    return normalize('NFKD', text).encode('ASCII', 'ignore').decode('ASCII')

def extract_data(text):
    text = normalize_text(text)  # Normalizar texto
    
    data = {
        "contact": {
            "name": None,
            "linkedin": None,
            "website": None,
            "location": None,
            "company": None
        },
        "profile": None,
        "title": None,
        "skills": [],
        "languages": [],
        "experience": [],
        "education": [],
        "achievements": {
            "certifications": [],
            "awards_honors": [],
            "publications": []
        },
        "others": {"additional_information": None}
    }

    # Extraer nombre (primera línea no vacía)
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    if lines:
        data['contact']['name'] = lines[0]

    # LinkedIn (patrón mejorado)
    linkedin_pattern = r'(linkedin\.com/in/[\w-]+)'
    if matches := re.search(linkedin_pattern, text, re.IGNORECASE):
        data['contact']['linkedin'] = f"https://www.{matches.group(1)}"

    # Ubicación (patrón mejorado)
    if location_match := re.search(r'(\b[A-Z][a-z]+(?: [A-Z][a-z]+)*, [A-Z]{2}, [A-Za-z]+\b)', text):
        data['contact']['location'] = location_match.group(1)

    # Experiencia (patrón mejorado)
    experience_section = re.split(r'Experiencia\n', text, flags=re.IGNORECASE)[-1]
    experience_entries = re.split(r'\n\s*\n', experience_section)
    
    for entry in experience_entries:
        if match := re.match(r'(.*?)\n(.*?)\n(.*?) \((\d+ meses|\d+ años? \d+ meses)\)', entry):
            data['experience'].append({
                "position": match.group(1).strip(),
                "company": match.group(2).strip(),
                "location": match.group(3).strip(),
                "duration": match.group(4).strip()
            })

    # Educación (patrón mejorado)
    if education_section := re.search(r'Educación\n(.*?)\nContactar', text, re.DOTALL | re.IGNORECASE):
        education_entries = re.findall(
            r'(.*?)\n(.*?)\n(.*?) \((\d{4} - \d{4}|Present)\)',
            education_section.group(1)
        )
        for entry in education_entries:
            data['education'].append({
                "institution": entry[0].strip(),
                "degree": entry[1].strip(),
                "field": entry[2].strip(),
                "duration": entry[3].strip()
            })

    # Habilidades (patrón mejorado)
    if skills_section := re.search(r'Aptitudes principales\n(.*?)Languages', text, re.DOTALL):
        data['skills'] = [s.strip() for s in skills_section.group(1).split('\n') if s.strip()]

    # Idiomas (patrón mejorado)
    if languages_section := re.search(r'Languages\n(.*?)Certifications', text, re.DOTALL):
        languages = re.findall(r'(\w+) \((.*?)\)', languages_section.group(1))
        data['languages'] = [{"language": lang[0], "proficiency": lang[1]} for lang in languages]

    # Certificaciones (patrón mejorado)
    if cert_section := re.search(r'Certifications\n(.*?)\n\n', text, re.DOTALL):
        data['achievements']['certifications'] = [
            c.strip() for c in cert_section.group(1).split('\n') if c.strip()
        ]

    return data

def convert_txt_to_json(input_file, output_file):
    try:
        with open(input_file, 'r', encoding='UTF-8') as f:
            text = f.read()

        data = extract_data(text)

        with open(output_file, 'w', encoding='UTF-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

        print(f"Conversión exitosa: {input_file} -> {output_file}")

    except Exception as e:
        print(f"Error procesando {input_file}: {str(e)}")
        