import pandas as pd
from controllers.file_controller import (
    select_columns, add_user_columns, load_column_template_json, standardize_dataframe
)
from libs.normalizers.cofarsur.controllers.file_controller import (
    read_file, format_fourth_column, assign_headers, exclude_rows_with_values, adjust_price_and_iva, format_and_propagate_date
)

columns = [3, 6, 7, 11, 12, 13, 17]
headers = [
    "registro", "nro cuenta", "col2", "nro fc", "col4", "col5", "cod barra", "desc",
    "col8", "col9", "col10", "iva", "cantidad", "costo", "pvp", "total", "col17", "fecha"
]

mapping = {
    "nro fc": "Nro Comprobante",
    "fecha": "Fecha",
    "Proveedor": "Drogueria",
    "Cuenta": "Nro de Cuenta",
    "cod barra": "Codigo de Barras",
    "desc": "Descripcion",
    "cantidad": "Cantidad",
    "iva": "IVA (%)",
    "costo": "Precio Unitario"
}


def process_cofarsur(df, provider, account):
    try:
        # Leemos el archivo
        df_readed = read_file(df)
        if df_readed is None or df_readed.empty:
            raise ValueError("❌ Error: El archivo leído está vacío o no se pudo procesar.")

        print("📂 Archivo leído correctamente.")

        # Combinamos las columnas de letra y número para factura
        df_fact_formated = format_fourth_column(df_readed)
        if df_fact_formated is None or df_fact_formated.empty:
            raise ValueError("❌ Error: No se pudo formatear la columna de la factura.")

        print("📜 Columna de factura formateada.")

        # Calculo del precio de costo y el IVA
        df_iva_calculated = adjust_price_and_iva(df_fact_formated)
        if df_iva_calculated is None or df_iva_calculated.empty:
            raise ValueError("❌ Error: No se pudo calcular el IVA o el precio de costo.")

        print("💰 Cálculo de IVA y costo realizado.")

        # Tomo la fecha y relleno el df
        df_date = format_and_propagate_date(df_iva_calculated)
        if df_date is None or df_date.empty:
            raise ValueError("❌ Error: No se pudo formatear ni propagar la fecha.")

        print("📅 Fecha formateada y propagada.")

        # Excluyo las filas innecesarias
        df_excluded = exclude_rows_with_values(df_date, 0, ["D"])
        if df_excluded is None or df_excluded.empty:
            raise ValueError("❌ Error: La eliminación de filas no deseadas dejó un DataFrame vacío.")

        print("🗑️ Filas innecesarias eliminadas.")

        # Asignamos headers temporales
        df_w_headers = assign_headers(df_excluded, headers)
        if df_w_headers is None or df_w_headers.empty:
            raise ValueError("❌ Error: No se pudieron asignar los encabezados.")

        print("🏷️ Headers asignados correctamente.")

        # Verificar que las columnas a seleccionar existan en el DataFrame
        max_col_index = df_w_headers.shape[1] - 1
        for col_index in columns:
            if col_index > max_col_index:
                raise IndexError(f"❌ Error: La columna {col_index} no existe en el DataFrame.")

        # Seleccionamos las columnas necesarias
        df_col_selected = select_columns(df_w_headers, columns)
        if df_col_selected is None or df_col_selected.empty:
            raise ValueError("❌ Error: No se pudieron seleccionar las columnas necesarias.")

        print("📑 Columnas seleccionadas correctamente.")

        # Añadimos las columnas de proveedor y cuenta
        df_prov_added = add_user_columns(df_col_selected, provider, account)
        if df_prov_added is None or df_prov_added.empty:
            raise ValueError("❌ Error: No se pudieron agregar las columnas de proveedor y cuenta.")

        print("🏛️ Columnas de proveedor y cuenta añadidas.")

        # Leer template y estandarizar
        final_columns = load_column_template_json(mapping)
        df_standard = standardize_dataframe(df_prov_added, mapping, final_columns)
        if df_standard is None or df_standard.empty:
            raise ValueError("❌ Error: No se pudo estandarizar el DataFrame.")

        print("✔️ DataFrame estandarizado correctamente.")
        
        return df_standard

    except Exception as e:
        raise ValueError(f"❌ Error en process_cofarsur: {str(e)}")
