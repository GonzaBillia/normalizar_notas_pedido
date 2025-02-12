import pandas as pd
import os, csv
from io import StringIO

def format_column(value):
    """
    Aplica formato a un número de comprobante en el formato adecuado.

    Parámetros:
        value (str): Valor del comprobante en formato 'A00180225101'.

    Retorna:
        str: Valor formateado 'FC A 0018-0225101'.
    """
    value = str(value).strip()
    if len(value) >= 12:
        letra = value[0]   # Primera letra
        parte1 = value[1:5]  # Primer segmento numérico
        parte2 = value[5:]   # Segundo segmento numérico
        return f"FC {letra} {parte1}-{parte2}"
    return value  # Si no cumple la condición, deja el valor igual


def process_file(file_path):
    """
    Procesa un archivo CSV, extrayendo el "número comprobante" basado en el nombre del archivo,
    y añadiendo la columna "numero comprobante" al DataFrame. Se valida que el archivo contenga
    las cabeceras esperadas y se reconstruye el DataFrame si existe un separador extra al inicio.

    Cabeceras esperadas:
        Fecha, CodBarra, Producto, Cantidad, Precio Público, Precio Unit., Importe, Faltas

    Parámetros:
        file_path (str): Ruta del archivo CSV.

    Retorna:
        pd.DataFrame: DataFrame del archivo CSV con la columna "numero comprobante".
                      En caso de error, retorna un DataFrame vacío.
    """
    expected_headers = ["Fecha", "CodBarra", "Producto", "Cantidad", "Precio Público", "Precio Unit.", "Importe", "Faltas"]
    possible_seps = [",", "\t", ";"]
    encoding_used = "utf-8-sig"
    
    if not os.path.isfile(file_path):
        raise ValueError(f"❌ El path proporcionado no es un archivo válido: {file_path}")
    
    try:
        # Leer el contenido completo del archivo como texto
        with open(file_path, encoding=encoding_used) as f:
            content = f.read()
        
        # Separar las líneas
        lines = content.splitlines()
        if not lines:
            raise ValueError("El archivo está vacío.")
        
        # Detectar la cabecera
        header_line = lines[0].lstrip('\ufeff').strip()
        detected_sep = None
        for sep in possible_seps:
            parts = header_line.split(sep)
            if len(parts) > 1:
                detected_sep = sep
                break
        
        if detected_sep is None:
            raise ValueError("❌ No se pudo detectar el separador en la cabecera.")
        
        # Obtener las partes del header y descartar un elemento vacío inicial si existe
        header_parts = [h.strip() for h in header_line.split(detected_sep)]
        if header_parts[0] == "":
            header_parts = header_parts[1:]
        
        # Reconstruir el DataFrame usando el contenido restante
        data = "\n".join(lines[1:])
        candidate_df = pd.read_csv(StringIO(data), sep=detected_sep, engine='python', on_bad_lines='skip', header=None)
        
        # Si se leyeron más columnas que las cabecera, revisar si las columnas extra están vacías
        if candidate_df.shape[1] > len(header_parts):
            extra_cols = candidate_df.columns[len(header_parts):]
            if candidate_df[extra_cols].isnull().all().all():
                candidate_df = candidate_df.iloc[:, :len(header_parts)]
            else:
                raise ValueError("Mismatch entre la cabecera y las columnas de datos")
        elif candidate_df.shape[1] < len(header_parts):
            raise ValueError("El número de columnas de datos es menor que el número de encabezados detectados.")
        
        df = candidate_df.copy()
        df.columns = header_parts
        
        missing = [col for col in expected_headers if col not in df.columns]
        if missing:
            raise ValueError(f"❌ Error: Faltan las siguientes columnas: {missing}. Columnas detectadas: {list(df.columns)}")
        
        if df.empty:
            raise ValueError("❌ El DataFrame está vacío tras leer el archivo.")
        
        # Extraer el número comprobante a partir del nombre del archivo
        file_name = os.path.basename(file_path)
        comprobante_raw = os.path.splitext(file_name)[0]  # Elimina la extensión .csv
        comprobante_formateado = format_column(comprobante_raw)  # Función auxiliar que debes definir
        
        # Añadir la columna "numero comprobante" al DataFrame
        df["numero comprobante"] = comprobante_formateado
        
        return df

    except Exception as e:
        print(f"Error al procesar el archivo '{file_path}': {str(e)}")
        return pd.DataFrame()
    

def add_iva_column(df, column_name="IVA", default_value=0):
    """
    Añade una nueva columna con un valor por defecto a un DataFrame.

    Parámetros:
        df (pd.DataFrame): DataFrame al que se añadirá la columna.
        column_name (str): Nombre de la nueva columna (por defecto "IVA").
        default_value (int/float): Valor por defecto para todas las filas (por defecto 0).

    Retorna:
        pd.DataFrame: DataFrame con la nueva columna añadida.
    """
    df[column_name] = default_value
    return df
