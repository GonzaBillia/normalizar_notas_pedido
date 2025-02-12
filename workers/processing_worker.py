# processing_worker.py
from PyQt5.QtCore import QObject, pyqtSignal
from libs.builder.builder import trigger_processing

class ProcessingWorker(QObject):
    finished = pyqtSignal(list)
    error = pyqtSignal(str)
    
    def __init__(self, files_to_process):
        super().__init__()
        self.files_to_process = files_to_process

    def run(self):
        try:
            processed_dataframes = trigger_processing(self.files_to_process)
            if processed_dataframes:
                print("DEBUG: DataFrames procesados:", processed_dataframes)
                self.finished.emit(processed_dataframes)
            else:
                self.error.emit("No se generaron DataFrames procesados.")
        except Exception as e:
            self.error.emit(f"Error durante el procesamiento: {str(e)}")
