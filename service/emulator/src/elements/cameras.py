from .controller import Controller
from base64 import b64encode


class Cameras(Controller):
    def __init__(self):
        super().__init__('Cameras')

    def get_image(self):
        if self.enabled:
            with open('static/cameras_enabled.jpg', 'rb') as f:
                image = f.read()
            return b64encode(image).decode()
        else:
            with open('static/cameras.jpg', 'rb') as f:
                image = f.read()
            return b64encode(image).decode()
