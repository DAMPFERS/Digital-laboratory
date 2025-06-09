import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGroupBox,
    QLabel, QTextEdit, QTableWidget, QTableWidgetItem, QPushButton,
    QFileDialog, QSplitter, QComboBox, QLineEdit, QSpinBox
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QPalette

import pars
import write

class PixelLogicViewer(QMainWindow):
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Pixel Logic Viewer")
        self.setGeometry(100, 100, 1100, 700)

        self.types_name = {
            0: "Результат Комб.", 1: "Комбинаторная логика",
            2: "Результат Послед.", 3: "Последовательностная логика",
            4: "Результат автомат.", 5: "Теория автоматов"
        }
        
        
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
        

        self.functions = [None] * 16
        self.current_index = 0
        self.setup_mode = False

        self.init_ui()


    def init_ui(self):
        # Создание элементов ввода
        self.new_file_data = {
            "id": QLineEdit(),
            "speed": QLineEdit(),
            "text": QTextEdit(),
            "type": QComboBox(),
            "variables": QSpinBox(),
            "var_indices": QLineEdit()
        }
        self.new_file_data["type"].addItems(list(self.types_name.values()))
        self.new_file_data["variables"].setRange(1, 8)
        self.new_file_data["variables"].valueChanged.connect(self.regenerate_table_by_spinbox)
        self.new_file_data["var_indices"].textChanged.connect(self.regenerate_table_by_varmask)

        # Центральное окно
        main_widget = QWidget()
        main_layout = QVBoxLayout()
        splitter = QSplitter(Qt.Horizontal)

        # Левая панель (информация)
        self.left_panel = QWidget()
        left_layout = QVBoxLayout()
        self.task_group = QGroupBox("TASK DETAILS")
        task_layout = QVBoxLayout()
        self.label_id = QLabel("№: ")
        self.label_type = QLabel("TYPE: ")
        self.label_speed = QLabel("SPEED: ")
        self.task_text = QTextEdit()
        self.task_text.setReadOnly(True)
        for widget in [self.label_id, self.label_type, self.label_speed, self.task_text]:
            task_layout.addWidget(widget)
        self.task_group.setLayout(task_layout)
        left_layout.addWidget(self.task_group)
        self.left_panel.setLayout(left_layout)

        # Правая панель (таблица)
        self.right_panel = QWidget()
        self.right_layout = QVBoxLayout()
        self.table_label = QLabel("Table")
        self.sub_label = QLabel("Truth Table")
        self.table = QTableWidget()
        self.table.setStyleSheet("""
            QTableWidget { background-color: #0d0d1a; color: #00FF99; gridline-color: #00FF99;
                           border: none; font-size: 18px; }
            QHeaderView::section { background-color: #0d0d1a; color: #00FF99; border: 1px solid #00FF99; font-size: 20px; }
            QTableCornerButton::section { background-color: #00FF99; border: 1px solid #00FF99; }
        """)
        self.right_layout.addWidget(self.table_label)
        self.right_layout.addWidget(self.sub_label)
        self.right_layout.addWidget(self.table)
        self.right_panel.setLayout(self.right_layout)

        splitter.addWidget(self.left_panel)
        splitter.addWidget(self.right_panel)
        splitter.setSizes([400, 800])
        main_layout.addWidget(splitter)

        # Нижние кнопки
        button_layout = QHBoxLayout()
        self.open_btn = QPushButton("OPEN FILE")
        self.prev_btn = QPushButton("<<")
        self.next_btn = QPushButton(">>")
        self.setup_btn = QPushButton("SET UP")
        self.save_btn = QPushButton("SAVE")
        for btn in [self.open_btn, self.prev_btn, self.next_btn, self.setup_btn, self.save_btn]:
            button_layout.addWidget(btn)
        main_layout.addLayout(button_layout)

        # Назначение событий
        self.open_btn.clicked.connect(self.open_file)
        self.prev_btn.clicked.connect(self.prev_table)
        self.next_btn.clicked.connect(self.next_table)
        self.setup_btn.clicked.connect(self.enter_setup_mode)
        self.save_btn.clicked.connect(self.save_to_file)

        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)

    def enter_setup_mode(self):
        self.setup_mode = True
        self.functions = [None] * 16
        self.current_index = 0

        layout = self.left_panel.layout()
        for i in reversed(range(layout.count())):
            widget = layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)

        # Группа создания задачи
        group = QGroupBox("CREATE NEW TASK")
        form = QVBoxLayout()
        for key, label in [("id", "Task ID:"), ("speed", "Speed:"), ("text", "Text:"),
                           ("type", "Type:"), ("variables", "Variables:"), ("var_indices", "Variable indexes:")]:
            form.addWidget(QLabel(label))
            form.addWidget(self.new_file_data[key])
        group.setLayout(form)
        layout.addWidget(group)

        self.generate_empty_table()

    def generate_empty_table(self, from_spinbox=False, from_varmask=False):
        if from_spinbox:
            num_vars = self.new_file_data["variables"].value()
            var_mask = (1 << num_vars) - 1
        elif from_varmask:
            indices = [int(i.strip()) for i in self.new_file_data["var_indices"].text().split(",") if i.strip().isdigit()]
            var_mask = sum((1 << i) for i in indices if 0 <= i < 16)
            num_vars = len(indices)
            self.new_file_data["variables"].blockSignals(True)
            self.new_file_data["variables"].setValue(num_vars)
            self.new_file_data["variables"].blockSignals(False)
        else:
            func = self.functions[self.current_index]
            if func:
                num_vars = func.num_vars
                var_mask = func.var_mask
                self.new_file_data["var_indices"].setText(",".join(str(i) for i in range(16) if (var_mask >> i) & 1))
            else:
                num_vars, var_mask = 1, 0b1
                self.new_file_data["variables"].setValue(1)

        num_rows = 1 << num_vars
        self.table.setRowCount(num_rows)
        self.table.setColumnCount(num_vars + 1)

        # Заголовки
        headers = [f"X{i}" for i in range(16) if (var_mask >> i) & 1][:num_vars] + ["Result"]
        self.table.setHorizontalHeaderLabels(headers)

        # Данные (если были сохранены)
        bit_data = [0] * num_rows
        func = self.functions[self.current_index]
        if func and func.num_vars == num_vars:
            for i in range(num_rows):
                bit_data[i] = (func.bit_vector[i >> 3] >> (i % 8)) & 1

        for i in range(num_rows):
            for j in range(num_vars):
                item = QTableWidgetItem(str((i >> (num_vars - j - 1)) & 1))
                item.setTextAlignment(Qt.AlignCenter)
                self.table.setItem(i, j, item)
            result = QTableWidgetItem(str(bit_data[i]))
            result.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(i, num_vars, result)

        self.table_label.setText(f"Table {self.current_index + 1} (edit mode)")
        self.sub_label.setText("Editable truth table")

    def regenerate_table_by_spinbox(self):
        self.save_current_function()
        self.generate_empty_table(from_spinbox=True)

    def regenerate_table_by_varmask(self):
        self.save_current_function()
        self.generate_empty_table(from_varmask=True)

    def save_current_function(self):
        if not self.setup_mode:
            return

        num_vars = self.new_file_data["variables"].value()
        num_rows = 1 << num_vars
        bit_vector = bytearray((num_rows + 7) // 8)
        for i in range(num_rows):
            item = self.table.item(i, num_vars)
            if item and item.text().strip() == "1":
                bit_vector[i >> 3] |= (1 << (i % 8))

        indices = [int(i.strip()) for i in self.new_file_data["var_indices"].text().split(",") if i.strip().isdigit()]
        var_mask = sum((1 << i) for i in indices if 0 <= i < 16)
        func = write.add_Func(self.current_index, num_vars, bytes(bit_vector), var_mask)
        self.functions[self.current_index] = func

    def next_table(self):
        if self.setup_mode and self.current_index < 15:
            self.save_current_function()
            self.current_index += 1
            self.generate_empty_table()
        elif not self.setup_mode and self.current_index < len(self.functions) - 1:
            self.current_index += 1
            self.update_table()

    def prev_table(self):
        if self.setup_mode and self.current_index > 0:
            self.save_current_function()
            self.current_index -= 1
            self.generate_empty_table()
        elif not self.setup_mode and self.current_index > 0:
            self.current_index -= 1
            self.update_table()

    def open_file(self):
        if self.setup_mode:
            self.setup_mode = False
            self.init_ui()
        file_path, _ = QFileDialog.getOpenFileName(self, "Open Binary File", "", "*.bin")
        if file_path:
            bin_file = pars.parse_bin_file(file_path)
            self.functions = bin_file.functions[:bin_file.function_count]
            self.label_id.setText(f"№: {bin_file.id}")
            self.label_type.setText(f"Type: {self.types_name.get(bin_file.type, '-')}")
            self.label_speed.setText(f"Speed: {bin_file.speed}")
            self.task_text.setText(bin_file.text or "")
            self.current_index = 0
            self.update_table()

    def update_table(self):
        func = self.functions[self.current_index]
        num_rows = 1 << func.num_vars
        self.table.setRowCount(num_rows)
        self.table.setColumnCount(func.num_vars + 1)

        headers = [f"X{i}" for i in range(16) if (func.var_mask >> i) & 1][:func.num_vars] + ["Result"]
        self.table.setHorizontalHeaderLabels(headers)

        for i in range(num_rows):
            for j in range(func.num_vars):
                val = (i >> (func.num_vars - j - 1)) & 1
                item = QTableWidgetItem(str(val))
                item.setTextAlignment(Qt.AlignCenter)
                item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
                self.table.setItem(i, j, item)
            res = (func.bit_vector[i >> 3] >> (i % 8)) & 1
            result_item = QTableWidgetItem(str(res))
            result_item.setTextAlignment(Qt.AlignCenter)
            result_item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
            self.table.setItem(i, func.num_vars, result_item)

        self.table_label.setText(f"Table {self.current_index + 1}")
        self.sub_label.setText(f"Truth Table #{func.name_func} | Variables: {func.num_vars}")
        
    def save_to_file(self):
        if not self.setup_mode:
            return

        self.save_current_function()

        bin_file = write.BinFile()
        try:
            bin_file.id = int(self.new_file_data["id"].text())
            bin_file.speed = int(self.new_file_data["speed"].text())
            bin_file.text = self.new_file_data["text"].toPlainText()
            bin_file.type = self.new_file_data["type"].currentIndex()
        except ValueError:
            print("Ошибка: неверные данные в полях ID, SPEED и т.д.")
            return

        bin_file.function_count = 0
        for func in self.functions:
            if func:
                bin_file.functions[bin_file.function_count] = func
                bin_file.function_count += 1

        path, _ = QFileDialog.getSaveFileName(self, "Save Binary File", "", "Binary Files (*.bin)")
        if path:
            write.generate_bin_file(path, bin_file)
            print(f"Файл сохранён: {path}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(13, 13, 26))
    palette.setColor(QPalette.WindowText, QColor(0, 255, 153))
    app.setPalette(palette)
    window = PixelLogicViewer()
    window.show()
    sys.exit(app.exec_())
