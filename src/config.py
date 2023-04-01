import os
import sys

from dotenv import load_dotenv
from loguru import logger


class Config:
    def __init__(self):
        load_dotenv()
        self.DB_DRIVER = os.getenv('DB_DRIVER')
        self.DB_HOST = os.getenv('DB_HOST')
        self.DB_USER = os.getenv('DB_USER')
        self.DB_PASSWORD = os.getenv('DB_PASSWORD')
        self.DB_DATABASE = os.getenv('DB_DATABASE')
        self.BOT_TOKEN = os.getenv('BOT_TOKEN')
        self.ADMIN_LOGIN = os.getenv('ADMIN_LOGIN')
        self.ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD')
        self.ADMIN = os.getenv('ADMIN')
        self.DSN = f"{self.DB_DRIVER}://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:5432/{self.DB_DATABASE}"


config = Config()

logger.add('log/error.log',
           format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {message}",
           filter=lambda x: x['level'].name == "ERROR",
           backtrace=True,
           diagnose=True,
           catch=True)

logger.add('log/success.log',
           format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {message}",
           filter=lambda x: x['level'].name == "SUCCESS",
           )


logger.level(name="update", no=31, color="<blue>", icon="♻️")
logger.level(name="error_update", no=32, color="<light-red>", icon='⚠️')


logger.add("log/update/{time:MMMM}/{time:D}/error_update.log", filter=lambda x: x['level'].name == "error_update",
           format="<green>{time:HH:mm:ss}</green> | <level>{message}</level>")
logger.add("log/update/{time:MMMM}/{time:D}/update.log", filter=lambda x: x['level'].name == "update",
           format="<green>{time:HH:mm:ss}</green> | <level>{message}</level>")
