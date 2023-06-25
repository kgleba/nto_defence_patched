from .section import Section
from datetime import datetime
from base64 import b64encode, b64decode
import requests
import json


class TimeoutHTTPAdapter(requests.adapters.HTTPAdapter):
    def send(self, *args, **kwargs) -> requests.Response:
        kwargs['timeout'] = 2
        return super().send(*args, **kwargs)


class ServerRoom(Section):
    def __init__(self):
        super().__init__('ServerRoom')
        self.backup_url = ''
        self.backup_date = ''
        self.data = {}
        self._session = requests.Session()
        self._session.mount('https://', TimeoutHTTPAdapter(max_retries=2))
        self._session.mount('http://', TimeoutHTTPAdapter(max_retries=2))
        self._session.verify = False

    def set_backup_url(self, url: str):
        self.backup_url = url

    def get_backup_url(self):
        return self.backup_url

    def backup(self):
        self.backup_date = str(datetime.now())

    def update_data(self, data: str):
        self.data = json.loads(b64decode(data))

    def send_backup(self):
        if '127.0.0.1' in self.backup_url or 'localhost' in self.backup_url:
            return False
        try:
            answer = self._session.post(self.backup_url, json=self.data)
            return answer.json()
        except Exception as e:
            print(e, flush=True)
            return False

    def full_clean(self):
        self.data = {}

    def get_backup_date(self):
        return self.backup_date
