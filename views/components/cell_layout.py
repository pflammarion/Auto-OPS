from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QVBoxLayout, QLineEdit, QListWidget, QPushButton, QWidget, QLabel, QHBoxLayout


class CellLayout(QWidget):
    def __init__(self, items):
        super().__init__()

        self.cell_name = None
        self.layout = None
        self.cell_button = None
        self.listWidget = None
        self.filterLineEdit = None
        self.items = items
        self.filtered_items = items.copy()

        self.state_list = QLineEdit(self)
        self.state_list.setPlaceholderText("Enter inputs states")

        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        self.filterLineEdit = QLineEdit(self)
        self.filterLineEdit.setPlaceholderText("Enter Cell Name")

        self.listWidget = QListWidget(self)
        self.listWidget.addItems(self.items)
        self.listWidget.setFixedHeight(100)

        state_list_label = QLabel("State list:", self)
        line2 = QHBoxLayout()
        line2.addWidget(state_list_label)
        line2.addWidget(self.state_list)

        self.cell_button = QPushButton("Update cell", self)
        self.cell_button.setCursor(Qt.CursorShape.PointingHandCursor)

        layout.addWidget(self.filterLineEdit)
        layout.addWidget(self.listWidget)
        layout.addLayout(line2)
        layout.addWidget(self.cell_button)

        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        layout.setSpacing(20)

        self.layout = layout

    def get_layout(self):
        return self.layout

    def filter_items(self):
        filter_text = self.filterLineEdit.text().lower()
        self.filtered_items = [item for item in self.items if filter_text in item.lower()]
        self.update_list_widget()

    def update_list_widget(self):
        self.listWidget.clear()
        self.listWidget.addItems(self.filtered_items)

    def get_cell_name(self):
        selected_items = self.listWidget.selectedItems()
        if selected_items:
            return selected_items[0].text()
        else:
            return self.filterLineEdit.text()

    def get_state_list(self):
        return self.state_list.text()

    def set_cell_name(self, value):
        if self.filterLineEdit is not None:
            self.filterLineEdit.setText(value)

    def set_state_list(self, value):
        if self.state_list is not None:
            self.state_list.setText(value)
