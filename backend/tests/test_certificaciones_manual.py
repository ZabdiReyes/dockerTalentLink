import sys
import os

# Asegura acceso a app/parser
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../app")))

from parser.certificaciones import procesar_certificaciones

casos = {
    # Casos contemplados en tus reglas
    "Subcaso 1 - Conector al final": ["Certificado en", "Redes Avanzadas"],
    "Subcaso 2 - Minúscula inicial (concat)": ["Python Avanzado", "de Google cloud"],
    "Subcaso 3 - Comillas sin cerrar": ["Curso de 'Machine Learning", "por Coursera'"],
    "Subcaso 4 - Paréntesis sin cerrar": ["Certificación (AWS", "Cloud Practitioner)"],
    "Subcaso 5 - Paréntesis completo": ["Certificado en Ciberseguridad ","(2021)"],
    "Subcaso 6 - Empieza con '-'": ["Hacking Ético", "- Nivel 2"],
    "Subcaso 7 - Termina con ','": ["Certificación en Docker,", "Kubernetes Básico"],
    "Subcaso 8 - Palabras individuales": ["Microsoft", "Office"],
    "Subcaso 9 - Tu caso original": ["Certificado de", "Seguridad Informática", "Python Avanzado", "- Módulo 1"],

    # Casos adicionales reales
    "Subcaso 10 - Comillas dobles abiertas": ['Curso "Deep Learning', 'con PyTorch"'],
    "Subcaso 11 - Paréntesis cruzado con guion": ["Introducción a Redes (2020", "- Nivel básico)"],
    "Subcaso 12 - Conector en alemán": ["Zertifikat für", "Sichere Softwareentwicklung"],
    "Subcaso 13 - Finaliza con conector (español)": ["Especialización en", "inteligencia artificial"],
    "Subcaso 14 - Mezcla de signos y minúsculas": ["Cisco Certified", "- cybersecurity analyst", "(2021)"],
    "Subcaso 15 - Prefijo válido con '-'": ["- Fundamentos de Hacking Ético"],
    "Subcaso 16 - Título limpio y completo": ["Machine Learning Certificate"],
    "Subcaso 17 - Línea vacía intermedia": ["Certificación Microsoft", "", "Azure Fundamentals"],
    "Subcaso 18 - Frases truncadas comunes": ["Certificación en", "Cloud", "-", "Nivel Básico"],
    "Subcaso 19 - Elementos duplicados": ["AWS", "AWS", "Developer", "Developer"],
    "Subcaso 20 - Palabra aislada con comillas": ["'Docker'"]
}

for descripcion, input_data in casos.items():
    print("="*80)
    print(f"{descripcion}")
    print("ANTES:")
    for item in input_data:
        print(f"  - {item}")

    # Limpiar vacíos y procesar
    limpio = [line for line in input_data if line.strip()]
    resultado = procesar_certificaciones(limpio)

    print("DESPUÉS:")
    for r in resultado:
        print(f"  - {r}")
