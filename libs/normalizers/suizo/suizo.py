from controllers.file_controller import read_file, select_columns, add_user_columns, load_column_template_json, standardize_dataframe
from libs.normalizers.suizo.controllers.file_controller import exclude_rows_with_value, format_column, format_fecha_comprobante

columns = [2,4,26,28,29,30,31]

mapping = {
    "num compr": "Nro Comprobante",
    "Fecha": "Fecha",
    "Proveedor": "Drogueria",
    "Cuenta": "Nro de Cuenta",
    "CodBarra": "Codigo de Barras",
    "Descripción del Producto": "Descripcion",
    "Cantidad de Unidades": "Cantidad",
    "Alicuota de IVA %": "IVA (%)",
    "Precio Unitario": "Precio Unitario"
}


def process_suizo(df, provider, account):

    # Leemos el archivo
    df_readed = read_file(df)

    # Filtrar filas de cabecera
    df_optimized_C = exclude_rows_with_value(df_readed, "Tipo de Registro", "C")
    df_optimized = exclude_rows_with_value(df_optimized_C, "Tipo de Registro", "I")

    # seleccionamos las columnas que necesitamos
    df_col_selected = select_columns(df_optimized, columns)

    # formateamos la columna para factura y fecha
    df_fact_formated = format_column(df_col_selected, "Número de Comprobante", "num compr")
    df_fecha_formated = format_fecha_comprobante(df_fact_formated, "Fecha comprobante", "Fecha")

    # añadimos las columnas de proveedor y cuenta
    df_prov_added = add_user_columns(df_fecha_formated, provider, account)

    # Leer template y estandarizar
    final_columns = load_column_template_json(mapping)
    df_standard = standardize_dataframe(df_prov_added, mapping, final_columns)

    return df_standard