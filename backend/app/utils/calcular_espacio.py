import os

def calcular_pesos_archivos(directorio):
    """
    Recorre todos los archivos de un directorio y devuelve una lista con sus tamaños y la suma total.

    Args:
        directorio (str): Ruta del directorio a analizar.

    Returns:
        archivos_info (list): Lista de tuplas (ruta_relativa, tamaño_en_bytes).
        total_bytes (int): Suma total de los tamaños de los archivos.
    """
    archivos_info = []
    total_bytes = 0

    for root, _, files in os.walk(directorio):
        for filename in files:
            ruta_absoluta = os.path.join(root, filename)
            try:
                peso = os.path.getsize(ruta_absoluta)
                ruta_relativa = os.path.relpath(ruta_absoluta, directorio)
                archivos_info.append((ruta_relativa, peso))
                total_bytes += peso
            except FileNotFoundError:
                continue  # por si algún archivo fue eliminado mientras se recorría

    return archivos_info, total_bytes

def bytes_a_megabytes(bytes_val):
    return bytes_val / (1024 * 1024)

def imprimir_reporte_espacio(directorio):
    archivos, total = calcular_pesos_archivos(directorio)
    print(f"📂 Archivos en: {directorio}")
    for ruta, peso in archivos:
        print(f" - {ruta}: {peso} bytes ({bytes_a_megabytes(peso):.2f} MB)")
    print(f"\n📊 Total: {total} bytes ({bytes_a_megabytes(total):.2f} MB)")
