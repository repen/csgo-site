import os

BASE_DIR = os.getenv("BASE_DIR", os.getcwd())
PRODUCTION_WORK = os.getenv("EXTERNAL_WORK", False)
SHARE_DIR = os.getenv("SHARE_DIR", "/tmp")