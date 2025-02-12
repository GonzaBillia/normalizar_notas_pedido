from controllers.file_controller import read_file, select_columns, add_user_columns, load_column_template_json, standardize_dataframe
from libs.normalizers.monroe.controllers.file_controller import combine_columns, fill_dates_from_header, exclude_rows_with_value

# Columnas a seleccionar
columns = [1, 2, 3, 4, 12, 13, 19, 24, 25]

mapping = {
    "NUMERO FACTURA": "Nro Comprobante",
    "FECHA": "Fecha",
    "Proveedor": "Drogueria",
    "Cuenta": "Nro de Cuenta",
    "CODIGO BARRA": "Codigo de Barras",
    "DESCRIPCION": "Descripcion",
    "UNIDADES": "Cantidad",
    "PORC IVA": "IVA (%)",
    "PCIO UNITARIO": "Precio Unitario"
}

def process_monroe(df, provider, account):
    try:
        # Leemos el archivo
        df_readed = read_file(df)
    except Exception as e:
        raise ValueError(f"Error leyendo el archivo: {e}")

    try:
        # Rellenamos los campos necesarios
        df_filled = fill_dates_from_header(df_readed)
    except Exception as e:
        raise ValueError(f"Error en fill_dates_from_header: {e}")

    try:
        # Filtrar filas de cabecera
        df_optimized = exclude_rows_with_value(df_filled, "TIPO LINEA", "Cabecera")
    except Exception as e:
        raise ValueError(f"Error en exclude_rows_with_value: {e}")

    try:
        # Seleccionamos las columnas que necesitamos
        df_col_selected = select_columns(df_optimized, columns)
    except Exception as e:
        raise ValueError(f"Error en select_columns: {e}")

    try:
        # Combinamos las columnas de letra y número para factura
        df_fact_merged = combine_columns(df_col_selected, "LETRA", "NUMERO FORMATEADO")
    except Exception as e:
        raise ValueError(f"Error en combine_columns: {e}")

    try:
        # Añadimos las columnas de proveedor y cuenta
        df_prov_added = add_user_columns(df_fact_merged, provider, account)
    except Exception as e:
        raise ValueError(f"Error en add_user_columns: {e}")

    try:
        # Leer template y estandarizar
        final_columns = load_column_template_json(mapping)
        df_standard = standardize_dataframe(df_prov_added, mapping, final_columns)
    except Exception as e:
        raise ValueError(f"Error en la estandarización del DataFrame: {e}")

    return df_standard
