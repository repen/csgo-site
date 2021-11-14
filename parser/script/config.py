"""
Copyright 2021 Andrey Plugin (9keepa@gmail.com)
Licensed under the Apache License v2.0
http://www.apache.org/licenses/LICENSE-2.0
"""

import os

BASE_DIR = os.getenv("BASE_DIR", os.getcwd())
DATA_DIR = os.getenv("DATA", False)
REMOTE_API = os.getenv("REMOTE_API", "http://0.0.0.0:5000/betcsgo")
MYSQL_USR =os.getenv("MYSQL_USR", False)
MYSQL_PWD =os.getenv("MYSQL_PWD", False)
HOST = os.getenv("HOSTMQ", "127.0.0.1")
SHARE_DIR = os.getenv("SHARE_DIR", "/tmp")
