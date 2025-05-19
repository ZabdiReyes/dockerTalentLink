from parser import idiomas

def test_parse_languages():
    input_data = ["Inglés (Avanzado)", "Francés", {"Language": "Alemán", "Proficiency": "Básico"}]
    expected = [
        {"Language": "Inglés", "Proficiency": "Avanzado"},
        {"Language": "Francés"},
        {"Language": "Alemán", "Proficiency": "Básico"}
    ]
    result = idiomas.parse_languages(input_data)
    assert result == expected
