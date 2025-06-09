import sys
import os
import pars
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGroupBox,
    QLabel, QTextEdit, QTableWidget, QTableWidgetItem, QPushButton, QFileDialog, QSplitter
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QColor, QPalette


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
        self.functions = []
        self.current_index = 0
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

    def open_file(self):
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
                self.table.setItem(i, j, QTableWidgetItem(str(bit)))

            # result_bit = (func.bit_vector[i >> 3] >> (7 - (i % 8))) & 0x01
            result_bit = (func.bit_vector[i >> 3] >> (i % 8)) & 0x01
            item = QTableWidgetItem(str(result_bit))
            item.setForeground(QColor("#FF69B4"))
            self.table.setItem(i, func.num_vars, item)

            for j in range(func.num_vars + 1):
                self.table.item(i, j).setTextAlignment(Qt.AlignCenter)

        self.table_label.setText(f"Table {self.current_index + 1}")
        self.sub_label.setText(f"Truth Table #{func.name_func} | Variables: {func.num_vars}")

    def next_table(self):
        if self.current_index < len(self.functions) - 1:
            self.current_index += 1
            self.update_table()

    def prev_table(self):
        if self.current_index > 0:
            self.current_index -= 1
            self.update_table()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    dark_palette = QPalette()
    dark_palette.setColor(QPalette.Window, QColor(13, 13, 26))
    dark_palette.setColor(QPalette.WindowText, QColor(0, 255, 153))
    app.setPalette(dark_palette)

    viewer = PixelLogicViewer()
    viewer.show()
    sys.exit(app.exec_())
