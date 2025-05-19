import sys
import os

# Asegura acceso a app/parser
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../app")))

from parser.educacion import process

casos = {
    "Subcaso 1 - Fecha clásica (años)": "UNAM\nIngeniería en Sistemas (2015 - 2019)",
    "Subcaso 2 - Con mes en español": "IPN\nLicenciatura en Informática (agosto de 2014 - julio de 2018)",
    "Subcaso 3 - Con mes en inglés": "Harvard\nData Science Program (June 2017 - May 2019)",
    "Subcaso 4 - Fecha con 'Presente'": "MIT\nAI Research (2020 - present)",
    "Subcaso 5 - Solo un año entre paréntesis": "Tecnológico de Monterrey\nDiplomado en Big Data\n(2019)",
    "Subcaso 6 - Dos entradas sin fecha (se fusionan)": "Coursera\nDeep Learning\n\nGoogle\nCloud Architecture",
    "Subcaso 7 - Fragmento suelto con fecha después": "UNAM\nTaller de Ciberseguridad\n\n(2020 - 2021)",
    "Subcaso 8 - Sin fechas (debe quedarse)": "Certificación Académica\nFundamentos de Programación",
    "Subcaso 9 - Campo vacío": "",
    "Subcaso 10 - Fragmento con punto final y salto": "UABC\nCurso de Redes.\n\n(2022 - Actualidad)",
    "Subcaso 11 - Grado con carácter final raro": "UPV\nBlockchain · (2018 - 2020)",
    "Subcaso 12 - Fragmento con año suelto entre medio": "ITESM\nCertificado en AI\n(2020)\nTaller de robótica",
    "Subcaso 13 - Mes en francés": "Université Paris-Saclay\nLicence Informatique (Septembre de 2016 - Juin de 2019)",
    "Subcaso 14 - Mes en alemán": "Technische Universität München\nMaster Maschinenbau (März 2015 - Dezember 2018)",
    "Subcaso 15 - Inglés/francés combinado": "École Polytechnique\nAI Program (janvier 2020 - July 2022)"
}

for descripcion, entrada in casos.items():
    print("=" * 80)
    print(descripcion)
    print("ANTES:")
    print(entrada)

    data = {"Education": entrada}
    resultado = process(data)

    print("DESPUÉS:")
    edu = resultado.get("Education", [])
    if isinstance(edu, list):
        for entry in edu:
            print(entry)
    else:
        print(edu)
