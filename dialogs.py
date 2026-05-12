# ============================================================
# Nama  : Nurhayati Ningsih
# NIM   : F1D02410085
# Kelas : Pemvis C
# ============================================================
from PySide6.QtWidgets import QDialog, QVBoxLayout, QFormLayout, QDialogButtonBox, QLineEdit, QTextEdit, QComboBox

class PostDialog(QDialog):
    def __init__(self, parent=None, post=None):
        super().__init__(parent)
        self.setWindowTitle("Form Post" if not post else "Edit Post")
        self.setMinimumWidth(400)
        
        layout = QVBoxLayout(self)
        form = QFormLayout()
        
        self.title_in = QLineEdit()
        self.body_in = QTextEdit()
        self.author_in = QLineEdit()
        self.slug_in = QLineEdit()
        self.status_in = QComboBox()
        self.status_in.addItems(["draft", "published"])
        
        form.addRow("Title:", self.title_in)
        form.addRow("Body:", self.body_in)
        form.addRow("Author:", self.author_in)
        form.addRow("Slug:", self.slug_in)
        form.addRow("Status:", self.status_in)
        layout.addLayout(form)
        
        if post:
            self.title_in.setText(str(post.get('title', '')))
            self.body_in.setPlainText(str(post.get('body', '')))
            self.author_in.setText(str(post.get('author', '')))
            self.slug_in.setText(str(post.get('slug', '')))
            self.status_in.setCurrentText(post.get('status', 'draft'))
            
        btn = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        btn.accepted.connect(self.accept)
        btn.rejected.connect(self.reject)
        layout.addWidget(btn)
        
    def get_data(self):
        return {
            "title": self.title_in.text().strip(),
            "body": self.body_in.toPlainText().strip(),
            "author": self.author_in.text().strip(),
            "slug": self.slug_in.text().strip(),
            "status": self.status_in.currentText()
        }