import subprocess
import os
from typing import Optional
import re
import json
import logging
import statistics

# Global dictionary to track function calls
function_calls = {}

# Variable global que es una lista de nombres
lista_nombres_caso_extension = [] #Todos los nombres de aquellos archivos cuya entension = True
actual_nombre_extension = ""
actual_estado_extension = False
actual_txt_partes = []
actual_txt_partes_dics = {}


def guardar_txt(txt_content, nombre_archivo, directorio_destino):
    """
    Guarda el contenido de texto en un archivo TXT.

    Args:
        txt_content (str): El contenido del texto a guardar.
        nombre_archivo (str): El nombre del archivo (sin extensión .txt).
        directorio_destino (str): El directorio donde guardar el archivo.

    Returns:
        bool: True si la operación fue exitosa, False si hubo un error.
    """
    try:
        ruta_completa = os.path.join(directorio_destino, f"{nombre_archivo}.txt")
        with open(ruta_completa, "w", encoding="Latin-1") as f:
            f.write(txt_content)
        return True
    except Exception as e:
        print(f"Error al guardar el archivo TXT: {e}")
        return False


def txt_a_json(txt_content):
    """
    Analiza el texto procesado y lo convierte a formato JSON.
    (Aquí va tu lógica de extracción de información y creación del JSON)

    Args:
        txt_content (str): El texto procesado del CV.

    Returns:
        str: Una cadena JSON que representa la información extraída del CV.
             Retorna None en caso de error.
    """
    try:
        # **REEMPLAZA ESTO CON TU LÓGICA REAL DE EXTRACCIÓN**
        # Este es solo un ejemplo para ilustrar la estructura
        data = {"texto_cv": txt_content}  # Un ejemplo muy básico
        return json.dumps(data, indent=4, ensure_ascii=False)  # JSON legible
    except Exception as e:
        print(f"Error al convertir TXT a JSON: {e}")
        return None


def guardar_json(json_content, nombre_archivo, directorio_destino):
    """
    Guarda el contenido JSON en un archivo .json.

    Args:
        json_content (str): El contenido JSON a guardar.
        nombre_archivo (str): El nombre del archivo (sin extensión .json).
        directorio_destino (str): El directorio donde guardar el archivo.

    Returns:
        bool: True si la operación fue exitosa, False si hubo un error.
    """
    try:
        ruta_completa = os.path.join(directorio_destino, f"{nombre_archivo}.json")
        with open(ruta_completa, "w", encoding="Latin.1") as f:
            f.write(json_content)
        return True
    except Exception as e:
        print(f"Error al guardar el archivo JSON: {e}")
        return False


# ----------------------------------------------------------------------
#  EJEMPLO DE USO
# ----------------------------------------------------------------------
def procesar_pdfs(lista_pdf_paths, directorio_origen, directorio_destino, procesar_todo=True, n=0, m=None , dividir = True, log=False):
    """
    Procesa una lista de archivos PDF.
    
    Parámetros:
      - lista_pdf_paths: Lista de rutas de los archivos PDF.
      - directorio_origen: Directorio origen de los archivos PDF.
      - directorio_destino: Directorio donde se guardarán los archivos TXT.
      - procesar_todo: Si es True, se procesan todos los archivos (o en el rango de índices indicado).
        Si es False, se procesa solo el primer archivo de la lista.
      - n: Índice de inicio del rango.
      - m: Índice final (no inclusivo) del rango. Si es None o mayor que la cantidad de archivos,
           se procesa hasta el final de la lista.
      - log: Si es True, se imprimen mensajes de log.
    """
    if not lista_pdf_paths:
        if log:
            print("No hay archivos para procesar.")
        return

    if not procesar_todo:
        # Ajustar m si es None o excede el tamaño de la lista
        if m is None or m > len(lista_pdf_paths):
            m = len(lista_pdf_paths)
        
        # Asegurarse de que n sea válido
        if n < 0:
            n = 0
        if n >= len(lista_pdf_paths):
            if log:
                print("El índice de inicio 'n' es mayor o igual que la cantidad de archivos.")
            return

        # Seleccionar el rango de archivos a procesar (de n a m, sin incluir m)
        archivos_a_procesar = lista_pdf_paths[n:m]
    else:
        archivos_a_procesar = lista_pdf_paths

    # Procesar cada archivo en el rango seleccionado, con índice de 0 a len(archivos_a_procesar)-1
    for indice, archivo_pdf in enumerate(archivos_a_procesar):
        procesar_archivo(archivo_pdf, directorio_origen, directorio_destino, indice, dividir, log)


def procesar_archivo(archivo_pdf, directorio_origen, directorio_destino, indice=0, dividir=True, log=False):
    """
    Procesa un único archivo PDF:
    - Convierte el PDF a TXT.
    - Procesa el contenido del archivo TXT.
    - Renombra el archivo TXT y lo divide si es necesario.
    """
    if log:
        print(f"Archivo a procesar: {archivo_pdf} índice {indice}")
    txt_file = archivo_pdf.replace(".pdf", ".txt")
    if log:
        print(txt_file)

    # Convertir PDF a TXT
    convert_pdf_to_txt(directorio_origen, archivo_pdf, directorio_destino, log)
    archivo_txt_raw = os.path.join(directorio_destino, txt_file)
    if log:
        print(f"Archivo TXT guardado en: {archivo_txt_raw}")

    # Procesar el archivo TXT
    dic_sin_procesar = file_to_dic(archivo_txt_raw,log)
    if dic_sin_procesar is None:
        if log:
            print("Error al procesar el archivo TXT:", archivo_txt_raw)
        return
    margen = calculate_margin(dic_sin_procesar)
    if log:
        print(f"Margen: {margen}")

    nombre = obtener_nombre(dic_sin_procesar, margen)
    nuevo_nombre_txt = os.path.join(directorio_destino, f"{nombre}.txt")

    # Si ya existe, eliminar y renombrar el archivo TXT
    if os.path.exists(nuevo_nombre_txt):
        os.remove(nuevo_nombre_txt)
    os.rename(archivo_txt_raw, nuevo_nombre_txt)
    if log:
        print(f"Archivo TXT renombrado a: {nuevo_nombre_txt}")

    # Leer contenido del TXT y obtener información adicional
    txt_content = read_file_content(nuevo_nombre_txt)
    n_pages = get_pages(nuevo_nombre_txt)
    if log:
        print(f"El archivo {nuevo_nombre_txt} tiene {n_pages} páginas")

    if dividir:
        # Dividir el archivo TXT en varios archivos según form feed
        archivos_divididos = dividir_txt_por_form_feed(txt_content, directorio_destino, nombre)
        actual_txt_partes = archivos_divididos
        if log:
            print(f"Archivos divididos: {archivos_divididos}")
            print(f"{nombre}_parte2.txt")
            print(f"El archivo {nombre} se dividió en {n_pages} partes")
        
        if os.path.exists(os.path.join(directorio_destino, f"{nombre}_parte_2.txt")):
            if log:
                
                print(f"{nombre}_parte_2.txt existe")
                
            
            extension_parte2 = verificar_extension(directorio_destino, f"{nombre}_parte_2.txt", margen)
            if extension_parte2:
                lista_nombres_caso_extension.append(nombre)
                actual_nombre_extension = nombre
                actual_estado_extension = True
            if log:
                print(f"Extensión archivo parte2: {extension_parte2}")
            
        else:
            if log:
                
                print(f"{nombre}_parte_2.txt no existe")
                
            actual_nombre_extension = []
            actual_estado_extension = False
            extension_parte2 = False
         
        ii = 0
           
        if extension_parte2:
            if log:
                print(f"El archivo {nombre} tiene extensión")
            for archivo in archivos_divididos:
                ii = ii + 1  
                if log:
                    print(f"Archivo {ii}: {archivo}")
                if (ii==1):
                    txt1_col1, txt1_col2 = dividir_txt_por_columnas(archivo, margen)
                    
                    # Buscar el patrón "Page 1 of" en txt1_col2
                    for i, elem in enumerate(txt1_col2):
                        if "Page 1 of" in elem:
                            indice_patron = i
                            if indice_patron > 0 and txt1_col2[indice_patron - 1].strip() == "":
                                # Borrar desde indice_patron-1 hasta el final de txt1_col2
                                txt1_col2 = txt1_col2[:indice_patron - 1]
                                break
                    acum_col1 =  txt1_col1
                    acum_col2 =  txt1_col2 
                    
                if (ii==2):
                    txt2_col1, txt2_col2 = dividir_txt_por_columnas(archivo, margen-1)
                    
                    for i, elem in enumerate(txt2_col2):
                        if "Page 2 of" in elem:
                            indice_patron = i
                            if indice_patron > 0 and txt2_col2[indice_patron - 1].strip() == "":
                                # Borrar desde indice_patron-1 hasta el final de txt1_col2
                                txt2_col2 = txt2_col2[:indice_patron - 1]
                                break
                    acum_col1 += txt2_col1
                    acum_col2 += txt2_col2 
                            
                if (ii>2):
                    txt_content = read_file_content(archivo).splitlines()
                    txt_col2 = txt_content
                    txt_col1 = []
                    for i, elem in enumerate(txt_col2):
                        if f"Page {ii} of" in elem:
                            indice_patron = i
                            if indice_patron > 0 and txt_col2[indice_patron - 1].strip() == "":
                                # Borrar desde indice_patron-1 hasta el final de txt_col2
                                txt_col2 = txt_col2[:indice_patron - 1]
                                break
                    acum_col1 += txt_col1
                    acum_col2 += txt_col2
                    
                archivo_final_txt = acum_col2 + [" "] + [" "] + [" "] + acum_col1
                    # Guardar el archivo final en un TXT en el directorio TxT_Procesado
                directorio_procesado = "Data/TxT_Procesado"
                if not os.path.exists(directorio_procesado):
                    os.makedirs(directorio_procesado)
                
                nombre_archivo_final = f"{nombre}_final"
                guardar_txt("\n".join(archivo_final_txt), nombre_archivo_final, directorio_procesado)              
                
            
        else:
            if log:
                print(f"El archivo {nombre} no tiene extensión")
                ## Procesar el archivo final de manera normal
                
                for archivo in archivos_divididos:
                    ii = ii + 1  
                    if log:
                        print(f"Archivo {ii}: {archivo}")
                    if (ii==1):
                        txt1_col1, txt1_col2 = dividir_txt_por_columnas(archivo, margen)
                        
                        # Buscar el patrón "Page 1 of" en txt1_col2
                        for i, elem in enumerate(txt1_col2):
                            if "Page 1 of" in elem:
                                indice_patron = i
                                if indice_patron > 0 and txt1_col2[indice_patron - 1].strip() == "":
                                    # Borrar desde indice_patron-1 hasta el final de txt1_col2
                                    txt1_col2 = txt1_col2[:indice_patron - 1]
                                    break
                        acum_col1 =  txt1_col1
                        acum_col2 =  txt1_col2 
                                
                    if (ii>1):
                        txt_content = read_file_content(archivo).splitlines()
                        txt_col2 = txt_content
                        txt_col1 = []
                        for i, elem in enumerate(txt_col2):
                            if f"Page {ii} of" in elem:
                                indice_patron = i
                                if indice_patron > 0 and txt_col2[indice_patron - 1].strip() == "":
                                    # Borrar desde indice_patron-1 hasta el final de txt_col2
                                    txt_col2 = txt_col2[:indice_patron - 1]
                                    break
                        acum_col1 += txt_col1
                        acum_col2 += txt_col2
                        
                    archivo_final_txt = acum_col2 + [" "] + [" "] + [" "] + acum_col1
                        # Guardar el archivo final en un TXT en el directorio TxT_Procesado
                    directorio_procesado = "Data/TxT_Procesado"
                    if not os.path.exists(directorio_procesado):
                        os.makedirs(directorio_procesado)
                    
                    nombre_archivo_final = f"{nombre}_final"
                    guardar_txt("\n".join(archivo_final_txt), nombre_archivo_final, directorio_procesado)
                
                
    

def print_function_name_once(func_name: str, args: dict):
    if func_name not in function_calls:
        print("_" * 40)
        print(f"{func_name}({args})")
        function_calls[func_name] = True

def convert_pdf_to_txt(source_directory: str, pdf_filename: str, destination_directory: str, log: bool = False) -> Optional[str]:
    print_function_name_once("convert_pdf_to_txt", locals())
    # Validate the directories.
    if not os.path.isdir(source_directory):
        raise FileNotFoundError(f"Source directory not found: {source_directory}")
    if not os.path.isdir(destination_directory):
        os.makedirs(destination_directory, exist_ok=True) #Create destination if it does not exist

    source_path = os.path.join(source_directory, pdf_filename)

    if not os.path.exists(source_path):
        if log:
            print(f"Source file not found: {source_path}")
        return None

    txt_filename = os.path.splitext(pdf_filename)[0] + ".txt"  # Same name, .txt extension
    destination_path = os.path.join(destination_directory, txt_filename)

    command = [
        "pdftotext",
        "-layout",

        source_path,
        destination_path,
    ]

    try:
        # Run the pdftotext command
        process = subprocess.run(command, capture_output=True, text=True, check=True) #check=True raises exception on error
        #Log standard error messages to console
        if process.stderr and log:
            print(f"pdftotext stderr: {process.stderr}")
        return destination_path  # Return the path to the created TXT file

    except FileNotFoundError:
        raise OSError("pdftotext is not installed or is not in the system's PATH.")
    except subprocess.CalledProcessError as e:
        if log:
            print(f"Error converting PDF to TXT: {e}")
            print(f"pdftotext output: {e.stderr}")  # Print the error message from pdftotext
        return None  # Conversion failed
    except Exception as e:
        if log:
            print(f"An unexpected error occurred: {e}")
        return None

def calculate_margin(text_dictionary: dict[int, str]) -> int:
    print("_" * 40)
    print("calculate_margin (usando múltiples líneas con separaciones visibles)")
    
    margenes_detectados = []

    for line in text_dictionary.values():
        # Busca una línea con un bloque de espacios (al menos 4 espacios)
        match = re.search(r'^(.+?)(\s{4,})(.+)', line)
        if match:
            margen = len(match.group(1)) + len(match.group(2))
            margenes_detectados.append(margen)

    if not margenes_detectados:
        print("❌ No se detectaron márgenes claros. Usando 0 por defecto.")
        return 0

    # Calcula la mediana para mayor robustez
    margen_final = int(statistics.median(margenes_detectados))
    print(f"✅ Márgenes detectados: {margenes_detectados}")
    print(f"📐 Margen estimado (mediana): {margen_final}")
    return margen_final

def find_keyword_in_dictionary(text_dictionary: dict[int, str], keyword: str) -> list[int]:
    print_function_name_once("find_keyword_in_dictionary", locals())
    result = []
    for key, value in text_dictionary.items():
        if isinstance(value, str) and keyword in value:  # Ensure value is a string before checking
            result.append(key)  # Append the key (line number)

    return result

def file_to_dic(full_file_path, log: bool = False) -> dict[int, str] | None:
    print_function_name_once("file_to_dic", locals())
    try:
        with open(full_file_path, 'r', newline="", encoding='Latin-1') as file:
            content = file.read()
            lines = re.split(r'\r\n|\r|\n', content)  # Split lines by \n, \r, or \r\n
            # Build the dictionary
            full_dictionary = {i: line for i, line in enumerate(lines, start=1)}
            return full_dictionary  # Return the dictionary

    except FileNotFoundError:
        if log:
            print(f"The file {full_file_path} does not exist.")
        return None  # Indicate failure
    except Exception as e:
        if log:
            print(f"An error occurred: {e} in read_file_content()")
        return None  # Indicate failure
    
def dividir_txt_por_form_feed(txt_content, directorio_destino, nombre_base, log: bool = False):
    print("_"*40)
    print("dividir_txt_por_form_feed")
    secciones = txt_content.split('\f')
    archivos_generados = []

    for i, seccion in enumerate(secciones):
        nombre_archivo = f"{nombre_base}_parte_{i+1}.txt"
        ruta_archivo = os.path.join(directorio_destino, nombre_archivo)
        with open(ruta_archivo, "w", encoding="utf-8") as f:
            f.write(seccion)
        archivos_generados.append(ruta_archivo)
        
    if len(archivos_generados)>1:
        archivo_a_eliminar = archivos_generados.pop()
        if os.path.exists(archivo_a_eliminar):
            os.remove(archivo_a_eliminar)
    
    return archivos_generados

def read_file_content(file_path: str, log: bool = False) -> Optional[str]:
    print_function_name_once("read_file_content", locals())
    try:
        with open(file_path, 'r', encoding='Latin-1') as file:
            return file.read()
    except FileNotFoundError:
        if log:
            print(f"The file {file_path} does not exist.")
        return None
    except Exception as e:
        if log:
            print(f"An error occurred: {e}")
        return None

def get_pages(file_path: str, log: bool = False) -> Optional[int]:
    print_function_name_once("get_pages", locals())
    content = read_file_content(file_path, log)
    if content is None:
        return None

    match = re.search(r'Page 1 of (\d+)', content)
    if match:
        return int(match.group(1))
    else:
        if log:
            print("Pattern 'Page 1 of {n}' not found in the file.")
        return None
    
def obtener_nombre(dic_sin_procesar, margen, log: bool = False):
    print("_"*40)
    print("obtener_nombre")
    iterador_lineas = iter(dic_sin_procesar.items())
    primera_linea = next(iterador_lineas)
    nombre = str(primera_linea[1])[margen:]
    
    segunda_linea = next(iterador_lineas)
    
    if not re.match(r'^\s*$', str(segunda_linea[1])):
        nombre = nombre + " " + str(segunda_linea[1][margen:])
    
    return nombre

def limpiar_final(dic_sin_procesar, log: bool = False):
    print("_"*40)
    print("limpiar_final")
    dic_procesado = {}
    last_key = max(dic_sin_procesar.keys(), default=None)
    
    if last_key is not None:
        last_line = dic_sin_procesar[last_key]
        if re.search(r'Page \d+ of \d+', last_line):
            dic_sin_procesar.pop(last_key)
    dic_procesado = dic_sin_procesar
    return dic_procesado

def dividir_txt_por_columnas(file_path: str, margen: int, log: bool = False) -> tuple[list[str], list[str]]:
    print("_"*40)
    print("dividir_txt_por_columnas")
    
    try:
        with open(file_path, 'r', encoding='latin-1') as file:
            txt_content = file.read()
    except FileNotFoundError:
        if log:
            print(f"The file {file_path} does not exist.")
        return [], []
    except Exception as e:
        if log:
            print(f"An error occurred: {e}")
        return [], []

    parte1 = []
    parte2 = []

    for line in txt_content.splitlines():
        parte1.append(line[:margen])
        parte2.append(line[margen:])

    return parte1, parte2

def verificar_extension(directorio_destino, nombre, margen, log: bool = False):
    print_function_name_once("verificar_extension", locals())
    extension = False
    archivo_parte_2 = os.path.join(directorio_destino, nombre)
    if log:
        print(archivo_parte_2, "verificar_extension")
    lineas_en_blanco = []
    if os.path.exists(archivo_parte_2):
        with open(archivo_parte_2, "r", encoding="Latin-1") as f:
            lineas = f.readlines()
            for linea in lineas[-5:]:
                lineas_en_blanco.append(linea[:margen-1])
                #print(linea[:margen-1])
            if all(re.match(r'^\s*$', linea) for linea in lineas_en_blanco):
                extension = True
                
    return extension
    
def borrar_txts(txt_directory: str, log: bool = False) -> None:
    print_function_name_once("borrar_txts", locals())
    for filename in os.listdir(txt_directory):
        if filename.endswith(".txt"):
            os.remove(os.path.join(txt_directory, filename))
            if log:
                print(f"Deleted file: {filename}")

def borrar_json(json_directory: str, log: bool = False) -> None:
    print_function_name_once("borrar_json", locals())
    for filename in os.listdir(json_directory):
        if filename.endswith(".json"):
            os.remove(os.path.join(json_directory, filename))
            if log:
                print(f"Deleted file: {filename}")


def print_education_from_json(directory):
  """Prints the 'Education' field from JSON files in the specified directory.

  Args:
    directory: The path to the directory containing the JSON files.
  """
  for filename in os.listdir(directory):
    if filename.endswith(".json"):
      filepath = os.path.join(directory, filename)
      try:
        with open(filepath, 'r', encoding='Latin-1') as f:
          try:
            data = json.load(f)
            if "Education" in data:
              print(data["Education"])
              print("-"*50)
              print("-"*50)
          except json.JSONDecodeError:
            print(f"Error decoding JSON in file: {filename}")
      except Exception as e:
        print(f"Error reading file {filename}: {e}")

def save_json(name, data, output_dir="/content/residencias/Data/Json/Custom"):
    """Guarda el JSON en la carpeta especificada con el nombre de la persona."""

    if not name:
        logging.error("Error: No se encontró un nombre válido. No se guardará el archivo.")
        return

    # Asegurar que el directorio existe
    os.makedirs(output_dir, exist_ok=True)

    # Limpiar el nombre del archivo (evitar caracteres problemáticos)
    safe_name = "".join(c if c.isalnum() or c in " _-" else "_" for c in name).strip()

    # Ruta completa del archivo JSON
    file_path = os.path.join(output_dir, f"{safe_name}.json")

    # Guardar el JSON
    with open(file_path, "w", encoding="Latin-1") as json_file:
        json.dump(data, json_file, indent=4, ensure_ascii=False)
        
#################################################################################################################################
#################################################################################################################################
#################################################################################################################################
        

def process_txt(file_path, log = False):
    """
    Reads a TXT file, extracts text line by line, and marks a point
    for applying processing logic to each line.

    Args:
        txt_path (str): The path to the TXT file.
    """
    name = ""
    puesto = ""
    email = ""
    phone = ""
    i = 0

    # Diccionario donde se guardará la información
    data = {}
    linkedin_stack = []
    linkedin_flag = False

    # Variables de estado para saber en qué categoría estamos
    current_category = None

    # Definir reglas personalizadas para categorías (si deben ser listas o concatenadas con \n)
    categories_to_concat = []
    categories_to_concat = ["Summary", "Education", "Experience"]
    # Estas categorías serán concatenadas con \n
    categories_to_keep_as_list = ["Skills","Top Skills","Languages"]  # Estas categorías permanecerán como listas

    try:
        logging.info(f"Iniciando el procesamiento del archivo: {file_path}")

        with open(file_path, 'r', encoding='Latin-1') as file:
            for line_number, line in enumerate(file, start=1):
                line = line.strip()

                if i == 0:
                    name = line
                    i += 1
                    continue
                """if not line:
                    logging.debug(f"Línea {line_number}: (Vacía) - Se ignora")
                    continue  # Ignorar líneas vacías"""

                # Detectar cada categoría manualmente
                if line in ["Extracto", "Summary", "Resumen"]:
                    current_category = "Summary"
                elif line in ["Experiencia", "Experience", "Expérience", "Berufserfahrung"]:
                    current_category = "Experience"
                elif line in ["Educación", "Education", "Formation", "Ausbildung"]:
                    current_category = "Education"
                elif line in ["Contactar", "Contact", "Coordonnées", "Kontakt"]:
                    current_category = "Contact"
                elif line in ["Aptitudes principales", "Top Skills", "Principales compétences", "Top-Kenntnisse"]:
                    current_category = "Top Skills"
                elif line in ["Certifications", "Certificaciones"]:
                    current_category = "Certifications"
                elif line in ["Languages", "Idiomas", "Sprachen"]:
                    current_category = "Languages"
                elif line in ["Honors-Awards", "Distinctions"]:
                    current_category = "Honors-Awards"
                elif line in ["Publications", "Publicaciones"]:
                    current_category = "Publications"
                elif line in ["Skills"]:
                    current_category = "Skills"
                else:


                    # Si ya estamos en una categoría, agregar el contenido
                    if current_category:

                        if (current_category == "Top Skills")|(current_category == "Languages")|(current_category == "Certifications"):
                          if not line:
                            continue

                        if current_category == "Contact":
                            if not line:
                              continue

                            # Si la línea empieza con 'www.linkedin', la agregamos a la pila
                            if line.startswith('www.linkedin') and not '(LinkedIn)' in line:
                                linkedin_stack.append(line)
                                logging.debug(f"Agregado a la pila: {line}")
                                linkedin_flag = True
                                continue

                            # Si la línea contiene '(LinkedIn)'
                            elif line.startswith('www.linkedin') and '(LinkedIn)' in line:
                                data.setdefault(current_category, []).append(line)
                                logging.debug(f"Línea {line_number}: '{line}' agregado a '{current_category}'")
                                continue

                            elif linkedin_flag and not '(LinkedIn)' in line:
                                linkedin_flag = True
                                linkedin_stack.append(line)
                                logging.debug(f"Agregado a la pila: {line}")
                                continue
                            elif linkedin_flag and '(LinkedIn)' in line:
                                linkedin_stack.append(line)
                                linkedin_flag = False
                                linkedin_data = "".join(linkedin_stack)
                                data.setdefault(current_category, []).append(linkedin_data)
                                linkedin_stack = []
                                continue


                        """if current_category == "Summary" or current_category == "Education" or current_category == "Experience":
                            final_data[current_category].append(line)  # Agregar a la lista para concatenar después
                            continue"""


                        data.setdefault(current_category, []).append(line)
                        logging.debug(f"Línea {line_number}: '{line}' agregado a '{current_category}'")
                    else:
                        logging.warning(f"Línea {line_number}: '{line}' no pertenece a ninguna categoría detectada")
                    continue  # Saltar a la siguiente línea





        final_data = {}
        final_data["Name"] = name  # Agrega el campo NAME con el valor extraído
        for category, values in data.items():
            if category in categories_to_concat:
                final_data[category] = "\n".join(values).strip()  # Concatenar con \n











            elif category in categories_to_keep_as_list:
                final_data[category] = values  # Mantener como lista
            else:
                final_data[category] = values  # Mantener como lista # Por defecto

            logging.info("Procesamiento completado. Datos extraídos:")
            for key, value in final_data.items():
                logging.info(f"{key}: {value[:100]}...")  # Mostrar solo los primeros 100 caracteres

        return name,final_data

    except FileNotFoundError:
        print(f"Error: File not found at {txt_path}")
    except Exception as e:
        print(f"An error occurred: {e}")
        
def save_json(name, data, output_dir="/content/residencias/Data/Json/Custom"):
    """Guarda el JSON en la carpeta especificada con el nombre de la persona."""

    if not name:
        logging.error("Error: No se encontró un nombre válido. No se guardará el archivo.")
        return

    # Asegurar que el directorio existe
    os.makedirs(output_dir, exist_ok=True)

    # Limpiar el nombre del archivo (evitar caracteres problemáticos)
    safe_name = "".join(c if c.isalnum() or c in " _-" else "_" for c in name).strip()

    # Ruta completa del archivo JSON
    file_path = os.path.join(output_dir, f"{safe_name}.json")

    # Guardar el JSON
    with open(file_path, "w", encoding="Latin-1") as json_file:
        json.dump(data, json_file, indent=4, ensure_ascii=False)

def list_txt_files(directory):
  """Lists all .txt files and their paths within a given directory.

  Args:
    directory: The path to the directory.

  Returns:
    A list of tuples, where each tuple contains the filename and its full path.
    Returns an empty list if the directory is invalid or no .txt files are found.
  """
  txt_files = []
  if os.path.isdir(directory):
    for filename in os.listdir(directory):
      if filename.endswith(".txt"):
        filepath = os.path.join(directory, filename)
        txt_files.append((filename, filepath))
  return txt_files

def load_json_data_from_directory(directory_path):
    data = []
    for filename in os.listdir(directory_path):
        if filename.endswith(".json"):
            full_path = os.path.join(directory_path, filename)
            with open(full_path, "r", encoding="utf-8") as f:
                try:
                    json_data = json.load(f)
                    json_data["_filename"] = filename
                    data.append(json_data)
                except json.JSONDecodeError:
                    print(f"Error al decodificar {filename}")
    return data

