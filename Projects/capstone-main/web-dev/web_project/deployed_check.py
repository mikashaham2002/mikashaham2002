import os


def is_deployed():
    return os.getenv("PYTHONANYWHERE_SITE") == "www.pythonanywhere.com"
