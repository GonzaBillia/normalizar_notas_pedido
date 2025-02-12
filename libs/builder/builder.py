import json
import os
import sys
from libs.normalizers.cofarsur.cofarsur import process_cofarsur
from libs.normalizers.suizo.suizo import process_suizo
from libs.normalizers.monroe.monroe import process_monroe
from libs.normalizers.keller.keller import process_keller

def trigger_processing(files_info):
    """
    Recorre un array de objetos con información de archivos a procesar,
    determina el proveedor y llama a la función correspondiente.

    Parámetros:
        files_info (list[dict]): Lista de diccionarios con:
            - "path" (str): Ruta del archivo.
            - "provider" (str): Nombre del proveedor.
            - "account" (int/str): Número de cuenta (excepto para keller).

    Retorna:
        list[pd.DataFrame]: Lista de DataFrames procesados.
    
    Si ocurre un error en el procesamiento de un archivo, se lanza la excepción.
    """
    # Diccionario que asocia proveedores con sus funciones
    provider_functions = {
        "monroe": process_monroe,
        "cofarsur": process_cofarsur,
        "suizo": process_suizo,
        "keller": process_keller
    }

    processed_dfs = []  # Lista para almacenar los DataFrames procesados

    for file_info in files_info:
        # Validar información básica
        if "path" not in file_info or "provider" not in file_info:
            raise ValueError(f"❌ Error: Falta información en {file_info}")

        path = file_info["path"]
        provider = file_info["provider"].lower()  # Normalizamos a minúsculas

        # Para 'keller', leer la cuenta desde el archivo cuentas.json
        if provider == "keller":
            # Determinar la ruta base en función de si estamos empaquetados o no
            if getattr(sys, 'frozen', False):
                base_path = sys._MEIPASS
            else:
                base_path = os.path.abspath(".")
            cuentas_path = os.path.join(base_path, "cuentas.json")
            with open(cuentas_path, "r") as f:
                config = json.load(f)
            account = config.get("keller", {}).get("depo")
            if account is None:
                raise ValueError("❌ No se encontró la cuenta 'depo' para 'keller' en cuentas.json")
        else:
            # Para otros proveedores se espera que 'account' esté en file_info
            if "account" not in file_info:
                raise ValueError(f"❌ Error: Falta 'account' para el proveedor '{provider}' en {file_info}")
            account = file_info["account"]

        # Buscar la función correspondiente al proveedor
        process_function = provider_functions.get(provider)
        if process_function is None:
            raise ValueError(f"❌ Error: No hay función asignada para el proveedor '{provider}'.")

        # Imprimir mensaje informativo antes de procesar
        print(f"🔹 Procesando archivo '{path}' con proveedor '{provider}' y cuenta '{account}'...")
        df_processed = process_function(path, provider, account)

        if df_processed is not None:
            processed_dfs.append(df_processed)
        else:
            # Si la función de procesamiento retorna None, consideramos que hubo un error
            raise ValueError(f"⚠️ Advertencia: El archivo '{path}' no pudo ser procesado.")

    return processed_dfs
