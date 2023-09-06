import shutil

from PyQt6.QtWidgets import QPushButton, QFileDialog


class Controller:
    def __init__(self, view):
        self.view = view

    def upload_image(self):
        file_dialog = QFileDialog()
        file_dialog.setFileMode(QFileDialog.FileMode.ExistingFiles)
        file_dialog.setNameFilter("Images (*.png *.jpg *.jpeg *.bmp *.gif)")

        if file_dialog.exec():
            selected_files = file_dialog.selectedFiles()
            if selected_files:
                source_file = selected_files[0]  # Assuming only one file is selected
                destination_folder = "resources/"  # Change this to your resource folder path
                shutil.copy(source_file, destination_folder)
                print("Image uploaded")

    def button_add_clicked(self):
        print("this is working")
        # Handle button 1 click event here
        pass

    def button2_clicked(self):
        # Handle button 2 click event here
        pass
