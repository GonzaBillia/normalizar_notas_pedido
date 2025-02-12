from controllers.file_controller import select_columns, add_user_columns, load_column_template_json, standardize_dataframe
from libs.normalizers.keller.controllers.file_controller import  process_file, add_iva_column


columns = [0,1,2,3,5,8]

mapping = {
    "numero comprobante": "Nro Comprobante",
    "Fecha": "Fecha",
    "Proveedor": "Drogueria",
    "Cuenta": "Nro de Cuenta",
    "CodBarra": "Codigo de Barras",
    "Producto": "Descripcion",
    "Cantidad": "Cantidad",
    "IVA": "IVA (%)",
    "Precio Unit.": "Precio Unitario"
}

def process_keller(fd, provider, account):

    # leemos y procesamos la carpeta:
    fd_processed = process_file(fd)
    print(fd_processed)

    # seleccionamos las columnas
    df_col_selected = select_columns(fd_processed, columns)
    print(df_col_selected)

    # Añadimos la columna porc IVA
    df_iva_added = add_iva_column(df_col_selected)
    print(df_iva_added)

    # añadimos las columnas de proveedor y cuenta
    df_prov_added = add_user_columns(df_iva_added, provider, account)
    print(df_prov_added)

    # Leer template y estandarizar
    final_columns = load_column_template_json(mapping)
    df_standard = standardize_dataframe(df_prov_added, mapping, final_columns)

    return df_standard