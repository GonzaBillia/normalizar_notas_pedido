import json, os, sys
from PyQt5.QtWidgets import QMainWindow, QFileDialog, QMessageBox, QTableWidgetItem, QPushButton
from ui.layout.mainWindow import Ui_MainWindow  # Importamos la UI generada por PyQt5
from controllers.file_processor import FileProcessor  # Procesador de archivos
from controllers.file_controller import merge_and_save, style_excel_file

class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.processor = FileProcessor()  # Instancia del procesador de archivos
        self.accounts_data = self.load_accounts_json()  # Cargar cuentas desde JSON

        # Cargar proveedores en el primer combobox
        self.populate_providers()

        # Conectar eventos
        self.comboBox.currentIndexChanged.connect(self.populate_accounts)
        self.comboBox.currentIndexChanged.connect(self.on_provider_changed)
        self.pushButton_2.clicked.connect(self.add_file)
        self.pushButton_3.clicked.connect(self.add_folder)
        self.pushButton.clicked.connect(self.start_processing)

        self.on_provider_changed()

    def load_accounts_json(self):
        try:
            if getattr(sys, 'frozen', False):  # Si está empaquetado como exe
                base_path = sys._MEIPASS
            else:
                base_path = os.path.abspath(".")
            file_path = os.path.join(base_path, "cuentas.json")
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"❌ No se encontró el archivo: {file_path}")
            with open(file_path, "r", encoding="utf-8") as file:
                return json.load(file)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"❌ Error al cargar cuentas.json: {e}")
            return {}

    def populate_providers(self):
        self.comboBox.clear()
        self.comboBox.addItem("Seleccione un proveedor")
        for provider in self.accounts_data.keys():
            self.comboBox.addItem(provider.capitalize())

    def populate_accounts(self):
        self.comboBox_2.clear()
        self.comboBox_2.addItem("Seleccione una cuenta")
        provider = self.comboBox.currentText().lower()
        if provider in self.accounts_data:
            for account_name, account_number in self.accounts_data[provider].items():
                self.comboBox_2.addItem(f"{account_name.capitalize()} ({account_number})", account_number)
    
    def remove_row(self, row):
        del self.processor.files_to_process[row]
        self.update_table()

    def on_provider_changed(self):
        provider = self.comboBox.currentText().lower()
        if provider == "keller":
            self.pushButton_2.setEnabled(False)
            self.pushButton_3.setEnabled(True)
        else:
            self.pushButton_2.setEnabled(True)
            self.pushButton_3.setEnabled(False)

    def add_file(self):
        provider = self.comboBox.currentText().lower()
        if provider == "keller":
            self.add_folder()
            return
        file_path, _ = QFileDialog.getOpenFileName(self, "Seleccionar Archivo", "", "Archivos (*.csv *.txt *.dat);;Todos los archivos (*)")
        if file_path:
            account = self.comboBox_2.currentData()
            if provider == "seleccione un proveedor" or account is None:
                QMessageBox.warning(self, "Advertencia", "Debe seleccionar un proveedor y una cuenta válida.")
                return
            self.processor.add_file(file_path, provider, account)
            self.update_table()

    def add_folder(self):
        folder_path = QFileDialog.getExistingDirectory(self, "Seleccionar Carpeta Kellerhof")
        if folder_path:
            provider = "keller"
            account = self.comboBox_2.currentData()
            if account is None:
                QMessageBox.warning(self, "Advertencia", "Debe seleccionar una cuenta válida.")
                return
            self.processor.add_folder(folder_path, provider, account)
            self.update_table()

    def update_table(self):
        self.tableWidget.setRowCount(len(self.processor.files_to_process))
        for row, file_info in enumerate(self.processor.files_to_process):
            file_name = os.path.basename(file_info["path"])
            self.tableWidget.setItem(row, 0, QTableWidgetItem(file_name))
            self.tableWidget.setItem(row, 1, QTableWidgetItem(file_info["provider"]))
            self.tableWidget.setItem(row, 2, QTableWidgetItem(str(file_info["account"])))
            btn_delete = QPushButton("❌")
            btn_delete.clicked.connect(lambda _, r=row: self.remove_row(r))
            self.tableWidget.setCellWidget(row, 3, btn_delete)

    def start_processing(self):
        if not self.processor.files_to_process:
            QMessageBox.warning(self, "Advertencia", "No hay archivos para procesar.")
            return
        # Crear el QThread y el worker
        self.thread, self.worker = self.processor.start_processing_worker()
        self.worker.finished.connect(self.handle_processing_finished)
        self.worker.error.connect(self.handle_processing_error)
        self.thread.start()

    def handle_processing_finished(self, processed_dataframes):
        # Este método se ejecuta en el hilo principal
        file_path, _ = QFileDialog.getSaveFileName(self, "Guardar Archivo", "", "Archivos Excel (*.xlsx);;Todos los archivos (*)")
        if not file_path:
            print("⚠️ Guardado cancelado por el usuario.")
        else:
            if not file_path.endswith(".xlsx"):
                file_path += ".xlsx"
            try:
                merge_and_save(processed_dataframes, file_path)
                style_excel_file(file_path)
                print(f"✅ Procesamiento completado. Archivo guardado en: {file_path}")
            except Exception as e:
                print(f"❌ Error al guardar los resultados: {str(e)}")
        self.thread.quit()
        self.thread.wait()

    def handle_processing_error(self, error_message):
        QMessageBox.critical(self, "Error en el procesamiento", error_message)
        self.thread.quit()
        self.thread.wait()
