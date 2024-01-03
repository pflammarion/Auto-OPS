from PyQt5.QtWidgets import QDialog, QLabel, QComboBox, QPushButton, QVBoxLayout


class ColumnSelectionDialog(QDialog):
    def __init__(self, column_names, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Select Columns")

        self.column_names = column_names

        self.label1 = QLabel("Select time column:")
        self.column_combo1 = QComboBox()
        self.column_combo1.addItems(column_names)

        self.label2 = QLabel("Select voltage column:")
        self.column_combo2 = QComboBox()
        self.column_combo2.addItems(column_names)
        self.column_combo2.setCurrentIndex(1)

        self.ok_button = QPushButton("OK")
        self.ok_button.clicked.connect(self.accept)

        layout = QVBoxLayout()
        layout.addWidget(self.label1)
        layout.addWidget(self.column_combo1)
        layout.addWidget(self.label2)
        layout.addWidget(self.column_combo2)
        layout.addWidget(self.ok_button)

        self.setLayout(layout)

    def get_selected_columns(self):
        return (
            self.column_combo1.currentText(),
            self.column_combo2.currentText()
        )
