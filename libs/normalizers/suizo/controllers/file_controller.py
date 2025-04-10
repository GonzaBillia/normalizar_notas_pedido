import pandas as pd

def format_column(df, column, new_col_name):
    """
    Formatea una columna específica transformando valores con un formato específico,
    utilizando además la columna "Tipo de Comprobante" para determinar el prefijo.
    
    La transformación se aplica solo si el valor de la columna tiene al menos 12 caracteres.
    Se extrae la primera letra, el siguiente segmento de 4 dígitos y el remanente, para luego 
    construir el string usando:
        - El prefijo obtenido a partir de "Tipo de Comprobante":
            · "FAC" se transforma a "FC"
            · "NCR" se transforma a "NC"
        - La letra y los números formateados en el siguiente formato:
          <prefijo> <letra> <primer segmento>-<segundo segmento>
    
    Parámetros:
        df (pd.DataFrame): DataFrame que contiene los datos.
        column (str): Nombre de la columna a formatear.
        new_col_name (str): Nombre de la nueva columna con los datos formateados.
    
    Retorna:
        pd.DataFrame: DataFrame con la nueva columna añadida.
    """
    # Verifica que existan la columna a formatear y la columna de tipo de comprobante
    if column not in df.columns:
        raise ValueError(f"❌ La columna '{column}' no existe en el DataFrame.")
    if "Tipo de Comprobante" not in df.columns:
        raise ValueError("❌ La columna 'Tipo de Comprobante' no existe en el DataFrame.")
    
    # Mapeo de valores para el prefijo
    map_tipo = {"FAC": "FC", "NCR": "NC"}
    
    # Función que se aplica a cada fila del DataFrame para transformar el valor
    def transform_row(row):
        value = row[column]
        if isinstance(value, str) and len(value) >= 12:
            letra = value[0]            # Primera letra
            parte1 = value[1:5]         # Primer segmento numérico (4 dígitos)
            parte2 = value[5:]          # Segundo segmento numérico
            tipo = row["Tipo de Comprobante"]  # Valor de la columna Tipo de Comprobante
            prefix = map_tipo.get(tipo, "FC")  # Si no está definido, se usa "FC" por defecto
            return f"{prefix} {letra} {parte1}-{parte2}"
        return value  # Si no cumple la condición, se retorna el valor original

    df = df.copy()
    df[new_col_name] = df.apply(transform_row, axis=1)
    
    return df


def format_fecha_comprobante(df, column, new_col_name):
    """
    Transforma fechas en formato '4022025' o '18022025' a objetos datetime.

    Parámetros:
        df (pd.DataFrame): DataFrame que contiene los datos.
        column (str): Nombre de la columna con la fecha en formato numérico.
        new_col_name (str): Nombre de la nueva columna con la fecha formateada.
    
    Retorna:
        pd.DataFrame: DataFrame con la nueva columna añadida en formato datetime.
    """
    if column not in df.columns:
        raise ValueError(f"❌ La columna '{column}' no existe en el DataFrame.")

    def transform_fecha(value):
        """Convierte la fecha a cadena en formato 'DD/MM/YYYY' dependiendo de su longitud."""
        value = str(value).strip()
        if len(value) == 7:
            # Por ejemplo: '4022025' se interpreta como '04/02/2025'
            dia = value[0].zfill(2)  # Rellena a dos dígitos: '4' -> '04'
            mes = value[1:3]         # Dos dígitos para el mes
            año = value[3:]          # Resto es el año
        elif len(value) == 8:
            # Por ejemplo: '18022025' se interpreta como '18/02/2025'
            dia = value[0:2]         # Día en dos dígitos
            mes = value[2:4]         # Mes en dos dígitos
            año = value[4:]          # Año en cuatro dígitos
        else:
            raise ValueError(f"Formato de fecha desconocido: {value}")
        return f"{dia}/{mes}/{año}"

    # Se transforma la columna a cadenas formateadas y se convierte a datetime
    fechas_formateadas = df[column].apply(transform_fecha)
    df = df.copy()
    df[new_col_name] = pd.to_datetime(fechas_formateadas, format='%d/%m/%Y', errors='coerce')

    return df


def format_quantity_column(df, column):
    """
    Convierte los valores de una columna formateada con ceros a la izquierda y,
    en algunos casos, con un guion (indicando un número negativo), a un valor numérico (entero).
    Se sobreescribe la misma columna con los valores convertidos.

    Ejemplos:
      - "000036"  --> 36
      - "0000-3"  --> -3
      - "00-400"  --> -400

    Parámetros:
        df (pd.DataFrame): DataFrame que contiene la columna con los datos.
        column (str): Nombre de la columna a convertir.

    Retorna:
        pd.DataFrame: DataFrame con la columna especificada actualizada con valores numéricos.
    """
    if column not in df.columns:
        raise ValueError(f"❌ La columna '{column}' no existe en el DataFrame.")

    def convert_quantity_value(value):
        s = str(value).strip()
        if '-' in s:
            # Se asume que el guion indica un número negativo, se elimina el guion y se convierte a entero.
            s_numerico = s.replace('-', '')
            return -int(s_numerico)
        else:
            return int(s)

    df = df.copy()
    df[column] = df[column].apply(convert_quantity_value)
    return df


def fill_dates_from_header(df):
    """
    Rellena la columna 'FECHA' de los detalles con la fecha de su respectiva cabecera,
    asegurando que cada factura (NUMERO FORMATEADO) mantenga su propia fecha.

    Parámetros:
        df (pd.DataFrame): DataFrame con los datos.

    Retorna:
        pd.DataFrame: DataFrame con las fechas correctamente asignadas a los detalles.
    """

    # Verificar que las columnas necesarias existen
    required_columns = {"TIPO LINEA", "NUMERO FORMATEADO", "FECHA"}
    missing_columns = required_columns - set(df.columns)

    if missing_columns:
        raise ValueError(f"Faltan las siguientes columnas requeridas: {missing_columns}")

    # Convertir la columna FECHA a formato datetime para validar fechas
    df["FECHA"] = pd.to_datetime(df["FECHA"], errors="coerce", dayfirst=True)

    # Detectar cabeceras sin fecha
    missing_dates = df[(df["TIPO LINEA"] == "Cabecera") & df["FECHA"].isna()]
    if not missing_dates.empty:
        print("⚠️ Advertencia: Hay cabeceras sin fecha. No se propagará la fecha en estos casos.")
        print(missing_dates)

    # Aplicar el llenado de fechas desde la cabecera hacia los detalles por grupo de "NUMERO FORMATEADO"
    df["FECHA"] = df.groupby("NUMERO FORMATEADO")["FECHA"].ffill()

    return df

def exclude_rows_with_value(df, column_name, value_to_exclude):
    """
    Excluye las filas en las que una columna específica tiene un valor determinado.

    Parámetros:
        df (pd.DataFrame): DataFrame que contiene los datos.
        column_name (str): Nombre de la columna en la que se buscará el valor.
        value_to_exclude (str): Valor que se desea excluir.

    Retorna:
        pd.DataFrame: DataFrame sin las filas que contenían el valor especificado.
    """
    if column_name not in df.columns:
        raise ValueError(f"❌ La columna '{column_name}' no existe en el DataFrame.")

    return df[df[column_name] != value_to_exclude].reset_index(drop=True)
