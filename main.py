import sys
import os

# Obtener la ruta absoluta del directorio base del proyecto
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Agregar `BASE_DIR` al sys.path (importante para PyInstaller)
if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)

# Asegurar que `ui/` y `controllers/` están en el path
UI_DIR = os.path.join(BASE_DIR, "ui")
CONTROLLERS_DIR = os.path.join(BASE_DIR, "controllers")

if UI_DIR not in sys.path:
    sys.path.append(UI_DIR)

if CONTROLLERS_DIR not in sys.path:
    sys.path.append(CONTROLLERS_DIR)

print("PYTHON PATH:", sys.path)  # Debug para verificar rutas

# Importar la UI después de agregar las rutas
from ui.main_window import MainWindow
from PyQt5.QtWidgets import QApplication

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
