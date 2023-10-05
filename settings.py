import logging

REDIS_HOST = '*'
REDIS_PORT = 6379
DEBUG = False
API_TOKEN = ''
MAX_TRAVELS_PER_USER = 10
MAX_PARCELS_PER_USER = 10
QR_CODE_FILE_ID = ''

DATABASE = 'postgres://postgres:12345@localhost:5432/postman'
USE_MEMORY_STORAGE = False
ADMIN_ID = 12345678

import os
if 'API_TOKEN' in os.environ:
    API_TOKEN = os.environ['API_TOKEN']

if 'STAGE' in os.environ:
    QR_CODE_FILE_ID = ''

try:
    from app_settings import *
except:
    pass

if DEBUG:
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s %(levelname)s %(module)s: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
    )
else:
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s %(levelname)s %(module)s: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
    )

if 'API_TOKEN' in os.environ:
    logging.info("token has been found in environment variables")
