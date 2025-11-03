import base64
from .secrets import SECRET_KEY

SECRET_KEY = base64.b64decode(SECRET_KEY).decode()
DATABASES = {}
DEBUG = False
ALLOWED_HOSTS = ["ripecapstone.pythonanywhere.com"]
