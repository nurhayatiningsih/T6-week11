# ============================================================
# Nama  : Nurhayati Ningsih
# NIM   : F1D02410085
# Kelas : Pemvis C
# ============================================================
import requests
from PySide6.QtCore import QObject, Signal
from api_service import ApiService

class ApiWorker(QObject):
    finished = Signal()
    success = Signal(object)
    error = Signal(str)

    def __init__(self, action, post_id=None, payload=None):
        super().__init__()
        self.action = action
        self.post_id = post_id
        self.payload = payload
        self.service = ApiService()

    def run(self):
        try:
            if self.action == "get_posts":
                result = self.service.get_posts()
            elif self.action == "get_post":
                result = self.service.get_post(self.post_id)
            elif self.action == "create_post":
                result = self.service.create_post(self.payload)
            elif self.action == "update_post":
                result = self.service.update_post(self.post_id, self.payload)
            elif self.action == "delete_post":
                result = self.service.delete_post(self.post_id)
            else:
                raise ValueError(f"Action tidak dikenali: {self.action}")
            
            self.success.emit(result)
            
        except requests.exceptions.HTTPError as e:
            if e.response is not None and e.response.status_code == 422:
                try:
                    err_data = e.response.json()
                    pesan = []
                    if "message" in err_data: pesan.append(err_data["message"])
                    if "errors" in err_data:
                        for field, m in err_data["errors"].items():
                            if isinstance(m, list): pesan.append(f"{field}: {', '.join(m)}")
                            else: pesan.append(f"{field}: {m}")
                    self.error.emit("\n".join(pesan) if pesan else str(e))
                except Exception: self.error.emit(str(e))
            else: self.error.emit(str(e))
        except Exception as e: self.error.emit(str(e))
        finally: self.finished.emit()