import pandas as pd
    
def combine_columns(df, letra_col, numero_col, tipo_col="TIPO", new_col_name="NUMERO FACTURA", separator=" "):
    """
    Combina el prefijo (tipo), la letra y el número formateado para generar el número de factura.

    Parámetros:
        df (pd.DataFrame): DataFrame con las columnas a combinar.
        letra_col (str): Nombre de la columna que contiene la letra de la factura.
        numero_col (str): Nombre de la columna que contiene el número formateado.
        tipo_col (str): Nombre de la columna que contiene el tipo (por ejemplo, "FC" o "NC").
                        Si la columna no existe, se usará por defecto "FC".
        new_col_name (str): Nombre de la nueva columna combinada. (Por defecto 'NUMERO FACTURA')
        separator (str): Separador entre los valores (por defecto un espacio " ").

    Retorna:
        pd.DataFrame: DataFrame con la nueva columna añadida.
    """
    # Verificamos que existan las columnas letra y número formateado
    if letra_col not in df.columns or numero_col not in df.columns:
        raise ValueError(f"❌ Las columnas '{letra_col}' y/o '{numero_col}' no existen en el DataFrame.")

    df = df.copy()

    # Definimos el prefijo: si la columna tipo_col existe, se toma su valor, de lo contrario se usa "FC"
    if tipo_col in df.columns:
        prefix = df[tipo_col].astype(str)
    else:
        prefix = "FC"

    # Se forma la nueva columna combinando el prefijo, la letra y el número formateado con el separador
    df[new_col_name] = prefix + separator + df[letra_col].astype(str) + separator + df[numero_col].astype(str)

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
