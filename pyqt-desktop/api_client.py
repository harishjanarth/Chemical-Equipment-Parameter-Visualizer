import requests
import os
import json

TOKEN_STORE = os.path.expanduser("~/.cepv_token.json")

class APIClient:
    def __init__(self, base_url: str):
        if not base_url.endswith("/"):
            base_url += "/"
        self.base = base_url + "api/"
        self.token = None
        self._load_token()

  
    def _load_token(self):
        try:
            if os.path.exists(TOKEN_STORE):
                with open(TOKEN_STORE, "r") as f:
                    data = json.load(f)
                    self.token = data.get("token")
        except Exception:
            self.token = None

    def _save_token(self):
        try:
            with open(TOKEN_STORE, "w") as f:
                json.dump({"token": self.token}, f)
        except Exception:
            pass

    def set_token(self, token: str):
        self.token = token
        self._save_token()

    
    def _headers(self, json_body=False):
        h = {"Accept": "application/json"}
        if json_body:
            h["Content-Type"] = "application/json"
        if self.token:
            h["Authorization"] = f"Bearer {self.token}"
        return h

   
    def register(self, username, password):
        url = self.base + "auth/register/"
        payload = {"username": username, "password": password}
        res = requests.post(url, json=payload, headers=self._headers(json_body=True))
        try:
            data = res.json()
        except Exception:
            res.raise_for_status()
        if res.status_code != 200 and res.status_code != 201:
            raise Exception(data.get("error", f"Registration failed ({res.status_code})"))
        return data

   
    def login(self, username, password):
        url = self.base + "auth/login/"
        payload = {"username": username, "password": password}
        res = requests.post(url, json=payload, headers=self._headers(json_body=True))
        try:
            data = res.json()
        except Exception:
            res.raise_for_status()
        if res.status_code != 200:
            raise Exception(data.get("error", f"Login failed ({res.status_code})"))
        self.token = data.get("token")
        self._save_token()
        return data

    def upload_csv(self, file_path):
        url = self.base + "upload/"
        if not self.token:
            raise Exception("Not logged in")
        with open(file_path, "rb") as f:
            files = {"file": (os.path.basename(file_path), f, "text/csv")}
            headers = {"Authorization": f"Bearer {self.token}"}
            res = requests.post(url, files=files, headers=headers)
        try:
            data = res.json()
        except Exception:
            res.raise_for_status()
        if res.status_code != 200:
            raise Exception(data.get("error", f"Upload failed ({res.status_code})"))
        return data

    def get_summary(self):
        url = self.base + "summary/"
        res = requests.get(url, headers=self._headers())
        try:
            data = res.json()
        except Exception:
            res.raise_for_status()
        if res.status_code != 200:
            raise Exception(data.get("error", f"Summary load failed ({res.status_code})"))
        return data

    def get_history(self):
        url = self.base + "history/"
        res = requests.get(url, headers=self._headers())
        try:
            data = res.json()
        except Exception:
            res.raise_for_status()
        if res.status_code != 200:
            raise Exception(data.get("error", f"History load failed ({res.status_code})"))
        return data

    def get_dataset_rows(self, dataset_id):
        url = self.base + f"dataset/{dataset_id}/data/"
        res = requests.get(url, headers=self._headers())
        try:
            data = res.json()
        except Exception:
            res.raise_for_status()
        if res.status_code != 200:
            raise Exception(data.get("error", f"Dataset rows load failed ({res.status_code})"))
        return data

   
    def download_pdf(self, dataset_id, save_path):
        url = self.base + f"generate_pdf/{dataset_id}/"
        headers = {"Authorization": f"Bearer {self.token}"} if self.token else {}
        res = requests.get(url, headers=headers, stream=True)
        if res.status_code != 200:
            try:
                data = res.json()
                msg = data.get("error", "PDF download failed")
            except Exception:
                msg = f"PDF download failed ({res.status_code})"
            raise Exception(msg)
        with open(save_path, "wb") as f:
            for chunk in res.iter_content(1024):
                f.write(chunk)
        return save_path
