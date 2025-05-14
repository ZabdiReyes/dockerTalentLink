
from parser import experiencia

def test_parse_experience():
    text = "Empresa XYZ\nDesarrollador Backend\n\nEnero 2020 - Diciembre 2022 (3 años)\nCDMX\nDesarrollé APIs REST."
    result = experiencia.parse_experience(text)
    assert isinstance(result, list) and len(result) == 1
    assert "company" in result[0] and "startDate" in result[0]
