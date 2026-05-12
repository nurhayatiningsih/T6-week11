# ============================================================
# Nama  : Nurhayati Ningsih
# NIM   : F1D02410085
# Kelas : Pemvis C
# ============================================================
import sys
from PySide6.QtCore import QThread, QTimer, Qt
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QTableWidget, QTableWidgetItem,
    QTextEdit, QSplitter, QHeaderView, QMessageBox, QDialog
)
from dialogs import PostDialog
from api_worker import ApiWorker

class WorkerThread(QThread):
    def __init__(self, worker):
        super().__init__()
        self.worker = worker

    def run(self):
        self.worker.run()

class PostManagerApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Post Manager")
        self.setGeometry(80, 80, 1200, 700)
        self.setMinimumSize(900, 550)

        self.posts_data = []
        self._is_loading = False
        self._detail_req_id = 0
        self._threads_to_cleanup = [] # Simpan thread agar tidak hilang

        self.setup_ui()
        self.fetch_posts()

    def setup_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(8)

        self.status_label = QLabel("Ready")
        self.status_label.setStyleSheet("font-weight: bold; padding: 6px; background: #ecf0f1; border-radius: 4px;")
        main_layout.addWidget(self.status_label)

        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(8)
        self.btn_refresh = QPushButton("Refresh")
        self.btn_tambah  = QPushButton("Tambah Post")
        self.btn_edit    = QPushButton("Edit")
        self.btn_hapus   = QPushButton("Hapus")

        for btn in [self.btn_refresh, self.btn_tambah, self.btn_edit, self.btn_hapus]:
            btn.setMinimumHeight(36)
            btn_layout.addWidget(btn)
        main_layout.addLayout(btn_layout)

        splitter = QSplitter(Qt.Horizontal)
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["ID", "Title", "Author", "Status"])
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.SingleSelection)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setAlternatingRowColors(True)
        self.table.verticalHeader().setVisible(False)

        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        splitter.addWidget(self.table)

        self.detail = QTextEdit()
        self.detail.setReadOnly(True)
        self.detail.setStyleSheet("QTextEdit { background: #f8f9fa; font-size: 13px; padding: 8px; }")
        splitter.addWidget(self.detail)
        splitter.setSizes([500, 500])
        main_layout.addWidget(splitter, stretch=1)

        self.btn_refresh.clicked.connect(self.fetch_posts)
        self.btn_tambah.clicked.connect(self.add_post)
        self.btn_edit.clicked.connect(self.edit_post)
        self.btn_hapus.clicked.connect(self.delete_post)
        self.table.currentCellChanged.connect(self.on_row_selected)

        self.btn_edit.setEnabled(False)
        self.btn_hapus.setEnabled(False)

    def set_state(self, state, msg=""):
        if state == "loading":
            self._is_loading = True
            self.status_label.setText("Loading...")
            self.status_label.setStyleSheet("font-weight:bold; padding:6px; color:#2c3e50; background:#d4e6f1; border-radius:4px;")
        elif state == "success":
            self._is_loading = False
            self.status_label.setText(msg)
            self.status_label.setStyleSheet("font-weight:bold; padding:6px; color:#1e8449; background:#d5f5e3; border-radius:4px;")
        elif state == "error":
            self._is_loading = False
            self.status_label.setText(f"Error: {msg}")
            self.status_label.setStyleSheet("font-weight:bold; padding:6px; color:#c0392b; background:#fadbd8; border-radius:4px;")
        elif state == "empty":
            self._is_loading = False
            self.status_label.setText("Tidak ada data ditemukan")
            self.status_label.setStyleSheet("font-weight:bold; padding:6px; color:#b7950b; background:#fef9e7; border-radius:4px;")
        
        self._update_button_states()

    def _update_button_states(self):
        has_selection = self.table.currentRow() >= 0
        self.btn_refresh.setEnabled(not self._is_loading)
        self.btn_tambah.setEnabled(not self._is_loading)
        self.btn_edit.setEnabled(not self._is_loading and has_selection)
        self.btn_hapus.setEnabled(not self._is_loading and has_selection)

    def _run_worker(self, worker, on_success, on_error=None):
        # 1. Hubungkan Signal dari Worker ke UI
        worker.success.connect(on_success)
        if on_error:
            worker.error.connect(on_error)
        else:
            worker.error.connect(self.on_error)

        # 2. Bungkus Worker ke dalam QThread 
        thread = WorkerThread(worker)
        
        # 3. Simpan referensi thread agar tidak dihapus oleh Python sampai selesai
        self._threads_to_cleanup.append(thread)
        
        # 4. Bersihkan memori setelah thread selesai
        thread.finished.connect(lambda: self._cleanup_thread(thread))
        
        # 5. Mulai thread!
        thread.start()

    def _cleanup_thread(self, thread):
        if thread in self._threads_to_cleanup:
            self._threads_to_cleanup.remove(thread)
        thread.deleteLater()

    def on_error(self, message):
        self.set_state("error", message)
        QMessageBox.critical(self, "API Error", message)

    # =================
    # CRUD — GET ALL
    # =================
    def fetch_posts(self):
        self.set_state("loading")
        worker = ApiWorker("get_posts")
        self._run_worker(worker, self.on_posts_loaded)

    def on_posts_loaded(self, posts):
        self.posts_data = posts
        self.table.setRowCount(0)
        if len(posts) == 0:
            self.set_state("empty")
            return
        for p in self.posts_data:
            row = self.table.rowCount()
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(str(p.get("id", ""))))
            self.table.setItem(row, 1, QTableWidgetItem(p.get("title", "")))
            self.table.setItem(row, 2, QTableWidgetItem(p.get("author", "")))
            self.table.setItem(row, 3, QTableWidgetItem(p.get("status", "")))
        self.set_state("success", f"{len(posts)} posts dimuat")
    # =============================================
    # DETAIL — GET BY ID (DENGAN ANIMASI LOADING)
    # =============================================
    def on_row_selected(self, row, _col, _prev_row, _prev_col):
        self._update_button_states()
        if row < 0 or row >= len(self.posts_data):
            return

        post_id = self.posts_data[row]["id"]
        p = self.posts_data[row]
        
        self.detail.setStyleSheet("QTextEdit { background: #f8f9fa; font-size: 13px; padding: 8px; color: #555; font-style: italic; }")
        self.detail.setPlainText(
            f"ID     : {p.get('id', '-')}\nTitle  : {p.get('title', '-')}\n"
            f"Author : {p.get('author', '-')}\nSlug   : {p.get('slug', '-')}\n"
            f"Status : {p.get('status', '-')}\n\nMemuat comments"
        )

        self._detail_req_id += 1
        current_req_id = self._detail_req_id
        self._animate_loading(current_req_id)

        worker = ApiWorker("get_post", post_id=post_id)
        self._run_worker(
            worker, 
            lambda data, rid=current_req_id: self._on_detail_loaded(data, rid),
            on_error=self._on_detail_error
        )

    def _animate_loading(self, req_id):
        if req_id != self._detail_req_id: return
        text = self.detail.toPlainText()
        if "Memuat comments" in text:
            base_text = "Memuat comments"
            current_dots = text.replace(base_text, "").strip()
            dot_count = len(current_dots)
            new_dots = "." * ((dot_count % 4) + 1)
            self.detail.setPlainText(text.split("Memuat comments")[0] + base_text + new_dots)
            QTimer.singleShot(400, lambda: self._animate_loading(req_id))

    def _on_detail_loaded(self, post, request_id):
        if request_id != self._detail_req_id: return
        
        self.detail.setStyleSheet("QTextEdit { background: #f8f9fa; font-size: 13px; padding: 8px; }")
        lines = [
            f"ID     : {post.get('id', '-')}", f"Title  : {post.get('title', '-')}",
            f"Author : {post.get('author', '-')}", f"Slug   : {post.get('slug', '-')}",
            f"Status : {post.get('status', '-')}", "", "-" * 45, "BODY:", "-" * 45,
            post.get("body", "-"),
        ]
        comments = post.get("comments", [])
        if comments:
            lines += ["", "-" * 45, f"COMMENTS ({len(comments)}):", "-" * 45]
            for idx, c in enumerate(comments, 1):
                lines.append(f"  {idx}. [{c.get('id', '-')}] {c.get('body', '-')}")
        else:
            lines += ["", "-" * 45, "COMMENTS (0):", "-" * 45, "  Tidak ada komentar."]
            
        self.detail.setPlainText("\n".join(lines))

    def _on_detail_error(self, message):
        self.detail.setStyleSheet("QTextEdit { background: #f8f9fa; font-size: 13px; padding: 8px; color: #c0392b; }")
        self.detail.setPlainText(f"Gagal memuat detail:\n{message}")

    # =======================
    # CRUD — POST (Tambah)
    # =======================
    def add_post(self):
        dialog = PostDialog(self)
        if dialog.exec() == QDialog.Accepted:
            data = dialog.get_data()
            required = {"title": "Title", "body": "Body", "author": "Author", "slug": "Slug"}
            for key, label in required.items():
                if not data[key]:
                    QMessageBox.warning(self, "Validasi Gagal", f"Field '{label}' wajib diisi!")
                    return
            worker = ApiWorker("create_post", payload=data)
            self._run_worker(worker, self.on_post_created)

    def on_post_created(self, result):
        new_id = result.get("data", {}).get("id", "-")
        QMessageBox.information(self, "Sukses", f"Post berhasil ditambahkan!\n\nID baru: {new_id}")
        self.fetch_posts()

    # ==================
    # CRUD — PUT (Edit)
    # ==================
    def edit_post(self):
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Peringatan", "Pilih post terlebih dahulu!")
            return
        post = self.posts_data[row]
        dialog = PostDialog(self, post)
        if dialog.exec() == QDialog.Accepted:
            data = dialog.get_data()
            required = {"title": "Title", "body": "Body", "author": "Author", "slug": "Slug"}
            for key, label in required.items():
                if not data[key]:
                    QMessageBox.warning(self, "Validasi Gagal", f"Field '{label}' wajib diisi!")
                    return
            worker = ApiWorker("update_post", post_id=post["id"], payload=data)
            self._run_worker(worker, self.on_post_updated)

    def on_post_updated(self, result):
        QMessageBox.information(self, "Sukses", "Post berhasil diperbarui!")
        self.fetch_posts()

    # ======================
    # CRUD — DELETE (Hapus)
    # ======================
    def delete_post(self):
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Peringatan", "Pilih post terlebih dahulu!")
            return
        post_id = self.posts_data[row]["id"]
        post_title = self.posts_data[row].get("title", "-")
        reply = QMessageBox.question(
            self, "Konfirmasi Hapus",
            f"Yakin ingin menghapus post berikut?\n\nID    : {post_id}\nTitle : {post_title}\n\nSemua comments pada post ini juga akan ikut terhapus (cascade delete).",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            worker = ApiWorker("delete_post", post_id=post_id)
            self._run_worker(worker, self.on_post_deleted)

    def on_post_deleted(self, result):
        QMessageBox.information(self, "Sukses", "Post berhasil dihapus!")
        self.detail.setPlainText("Pilih post dari tabel untuk melihat detail lengkap.")
        self.table.clearSelection()
        self.btn_edit.setEnabled(False)
        self.btn_hapus.setEnabled(False)
        self.fetch_posts()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PostManagerApp()
    window.show()
    sys.exit(app.exec())