import pandas as pd
import os, csv
from io import StringIO

def read_file(filepath):
    """
    Lee archivos .dat, .txt o .csv con delimitadores como tabulación, coma, punto y coma, barra vertical o espacio.
    
    Parámetros:
        filepath (str): Ruta del archivo a procesar.

    Retorna:
        pandas.DataFrame: Contenido del archivo en un DataFrame si la lectura es exitosa.
        pandas.DataFrame: DataFrame vacío en caso de error.
    """
    try:
        # Leer todas las líneas del archivo
        with open(filepath, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        # Detectar delimitador usando la primera línea (incluyendo "\t")
        first_line = lines[0].strip()
        delimiters = ["\t", ",", ";", "|", " "]
        detected_delimiter = None
        for delim in delimiters:
            if delim in first_line:
                detected_delimiter = delim
                break

        if not detected_delimiter:
            print(f"Error: No se pudo determinar un delimitador válido en '{filepath}'.")
            return pd.DataFrame()

        # Definir el número de columnas esperado (en este ejemplo, 17)
        expected_columns = 17
        col_names = [f'col{i+1}' for i in range(expected_columns)]

        # Revisar la cantidad de campos en la primera línea
        fields = first_line.split(detected_delimiter)
        if len(fields) < expected_columns:
            missing = expected_columns - len(fields)
            # Agregar al final de la primera línea la cantidad de delimitadores necesarios
            new_first_line = first_line + (detected_delimiter * missing)
            lines[0] = new_first_line + "\n"
            print(f"Se agregaron {missing} delimitadores en la primera fila para alcanzar {expected_columns} columnas.")

        # Reunir el contenido modificado
        new_content = ''.join(lines)

        # Leer el contenido corregido con pandas
        df = pd.read_csv(StringIO(new_content),
                         delimiter=detected_delimiter,
                         quoting=csv.QUOTE_NONE,
                         encoding="utf-8",
                         on_bad_lines='skip',
                         header=None,
                         names=col_names)

        return df

    except Exception as e:
        print(f"Error al leer el archivo '{filepath}': {e}")
        return pd.DataFrame()


def format_fourth_column(df):
    """
    Modifica la cuarta columna del DataFrame en las filas donde la primera columna sea 'D'.
    Transforma el formato de la cuarta columna desde '0307A04304132' a:
      '<prefijo> <letra> <primer segmento>-<segundo segmento>'
    
    Donde:
      - El prefijo se obtiene de la tercera columna:
          'F' -> 'FC'
          'C' -> 'NC'
      - La 'letra' es el carácter en la posición 5 del string original (índice 4)
      - El 'primer segmento' corresponde a los primeros 4 dígitos
      - El 'segundo segmento' corresponde a los dígitos posteriores a la letra
    
    Parámetros:
        df (pd.DataFrame): DataFrame sin headers.
    
    Retorna:
        pd.DataFrame: DataFrame con la cuarta columna modificada donde corresponda.
    """
    
    def transform_value(value, comprobante_type):
        """Convierte '0307A04304132' en '<prefijo> A 0307-04304132' usando comprobante_type para el prefijo."""
        value = str(value).strip()
        if len(value) >= 12:
            # Extraer la letra (en posición 4, índice 4)
            tipo_factura = value[4]
            # Primer segmento: primeros 4 dígitos
            parte1 = value[:4]
            # Segundo segmento: dígitos después de la letra
            parte2 = value[5:]
            # Determinar el prefijo basándonos en el valor de la tercera columna:
            # Se asume que 'F' corresponde a "FC" y 'C' a "NC"; si no coincide, se usa "FC" por defecto
            prefix = "FC" if comprobante_type.upper() == "F" else "NC" if comprobante_type.upper() == "C" else "FC"
            return f"{prefix} {tipo_factura} {parte1}-{parte2}"
        return value

    df = df.copy()
    # Se aplica la transformación en las filas donde la primera columna sea 'D'
    # Se accede a:
    #   row.iloc[0] -> Primera columna
    #   row.iloc[2] -> Tercera columna (para determinar el prefijo)
    #   row.iloc[3] -> Cuarta columna (la que se va a transformar)
    df.iloc[:, 3] = df.apply(lambda row: transform_value(row.iloc[3], row.iloc[2]) 
                                  if row.iloc[0] == "D" 
                                  else row.iloc[3], axis=1)
    return df

def adjust_price_and_iva(df):
    """
    Modifica las columnas 12 y 14 en las filas donde la primera columna sea 'D':
    - Si la columna 12 (índice 11) es 1:
        * Se cambia a 21 (IVA del 21%).
        * La columna 14 (índice 13) se ajusta dividiéndola por 1.21 y redondeándola a 2 decimales.
    - Si la columna 12 es 0, no se hacen modificaciones en cuanto a IVA.
    - Finalmente, la columna 14 (índice 13) se divide por 100.
    
    Parámetros:
        df (pd.DataFrame): DataFrame sin headers.

    Retorna:
        pd.DataFrame: DataFrame con las columnas modificadas donde corresponda.
    """
    def adjust_values(row):
        if row.iloc[0] == "D":
            if row.iloc[11] == 1:  # La columna 12 es el índice 11
                row.iloc[11] = 21  # Cambiar indicador de IVA a 21%
                row.iloc[13] = round(row.iloc[13] / 1.21, 2)  # Ajustar precio sin IVA
            # Al final, dividir la columna 14 (índice 13) por 100
            row.iloc[13] = row.iloc[13] / 100
        return row

    df = df.apply(adjust_values, axis=1)
    return df



def format_and_propagate_date(df):
    """
    - En las filas donde la primera columna sea 'C', toma la fecha de la columna 15 (índice 14),
      la convierte de 'YYYYMMDD' a 'DD/MM/YYYY'.
    - Propaga esta fecha formateada a todas las filas donde la primera columna sea 'D'.
    - Corrige la estructura de las filas si tienen una cantidad desigual de columnas.

    Parámetros:
        df (pd.DataFrame): DataFrame sin headers.

    Retorna:
        pd.DataFrame: DataFrame con la nueva columna de fecha formateada (será la columna 18).
    """
    
    def transform_date(value):
        """Convierte '20250207' (o '20250207.0') en '07/02/2025'."""
        try:
            value_int = int(float(value))
            value_str = str(value_int).zfill(8)
            año, mes, dia = value_str[:4], value_str[4:6], value_str[6:]
            return f"{dia}/{mes}/{año}"
        except Exception as e:
            return ""

    # Paso 1: Asegurarse de que todas las filas tengan la misma cantidad de columnas
    max_cols = df.shape[1]
    df = df.copy()
    df.reset_index(drop=True, inplace=True)
    
    # Normalizar cada fila (rellena con cadenas vacías si la fila tiene menos columnas)
    df = df.apply(lambda row: row.tolist() + [""] * (max_cols - len(row)), axis=1)
    df = pd.DataFrame(df.tolist())
    
    # Paso 2: Asignar nombres genéricos a las columnas
    headers = [f"col_{i}" for i in range(df.shape[1])]
    df.columns = headers

    # Verificar que la columna con la fecha (col_14) existe
    if "col_14" not in df.columns:
        raise KeyError("❌ Error: La columna con la fecha (col_14) no está presente en el DataFrame.")

    # Paso 3: Crear la columna "Fecha Formateada" (será la columna 18)
    df["Fecha Formateada"] = ""

    # Variable para guardar la última fecha formateada encontrada en filas tipo 'C'
    last_date = ""

    # Depuración: Mostrar las primeras filas antes de procesar las fechas
    print("📊 DataFrame antes de procesar fechas:")
    print(df.head(10))

    for index, row in df.iterrows():
        if pd.isna(row["col_0"]):
            continue  # Saltar filas vacías
        if str(row["col_0"]).strip() == "C":
            # Tomar la fecha de la columna 15 (índice 14)
            fecha_valor = str(row["col_14"]).strip()
            last_date = transform_date(fecha_valor)
            df.at[index, "Fecha Formateada"] = last_date
        elif str(row["col_0"]).strip() == "D" and last_date:
            # Propagar la última fecha encontrada en filas tipo 'C'
            df.at[index, "Fecha Formateada"] = last_date

    df["Fecha Formateada"] = pd.to_datetime(df["Fecha Formateada"], format="%d/%m/%Y", errors="coerce")

    # Depuración: Mostrar resultados parciales
    print("📆 DataFrame después de procesar fechas:")
    print(df[["col_0", "col_14", "Fecha Formateada"]].head(10))

    return df



def exclude_rows_with_values(df, column_index, values_to_exclude):
    """
    Conserva solo las filas en las que la columna especificada contiene los valores indicados.

    Parámetros:
        df (pd.DataFrame): DataFrame sin headers.
        column_index (int): Índice de la columna donde se buscarán los valores permitidos.
        values_to_exclude (list): Lista de valores que se desean conservar en la columna.

    Retorna:
        pd.DataFrame: DataFrame con solo las filas que contienen los valores especificados en la columna.
    """
    if column_index >= df.shape[1]:
        raise ValueError(f"❌ El índice de columna '{column_index}' está fuera del rango del DataFrame ({df.shape[1]} columnas).")

    # Conservar solo las filas donde la columna contenga alguno de los valores permitidos
    df_filtered = df[df.iloc[:, column_index].isin(values_to_exclude)].reset_index(drop=True)
    
    return df_filtered




def assign_headers(df, headers):
    """
    Asigna nombres de columnas a un DataFrame sin headers, asegurando alineación correcta.

    Parámetros:
        df (pd.DataFrame): DataFrame sin nombres de columnas.
        headers (list): Lista de nombres de columnas en el orden correcto.

    Retorna:
        pd.DataFrame: DataFrame con los headers asignados.
    """
    if df.empty:
        raise ValueError("❌ El DataFrame está vacío y no se pueden asignar headers.")

    if len(headers) != df.shape[1]:
        raise ValueError(f"❌ El número de headers ({len(headers)}) no coincide con las columnas del DataFrame ({df.shape[1]}).")

    # Reiniciar índices en caso de desplazamiento
    df = df.reset_index(drop=True)

    # Reasignar nombres de columna correctamente
    df.columns = headers

    return df

