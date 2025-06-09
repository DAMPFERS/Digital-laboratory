import sys
import os

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGroupBox,
    QLabel, QTextEdit, QTableWidget, QTableWidgetItem, QPushButton, QFileDialog, QSplitter
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QColor, QPalette
from PyQt5.QtWidgets import QComboBox, QLineEdit, QSpinBox


import pars
import write





class PixelLogicViewer(QMainWindow):
    
    
    def __init__(self):
        super().__init__()
        self.types_name = {0: "Результат Комб.", 1: "Комбинаторная логика", 2: "Результат Послед.", 3: "Последовательностная логика", 4: "Результат автомат." , 5: "Теория автоматов"}
        self.setWindowTitle("Pixel Logic Viewer")
        self.setGeometry(100, 100, 1100, 700)   # Размер окна
        self.setStyleSheet("""
           
            
            QWidget {
                background-color: #0d0d1a;
                color: #00FF99;
                font-family: 'Courier New';
                font-size: 10px;
            }
            QLabel {
                color: #00FF99;
                font-size: 20px;
                margin-top: 15px;
            }
            QTextEdit {
                background-color: #0d0d1a;
                color: #00FF99;
                border: 1px solid #00FF99;
                font-family: 'Courier New';
                font-size: 18px;
                border-radius: 12px
            }
            QGroupBox {
                border: 2px solid #00FF99;
                margin-top: 1px;
                border-radius: 10px;
                font-size: 24px;
                font-weight: bold;
            }
            QLineEdit {
                border: 1px solid #00FF99;
                border-radius: 3px;
                font-size: 18px;
                font-weight: bold;
            }
            QComboBox {
                font-size: 18px;
                font-weight: bold;
            }
            QSpinBox {
                border: 1px solid #00FF99;
                font-size: 20px;
            }
            QPushButton {
                border: 1px solid #00FF99;
                color: #00FF99;
                background-color: transparent;
                padding: 14px 12px;
                font-size: 18px;
                border-radius: 10px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #00FF99;
                color: #0d0d1a;
            }
            
        """)
        
        # Текущий индекс отображаемой таблицы
        self.functions = [None] * 16  # максимум 16 функций
        self.current_index = 0
        
        
        
        
        self.setup_mode = False  # флаг: режим создания
        self.new_file_data = {
            "id": QLineEdit(),
            "speed": QLineEdit(),
            "text": QTextEdit(),
            "type": QComboBox(),
            "variables": QSpinBox()
        }
        self.new_file_data["type"].addItems(list(self.types_name.values()))
        self.new_file_data["variables"].setRange(1, 8)
        # self.new_file_data["variables"].valueChanged.connect(self.generate_empty_table)
        self.new_file_data["variables"].valueChanged.connect(self.regenerate_table_by_spinbox)


        
        
        
        self.init_ui()


    def init_ui(self):
        main_widget = QWidget()
        main_layout = QVBoxLayout()
        splitter = QSplitter(Qt.Horizontal)

        # Left panel
        self.left_panel = QWidget()
        left_layout = QVBoxLayout()
        self.task_group = QGroupBox("TASK DETAILS")
        task_layout = QVBoxLayout()
        self.label_id = QLabel("№: ")
        self.label_type = QLabel("Type: ")
        self.label_speed = QLabel("Speed: ")
        self.task_text = QTextEdit()
        self.task_text.setReadOnly(True)

        task_layout.addWidget(self.label_id)
        task_layout.addWidget(self.label_type)
        task_layout.addWidget(self.label_speed)
        task_layout.addWidget(self.task_text)
        self.task_group.setLayout(task_layout)
        left_layout.addWidget(self.task_group)
        self.left_panel.setLayout(left_layout)

        # Right panel
        self.right_panel = QWidget()
        self.right_layout = QVBoxLayout()

        self.table_label = QLabel("Table")
        self.sub_label = QLabel("Truth Table")
        self.table = QTableWidget()
        self.table.setStyleSheet("""
            QTableWidget {
                background-color: #0d0d1a;
                color: #00FF99;
                gridline-color: #00FF99;
                border: none;
                font-size: 18px;
            }
            QHeaderView::section {
                background-color: #0d0d1a;
                color: #00FF99;
                border: 1px solid #00FF99;
                font-size: 20px;
            }
            QTableCornerButton::section {
                background-color: #00FF99;
                border: 1px solid #00FF99;
            }
        """)
        # Настройка выравнивания заголовков
        header = self.table.horizontalHeader()
        header.setDefaultAlignment(Qt.AlignCenter)  # Выравнивание по центру
        header = self.table.verticalHeader()
        header.setDefaultAlignment(Qt.AlignCenter)  # Выравнивание по центру
        self.right_layout.addWidget(self.table_label)
        self.right_layout.addWidget(self.sub_label)
        self.right_layout.addWidget(self.table)
        self.right_panel.setLayout(self.right_layout)

        splitter.addWidget(self.left_panel)
        splitter.addWidget(self.right_panel)
        splitter.setSizes([300, 800])

        main_layout.addWidget(splitter)

        # Bottom buttons
        button_layout = QHBoxLayout()
        self.open_btn = QPushButton("OPEN FILE")
        self.prev_btn = QPushButton("<<")
        self.next_btn = QPushButton(">>")
        self.setup_btn = QPushButton("SET UP")
        self.save_btn = QPushButton("SAVE")

        self.open_btn.clicked.connect(self.open_file)
        self.prev_btn.clicked.connect(self.prev_table)
        self.next_btn.clicked.connect(self.next_table)

        for btn in [self.open_btn, self.prev_btn, self.next_btn, self.setup_btn, self.save_btn]:
            button_layout.addWidget(btn)

        main_layout.addLayout(button_layout)
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)
        
        
        
        # подключаем действия
        self.setup_btn.clicked.connect(self.enter_setup_mode)
        self.save_btn.clicked.connect(self.save_to_file)


    def open_file(self):
        
        if self.setup_mode:
            self.setup_mode = False
            self.rebuild_task_panel()
            
            
        file_name, _ = QFileDialog.getOpenFileName(self, "Open Binary File", "", "Binary Files (*.bin)")
        if file_name:
            bin_file = pars.parse_bin_file(file_name)
            if bin_file:
                
                self.label_id.setText(f"№: {bin_file.id}")
                self.label_type.setText(f"Type: {self.types_name[bin_file.type]}")
                self.label_speed.setText(f"Speed: {bin_file.speed} MIPS")
                self.task_text.setText(bin_file.text or "")
                self.functions = bin_file.functions[:bin_file.function_count]
                self.current_index = 0
                self.update_table()


    def update_table(self):
        if not self.functions:
            return
        func = self.functions[self.current_index]
        num_rows = 1 << func.num_vars
        self.table.setRowCount(num_rows)
        self.table.setColumnCount(func.num_vars + 1)

        # вычленение индексов переменных
        variables = list()
        count = func.num_vars
        i = 0
        while(i < 16 and count > 0):
            if ((func.var_mask >> i) & 0x01) == 1:
                count -= 1
                variables.append(i)
            i += 1
            

        headers = [f"X{i}" for i in variables] + ["Result"]
        self.table.setHorizontalHeaderLabels(headers)


        for i in range(num_rows):
            for j in range(func.num_vars):
                bit = (i >> (func.num_vars - j - 1)) & 0x01
                # self.table.setItem(i, j, QTableWidgetItem(str(bit)))
                bit_item = QTableWidgetItem(str(bit))
                bit_item.setTextAlignment(Qt.AlignCenter)
                bit_item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)
                self.table.setItem(i, j, bit_item)

            result_bit = (func.bit_vector[i >> 3] >> (7 - (i % 8))) & 0x01
            result_bit = (func.bit_vector[i >> 3] >> (i % 8)) & 0x01
            result_item = QTableWidgetItem(str(result_bit))
            result_item.setTextAlignment(Qt.AlignCenter)
            result_item.setForeground(QColor("#FF69B4"))
            result_item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)
            self.table.setItem(i, func.num_vars, result_item)

            for j in range(func.num_vars + 1):
                self.table.item(i, j).setTextAlignment(Qt.AlignCenter)

        self.table_label.setText(f"Table {self.current_index + 1}")
        self.sub_label.setText(f"Truth Table #{func.name_func} | Variables: {func.num_vars}")


    def next_table(self):
        if self.setup_mode:
            if self.current_index < 15:
                self.save_current_function()
                self.current_index += 1
                self.generate_empty_table()
        elif self.current_index < len(self.functions) - 1:
            self.current_index += 1
            self.update_table()


    def prev_table(self):
        if self.setup_mode:
            if self.current_index > 0:
                self.save_current_function()
                self.current_index -= 1
                self.generate_empty_table()
        elif self.current_index > 0:
            self.current_index -= 1
            self.update_table()
            
            
    def enter_setup_mode(self):
        self.setup_mode = True
        self.functions = [None] * 16
        self.current_index = 0

        layout = self.left_panel.layout()
        for i in reversed(range(layout.count())):
            widget = layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)

        # ПЕРЕСОЗДАЁМ ВИДЖЕТЫ
        self.new_file_data = {
            "id": QLineEdit(),
            "speed": QLineEdit(),
            "text": QTextEdit(),
            "type": QComboBox(),
            "variables": QSpinBox()
        }
        self.new_file_data["type"].addItems(list(self.types_name.values()))
        self.new_file_data["variables"].setRange(1, 8)
        self.new_file_data["variables"].valueChanged.connect(self.regenerate_table_by_spinbox)

        self.input_group = QGroupBox("CREATE NEW TASK")
        form_layout = QVBoxLayout()

        form_layout.addWidget(QLabel("Task ID:"))
        form_layout.addWidget(self.new_file_data["id"])
        form_layout.addWidget(QLabel("Speed:"))
        form_layout.addWidget(self.new_file_data["speed"])
        form_layout.addWidget(QLabel("Text:"))
        form_layout.addWidget(self.new_file_data["text"])
        form_layout.addWidget(QLabel("Type:"))
        form_layout.addWidget(self.new_file_data["type"])
        form_layout.addWidget(QLabel("Variables:"))
        form_layout.addWidget(self.new_file_data["variables"])

        self.input_group.setLayout(form_layout)
        layout.addWidget(self.input_group)

        self.generate_empty_table()
             
        
    def save_to_file(self):
        if not self.setup_mode:
            return

        bin_file = write.BinFile()
        try:
            bin_file.id = int(self.new_file_data["id"].text())
            bin_file.speed = int(self.new_file_data["speed"].text())
            bin_file.text = self.new_file_data["text"].toPlainText()
            bin_file.type = self.new_file_data["type"].currentIndex()
        except ValueError:
            print("Invalid input")
            return

        num_vars = self.new_file_data["variables"].value()
        num_rows = 1 << num_vars
        bit_vector = bytearray((num_rows + 7) // 8)

        for i in range(num_rows):
            item = self.table.item(i, num_vars)
            if item and item.text().strip() == "1":
                byte_index = i // 8
                bit_index = i % 8
                bit_vector[byte_index] |= (1 << bit_index)

        # func = write.add_Func(0, num_vars, bytes(bit_vector), (1 << num_vars) - 1)
        # bin_file.functions[0] = func
        # bin_file.function_count = 1

        self.save_current_function()  # сохранить последнюю перед экспортом

        bin_file.function_count = 0
        for i in range(16):
            func = self.functions[i]
            if func:
                bin_file.functions[bin_file.function_count] = func
                bin_file.function_count += 1
        
        
        path, _ = QFileDialog.getSaveFileName(self, "Save Binary File", "", "Binary Files (*.bin)")
        if path:
            write.generate_bin_file(path, bin_file)
            
            
    def rebuild_task_panel(self):
        layout = self.left_panel.layout()
        for i in reversed(range(layout.count())):
            widget = layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)

        self.task_group = QGroupBox("TASK DETAILS")
        task_layout = QVBoxLayout()
        self.label_id = QLabel("№: ")
        self.label_type = QLabel("Type: ")
        self.label_speed = QLabel("Speed: ")
        self.task_text = QTextEdit()
        self.task_text.setReadOnly(True)

        task_layout.addWidget(self.label_id)
        task_layout.addWidget(self.label_type)
        task_layout.addWidget(self.label_speed)
        task_layout.addWidget(self.task_text)
        self.task_group.setLayout(task_layout)
        layout.addWidget(self.task_group)
        
        
    def save_current_function(self):
        if not self.setup_mode:
            return

        num_vars = self.new_file_data["variables"].value()
        num_rows = 1 << num_vars
        bit_vector = bytearray((num_rows + 7) // 8)

        for i in range(num_rows):
            item = self.table.item(i, num_vars)
            if item and item.text().strip() == "1":
                byte_index = i // 8
                bit_index = i % 8
                bit_vector[byte_index] |= (1 << bit_index)

        func = write.add_Func(self.current_index, num_vars, bytes(bit_vector), (1 << num_vars) - 1)
        self.functions[self.current_index] = func
        
        
    def regenerate_table_by_spinbox(self):
        """Вызывается, когда пользователь вручную меняет количество переменных"""
        if self.setup_mode:
            self.save_current_function()
            self.generate_empty_table(from_spinbox=True)
            
            
    def generate_empty_table(self, from_spinbox=False):
        if self.setup_mode:
            # Выбор размерности: либо вручную, либо по сохранённой функции
            if from_spinbox:
                num_vars = self.new_file_data["variables"].value()
            else:
                existing_func = self.functions[self.current_index]
                if existing_func:
                    num_vars = existing_func.num_vars
                else:
                    num_vars = 1
                self.new_file_data["variables"].blockSignals(True)
                self.new_file_data["variables"].setValue(num_vars)
                self.new_file_data["variables"].blockSignals(False)

            # Размер таблицы
            num_rows = 1 << num_vars
            self.table.setRowCount(num_rows)
            self.table.setColumnCount(num_vars + 1)
            headers = [f"X{i}" for i in range(num_vars)] + ["Result"]
            self.table.setHorizontalHeaderLabels(headers)

            # Восстановление значений
            bit_data = [0] * num_rows
            existing_func = self.functions[self.current_index]
            if existing_func and existing_func.num_vars == num_vars:
                for i in range(num_rows):
                    bit = (existing_func.bit_vector[i >> 3] >> (i % 8)) & 1
                    bit_data[i] = bit

            for i in range(num_rows):
                for j in range(num_vars):
                    bit = (i >> (num_vars - j - 1)) & 1
                    # self.table.setItem(i, j, QTableWidgetItem(str(bit)))
                    bit_item = QTableWidgetItem(str(bit))
                    bit_item.setTextAlignment(Qt.AlignCenter)
                    self.table.setItem(i, j, bit_item)
                result_item = QTableWidgetItem(str(bit_data[i]))
                result_item.setTextAlignment(Qt.AlignCenter)
                self.table.setItem(i, num_vars, result_item)

            self.table_label.setText(f"Table {self.current_index + 1} (edit mode)")
            self.sub_label.setText("Editable truth table")








if __name__ == "__main__":
    app = QApplication(sys.argv)
    dark_palette = QPalette()
    dark_palette.setColor(QPalette.Window, QColor(13, 13, 26))
    dark_palette.setColor(QPalette.WindowText, QColor(0, 255, 153))
    app.setPalette(dark_palette)

    viewer = PixelLogicViewer()
    viewer.show()
    sys.exit(app.exec_())
