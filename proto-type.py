import os
import sys

from PIL import Image
from PIL.ExifTags import TAGS
from PySide2.QtCore import Qt
from PySide2.QtGui import QDragEnterEvent, QDropEvent, QPixmap
from PySide2.QtWidgets import QApplication, QWidget, QLabel, QPushButton, QVBoxLayout, QTextEdit, QListWidget


def get_metadata(image_path):
    try:
        img = Image.open(image_path)
        exif_data = img._getexif()
        metadata = {}
        if exif_data:
            for tag, value in exif_data.items():
                decoded = TAGS.get(tag, tag)
                metadata[decoded] = value
        return metadata
    except Exception as e:
        return {"Error": str(e)}

def remove_metadata(image_path, output_path):
    try:
        img = Image.open(image_path)
        img.save(output_path, "jpeg")  # Saves without EXIF data
        return True
    except Exception as e:
        return str(e)

class ImageMetadataViewer(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Image Metadata Viewer")
        self.setGeometry(100, 100, 600, 500)
        self.setAcceptDrops(True)

        self.image_list = QListWidget()
        self.image_label = QLabel(self)
        self.image_label.setAlignment(Qt.AlignCenter)
        self.label = QLabel("Drag & Drop Images Here", self)
        self.label.setAlignment(Qt.AlignCenter)
        self.metadata_list = QListWidget()
        self.text_edit = QTextEdit()
        self.text_edit.setReadOnly(True)
        self.clear_metadata_btn = QPushButton("Remove Metadata")
        self.clear_metadata_btn.setEnabled(False)
        self.clear_metadata_btn.clicked.connect(self.remove_metadata)

        layout = QVBoxLayout()
        layout.addWidget(self.label)
        layout.addWidget(self.image_list)
        layout.addWidget(self.image_label)
        layout.addWidget(self.metadata_list)
        layout.addWidget(self.text_edit)
        layout.addWidget(self.clear_metadata_btn)
        self.setLayout(layout)

        self.image_list.itemClicked.connect(self.load_selected_image)
        self.metadata_list.itemClicked.connect(self.show_selected_metadata)
        self.image_paths = []

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event: QDropEvent):
        urls = event.mimeData().urls()
        for url in urls:
            file_path = url.toLocalFile()
            if file_path.lower().endswith((".jpg", ".jpeg", ".png")):
                self.image_paths.append(file_path)
                self.image_list.addItem(os.path.basename(file_path))
        self.label.setText("Images Loaded")

    def load_selected_image(self):
        selected_item = self.image_list.currentItem()
        if selected_item:
            selected_image = selected_item.text()
            for path in self.image_paths:
                if os.path.basename(path) == selected_image:
                    self.display_image(path)
                    self.load_metadata(path)
                    break

    def display_image(self, image_path):
        pixmap = QPixmap(image_path)
        self.image_label.setPixmap(pixmap.scaled(200, 200, Qt.KeepAspectRatio))
        self.clear_metadata_btn.setEnabled(True)

    def load_metadata(self, image_path):
        metadata = get_metadata(image_path)
        self.metadata_list.clear()
        self.text_edit.clear()
        for key in metadata.keys():
            self.metadata_list.addItem(key)
        self.text_edit.setText("\n".join(f"{k}: {v}" for k, v in metadata.items()))
        self.selected_image_path = image_path

    def show_selected_metadata(self):
        selected_item = self.metadata_list.currentItem()
        if selected_item and self.selected_image_path:
            metadata = get_metadata(self.selected_image_path)
            key = selected_item.text()
            self.text_edit.setText(f"{key}: {metadata.get(key, 'No data')}")

    def remove_metadata(self):
        if self.selected_image_path:
            output_path = self.selected_image_path.replace(".jpg", "_clean.jpg").replace(".jpeg", "_clean.jpeg").replace(".png", "_clean.png")
            success = remove_metadata(self.selected_image_path, output_path)
            if success is True:
                self.text_edit.append(f"\nMetadata removed! Saved as {output_path}")
            else:
                self.text_edit.append(f"\nError: {success}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ImageMetadataViewer()
    window.show()
    sys(app.exec_())
