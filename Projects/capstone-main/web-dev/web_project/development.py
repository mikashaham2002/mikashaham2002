import base64
from .secrets import SECRET_KEY

SECRET_KEY = base64.b64decode(SECRET_KEY).decode()
DATABASES = {}
DEBUG = True
ALLOWED_HOSTS = ["localhost", "127.0.0.1"]
