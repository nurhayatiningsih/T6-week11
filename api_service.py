# ============================================================
# Nama  : Nurhayati Ningsih
# NIM   : F1D02410085
# Kelas : Pemvis C
# ============================================================
import requests

class ApiService:
    BASE_URL = "https://api.pahrul.my.id/api"
    TIMEOUT = 10

    def get_posts(self):
        r = requests.get(f"{self.BASE_URL}/posts", timeout=self.TIMEOUT)
        r.raise_for_status()
        return r.json().get("data", [])

    def get_post(self, post_id):
        r = requests.get(f"{self.BASE_URL}/posts/{post_id}", timeout=self.TIMEOUT)
        r.raise_for_status()
        return r.json().get("data")

    def create_post(self, payload):
        r = requests.post(f"{self.BASE_URL}/posts", json=payload, timeout=self.TIMEOUT)
        r.raise_for_status()
        return r.json()

    def update_post(self, post_id, payload):
        r = requests.put(f"{self.BASE_URL}/posts/{post_id}", json=payload, timeout=self.TIMEOUT)
        r.raise_for_status()
        return r.json()

    def delete_post(self, post_id):
        r = requests.delete(f"{self.BASE_URL}/posts/{post_id}", timeout=self.TIMEOUT)
        r.raise_for_status()
        return True