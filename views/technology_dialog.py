from PyQt5.QtWidgets import QDialog, QLabel, QPushButton, QVBoxLayout, QFileDialog

class TechnologySelectionDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Select technology files")
        self.setFixedSize(400, 200)

        self.label1 = QLabel("GDS library file:")
        self.import_button1 = QPushButton("Import GDS file")
        self.import_button1.clicked.connect(self.import_gds_file)

        self.label2 = QLabel("Liberty library file:")
        self.import_button2 = QPushButton("Import Liberty file")
        self.import_button2.clicked.connect(self.import_liberty_file)

        self.ok_button = QPushButton("OK")
        self.ok_button.clicked.connect(self.accept)
        self.ok_button.setEnabled(False)

        layout = QVBoxLayout()
        layout.addWidget(self.label1)
        layout.addWidget(self.import_button1)
        layout.addWidget(self.label2)
        layout.addWidget(self.import_button2)
        layout.addWidget(self.ok_button)

        self.setLayout(layout)

    def import_gds_file(self):
        gds_file, gds_filter = QFileDialog.getOpenFileName(self, "Select GDS library file", "", "GDS files (*.gds);;All Files (*)")
        if gds_file:
            self.label1.setText(f"GDS library file: {gds_file}")
            self.check_files_selected()

    def import_liberty_file(self):
        liberty_file, liberty_filter = QFileDialog.getOpenFileName(self, "Select Liberty library file", "", "Liberty files (*.lib);;All Files (*)")
        if liberty_file:
            self.label2.setText(f"Liberty library file: {liberty_file}")
            self.check_files_selected()

    def check_files_selected(self):
        gds_selected = "GDS library file:" in self.label1.text()
        liberty_selected = "Liberty library file:" in self.label2.text()
        self.ok_button.setEnabled(gds_selected and liberty_selected)

    def get_selected_technology(self):
        return (
            self.label1.text().replace("GDS library file: ", ""),
            self.label2.text().replace("Liberty library file: ", "")
        )
