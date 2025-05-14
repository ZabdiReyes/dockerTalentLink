
import re

def parse_languages(language_list):
    languages = []
    for lang in language_list:
        if isinstance(lang, dict):
            languages.append(lang)
        elif isinstance(lang, str):
            match = re.match(r"(.+?)\s*\(([^)]+)\)", lang)
            if match:
                language, proficiency = match.groups()
                languages.append({"Language": language.strip(), "Proficiency": proficiency.strip()})
            else:
                languages.append({"Language": lang.strip()})
    return languages

def process(data):
    if "Languages" in data and isinstance(data["Languages"], list):
        if not all(isinstance(x, dict) for x in data["Languages"]):
            data["Languages"] = parse_languages(data["Languages"])
    return data
