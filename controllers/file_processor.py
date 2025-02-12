import os
from PyQt5.QtCore import QThread

class FileProcessor:
    """
    Clase encargada de manejar la lógica de procesamiento de archivos en la aplicación.

    Funcionalidades:
        - Agregar archivos y carpetas a la cola de procesamiento.
        - Determinar el proveedor y llamar a la función adecuada.
        - Procesar archivos en segundo plano mediante QThread y un worker.
    """

    def __init__(self):
        self.files_to_process = []  # Lista de archivos en cola
        self.processed_dataframes = []  # Lista de DataFrames procesados

    def add_file(self, file_path, provider, account):
        if not os.path.exists(file_path):
            print(f"❌ Error: El archivo '{file_path}' no existe.")
            return
        self.files_to_process.append({"path": file_path, "provider": provider, "account": account})
        print(f"✅ Archivo añadido: {file_path} (Proveedor: {provider}, Cuenta: {account})")

    def add_folder(self, folder_path, provider, account):
        if not os.path.exists(folder_path):
            print(f"❌ Error: La carpeta '{folder_path}' no existe.")
            return
        for file_name in os.listdir(folder_path):
            if file_name.endswith(".csv"):
                full_path = os.path.join(folder_path, file_name)
                self.files_to_process.append({"path": full_path, "provider": provider, "account": account})
        print(f"✅ Carpeta añadida: {folder_path} (Proveedor: {provider}, Cuenta: {account})")
    
    def start_processing_worker(self):
        """
        Crea y retorna un QThread y un ProcessingWorker para ejecutar el procesamiento en segundo plano.
        """
        from workers.processing_worker import ProcessingWorker  # Asegúrate de que la ruta sea correcta
        
        thread = QThread()
        worker = ProcessingWorker(self.files_to_process)
        worker.moveToThread(thread)
        thread.started.connect(worker.run)
        return thread, worker
