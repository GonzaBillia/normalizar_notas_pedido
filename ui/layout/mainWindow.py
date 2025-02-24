from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(600, 479)  # Se amplía la ventana horizontalmente
        
        # Crear widget central y el layout principal vertical
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.main_layout = QtWidgets.QVBoxLayout(self.centralwidget)
        self.main_layout.setContentsMargins(20, 20, 20, 20)
        self.main_layout.setSpacing(10)
        
        # Título principal
        self.label = QtWidgets.QLabel(self.centralwidget)
        font = QtGui.QFont()
        font.setPointSize(12)
        font.setBold(True)
        self.label.setFont(font)
        self.label.setObjectName("label")
        self.main_layout.addWidget(self.label)
        
        # Línea divisoria
        self.line = QtWidgets.QFrame(self.centralwidget)
        self.line.setFrameShape(QtWidgets.QFrame.HLine)
        self.line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line.setObjectName("line")
        self.main_layout.addWidget(self.line)
        
        # Etiqueta para seleccionar archivo
        self.label_2 = QtWidgets.QLabel(self.centralwidget)
        font2 = QtGui.QFont()
        font2.setPointSize(10)
        self.label_2.setFont(font2)
        self.label_2.setObjectName("label_2")
        self.main_layout.addWidget(self.label_2)
        
        # Layout horizontal para dropdowns y botón de subir
        dropdown_layout = QtWidgets.QHBoxLayout()
        dropdown_layout.setSpacing(10)
        
        sizePolicyExpanding = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        
        self.comboBox = QtWidgets.QComboBox(self.centralwidget)
        self.comboBox.setSizePolicy(sizePolicyExpanding)
        self.comboBox.setObjectName("comboBox")
        self.comboBox.addItem("")
        dropdown_layout.addWidget(self.comboBox)
        
        self.comboBox_2 = QtWidgets.QComboBox(self.centralwidget)
        self.comboBox_2.setSizePolicy(sizePolicyExpanding)
        self.comboBox_2.setObjectName("comboBox_2")
        self.comboBox_2.addItem("")
        dropdown_layout.addWidget(self.comboBox_2)
        
        self.pushButton_2 = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_2.setObjectName("pushButton_2")
        dropdown_layout.addWidget(self.pushButton_2)
        
        self.main_layout.addLayout(dropdown_layout)
        
        # Etiqueta para la selección de carpeta
        self.label_3 = QtWidgets.QLabel(self.centralwidget)
        font3 = QtGui.QFont()
        font3.setPointSize(10)
        self.label_3.setFont(font3)
        self.label_3.setObjectName("label_3")
        self.main_layout.addWidget(self.label_3)
        
        # Layout horizontal para botón de subir carpeta (opcional)
        folder_layout = QtWidgets.QHBoxLayout()
        folder_layout.setSpacing(10)
        self.pushButton_3 = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_3.setObjectName("pushButton_3")
        folder_layout.addWidget(self.pushButton_3)
        self.main_layout.addLayout(folder_layout)
        
        # Tabla (se adapta al ancho disponible)
        self.tableWidget = QtWidgets.QTableWidget(self.centralwidget)
        self.tableWidget.setObjectName("tableWidget")
        self.tableWidget.setColumnCount(4)
        self.tableWidget.setRowCount(0)
        # Definir los headers de la tabla
        for i in range(4):
            item = QtWidgets.QTableWidgetItem()
            self.tableWidget.setHorizontalHeaderItem(i, item)
        header = self.tableWidget.horizontalHeader()
        header.setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        self.main_layout.addWidget(self.tableWidget)
        
        # Botón para procesar archivos
        self.pushButton = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton.setObjectName("pushButton")
        self.main_layout.addWidget(self.pushButton)
        
        MainWindow.setCentralWidget(self.centralwidget)
        
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        
        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)
    
    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.label.setText(_translate("MainWindow", "Normalizador de Notas de Pedido"))
        self.label_2.setText(_translate("MainWindow", "Selecciona el Archivo a procesar:"))
        self.comboBox.setItemText(0, _translate("MainWindow", "Droguería"))
        self.comboBox_2.setItemText(0, _translate("MainWindow", "Cuenta"))
        self.pushButton_2.setText(_translate("MainWindow", "Subir"))
        self.label_3.setText(_translate("MainWindow", "Selecciona la Carpeta Kellerhof:"))
        self.pushButton_3.setText(_translate("MainWindow", "Subir"))
        item = self.tableWidget.horizontalHeaderItem(0)
        item.setText(_translate("MainWindow", "Archivo"))
        item = self.tableWidget.horizontalHeaderItem(1)
        item.setText(_translate("MainWindow", "Droguería"))
        item = self.tableWidget.horizontalHeaderItem(2)
        item.setText(_translate("MainWindow", "Cuenta"))
        item = self.tableWidget.horizontalHeaderItem(3)
        item.setText(_translate("MainWindow", "Eliminar"))
        self.pushButton.setText(_translate("MainWindow", "Procesar Archivos"))
