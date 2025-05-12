import os
import json
from rank_bm25 import BM25Okapi
from nltk.tokenize import word_tokenize
import nltk

# Descargar recursos necesarios de NLTK si no están
nltk.download('punkt', quiet=True)

class BM25SearchEngine:
    def __init__(self, directory_path, sections=None, section_key=None):
        if section_key and not sections:
            sections = [section_key]
        self.directory_path = directory_path
        self.sections = sections if sections else ["profile"]
        self.documents = []
        self.file_paths = []
        self.tokenized_docs = []
        self.raw_jsons = []
        self.bm25 = None
        self.index()

    def extract_text(self, value):
        if isinstance(value, str):
            return value.strip()
        elif isinstance(value, list):
            return ' '.join(filter(None, (self.extract_text(item) for item in value)))
        elif isinstance(value, dict):
            return ' '.join(filter(None, (self.extract_text(v) for v in value.values())))
        return ''

    def extract_relevant_text(self, json_obj):
        combined = ""
        for section in self.sections:
            value = json_obj.get(section)
            if section == "certifications":
                value = json_obj.get("achievements", {}).get("certifications", [])
            elif section == "awards":
                value = json_obj.get("achievements", {}).get("awards_honors", [])
            if value:
                combined += self.extract_text(value) + " "
        return combined.strip()

    def index(self):
        for fname in os.listdir(self.directory_path):
            if fname.endswith('.json'):
                path = os.path.join(self.directory_path, fname)
                with open(path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    text = self.extract_relevant_text(data)
                    if text:
                        self.documents.append(text)
                        self.file_paths.append(path)
                        self.raw_jsons.append(data)
        self.tokenized_docs = [word_tokenize(doc.lower()) for doc in self.documents]
        self.bm25 = BM25Okapi(self.tokenized_docs)

    def search(self, query, top_n=5):
        if not query.strip():
            raise ValueError("La consulta no puede estar vacía.")

        tokenized_query = word_tokenize(query.lower())
        scores = self.bm25.get_scores(tokenized_query)
        effective_n = len(scores) if top_n <= 0 else min(top_n, len(scores))
        top_idxs = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:effective_n]

        json_results = []
        score_results = []

        for i in top_idxs:
            data = self.raw_jsons[i]
            data["_filename"] = os.path.basename(self.file_paths[i])
            json_results.append(data)
            score_results.append(float(scores[i]))

        return json_results, score_results
