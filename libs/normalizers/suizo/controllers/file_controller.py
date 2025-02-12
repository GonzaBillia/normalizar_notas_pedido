import pandas as pd
    
def format_column(df, column, new_col_name):
    """
    Formatea una columna específica transformando valores con un formato específico.

    Parámetros:
        df (pd.DataFrame): DataFrame que contiene los datos.
        column (str): Nombre de la columna a formatear.
        new_col_name (str): Nombre de la nueva columna con los datos formateados.

    Retorna:
        pd.DataFrame: DataFrame con la nueva columna añadida.
    """
    if column not in df.columns:
        raise ValueError(f"❌ La columna '{column}' no existe en el DataFrame.")

    def transform_value(value):
        """Aplica la transformación al valor de la columna."""
        if isinstance(value, str) and len(value) >= 12:
            letra = value[0]   # Primera letra
            parte1 = value[1:5]  # Primer segmento numérico
            parte2 = value[5:]   # Segundo segmento numérico
            return f"FC {letra} {parte1}-{parte2}"
        return value  # Si no cumple la condición, deja el valor igual

    # Aplicar la transformación
    df[new_col_name] = df[column].apply(transform_value)

    return df

def format_fecha_comprobante(df, column, new_col_name):
    """
    Transforma fechas en formato '4022025' a 'DD/MM/YYYY'.

    Parámetros:
        df (pd.DataFrame): DataFrame que contiene los datos.
        column (str): Nombre de la columna con la fecha en formato numérico.
        new_col_name (str): Nombre de la nueva columna con la fecha formateada.

    Retorna:
        pd.DataFrame: DataFrame con la nueva columna añadida.
    """
    if column not in df.columns:
        raise ValueError(f"❌ La columna '{column}' no existe en el DataFrame.")

    def transform_fecha(value):
        """Convierte '4022025' en '04/02/2025'."""
        value = str(value).strip()
        if len(value) == 7:
            dia = value[0]  # Primer dígito (día)
            mes = value[1:3]  # Segundo y tercer dígito (mes)
            año = value[3:]  # Resto es el año
            return f"{dia.zfill(2)}/{mes}/{año}"
        return value  # Si no cumple la condición, deja el valor igual

    df[new_col_name] = df[column].apply(transform_fecha)

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
