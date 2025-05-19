import sys
import os

# Asegura acceso a app/parser
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../app")))

from parser.educacion import process

entrada = """
University of New Mexico School of Engineering

Posdoctorado en sistemas complejos · (2015 - 2016)

Centro de Investigación y de Estudios Avanzados del IPN

Doctorado en Ciencias en la Especialidad en Ingeniería Eléctrica, Diagnóstico
de Fallas en Sistemas · (2004 - 2007)

Centro de Investigación y de Estudios Avanzados del IPN

Maestria en Ciencias en la especialidad de Ciencias
Computacionales, Diagnóstico de Fallas · (2002 - 2004)

Universidad Autónoma de Sinaloa

Licencitura en Informática, Inteligencia artificial · (agosto de 1997 - diciembre
de 2002)
"""

print("=" * 80)
print("Test de Educación complejo con varias entradas y líneas partidas\nANTES:")
print(entrada)

data = {"Education": entrada}
resultado = process(data)

print("\nDESPUÉS:")
for item in resultado["Education"]:
    print(item)
print("=" * 80)
