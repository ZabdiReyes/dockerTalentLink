import re

STOPWORDS = {
    # Español
    "el", "la", "los", "las", "un", "una", "unos", "unas", "de", "del", "al", "a", "y", "o", "pero",
    "porque", "con", "sin", "para", "por", "que", "como", "en", "es", "su", "sus", "mi", "mis", "tu", "tus",
    "yo", "tú", "él", "ella", "nosotros", "nosotras", "ustedes", "ellos", "ellas", "lo", "le", "les", "me", "te",
    "se", "ya", "muy", "sí", "no", "ni", "donde", "cuando", "mientras", "aunque",

    # Inglés
    "the", "a", "an", "and", "or", "but", "because", "with", "without", "for", "by", "of", "to", "in", "on",
    "at", "as", "is", "are", "was", "were", "be", "been", "being", "he", "she", "it", "they", "them", "his",
    "her", "its", "we", "you", "i", "my", "me", "your", "yours", "their", "our", "ours", "this", "that", "these",
    "those", "what", "which", "who", "whom", "where", "when", "why", "how", "if", "then", "than", "so", "too", "very"
    }

def limpiar_texto(texto):
    texto = str(texto).lower()
    texto = re.sub(r"\d+", "", texto)
    texto = re.sub(r"[^\w\s]", "", texto)
    texto = re.sub(r"\s+", " ", texto)
    palabras = texto.strip().split()
    palabras_filtradas = [p for p in palabras if p not in STOPWORDS]
    return " ".join(palabras_filtradas)
