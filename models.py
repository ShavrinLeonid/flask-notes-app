from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
# Инициализация объекта базы данных SQLAlchemy
# Он будет привязан к Flask-приложению в create_app()
db = SQLAlchemy()
# Модель заметки
class Note(db.Model):
    # Уникальный идентификатор записи (первичный ключ)
    id = db.Column(db.Integer, primary_key=True)
    # Заголовок заметки (до 150 символов, обязательное поле)
    title = db.Column(db.String(150), nullable=False)
    # Основной текст заметки (обязательное поле)
    content = db.Column(db.Text, nullable=False)
    # Дата и время создания заметки
    # По умолчанию текущий UTC
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    # Имя владельца заметки (строка до 64 символов)
    # index=True создаёт индекс в БД для ускорения поиска по полю owner
    owner = db.Column(db.String(64), nullable=False, index=True)
    # Метод для отображения объекта в консоли и логах
    def __repr__(self):
        return f"<Note id={self.id} title={self.title!r} owner={self.owner!r}>"

from werkzeug.security import generate_password_hash, check_password_hash

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
