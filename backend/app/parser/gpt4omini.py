# parser/gpt4omini.py
import os
from dotenv import load_dotenv
from openai import OpenAI
import json
import re

# Cargar variables del .env
load_dotenv()

# Obtener la API Key de OpenAI desde el entorno
api_key = os.getenv("OPENAI_API_KEY")

# Inicializar el cliente
client = OpenAI(api_key=api_key)


def extract_info_from_txt(txt_path):
    try:
        with open(txt_path, "r", encoding="UTF-8") as file:
            txt_content = file.read()
    except UnicodeDecodeError:
        with open(txt_path, "r", encoding="UTF-8") as file:
            txt_content = file.read()

    prompt = f"""Extrae la información del siguiente contenido y formatea la respuesta exactamente en el siguiente formato JSON. Asegúrate de que la respuesta solo contenga ese formato, sin saludos, explicaciones ni advertencias:

Return Format:
{{
  "contact": {{
    "name": "Full Name",
    "linkedin": "LinkedIn URL",
    "website": "URL (optional)",
    "location": "City, Country",
    "company": "Current Company (optional)"
  }},
  "profile": "Brief professional profile summary (can include title and summary/excerpt)",
  "title": "Professional Title (optional)",
  "skills": [
    "Skill 1",
    "Skill 2"
  ],
  "languages": [
    {{
      "language": "Language",
      "proficiency": "Proficiency Level (optional)"
    }}
  ],
  "experience": [
    {{
      "company": "Company Name",
      "position": "Job Title or Position",
      "duration": "Period (e.g., 'January 2012 - Present')",
      "location": "Company Location (optional)"
    }}
  ],
  "education": [
    {{
      "institution": "Name of the institution or university",
      "degree": "Degree, qualification or program (as applicable)",
      "duration": "Period (e.g., '2010 - 2014')"
    }}
  ],
  "achievements": {{
    "certifications": [
      "Certification 1",
      "Certification 2"
    ],
    "awards_honors": [
      "Award or recognition 1"
    ],
    "publications": [
      "Publication Title 1"
    ]
  }},
  "others": {{
    "additional_information": "Any extra information that does not fit into the above categories"
  }}
}}

Contenido:
{txt_content}
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini-2024-07-18",
        messages=[
            {
                "role": "system",
                "content": "Eres un asistente que extrae información y devuelve únicamente el JSON solicitado, sin texto adicional."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.0
    )

    return response.choices[0].message.content
