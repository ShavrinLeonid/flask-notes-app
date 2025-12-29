import os
from dotenv import load_dotenv

# Загружаем переменные окружения из .env
load_dotenv()

# Путь к директории проекта
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

# Папка instance для базы данных
INSTANCE_DIR = os.path.join(BASE_DIR, 'instance')
os.makedirs(INSTANCE_DIR, exist_ok=True)  # создаём папку, если её нет

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'replace-this-with-a-secure-random-key'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
                             'sqlite:///' + os.path.join(INSTANCE_DIR, 'notes.sqlite')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SESSION_COOKIE_SAMESITE = 'Lax'
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SECURE = False