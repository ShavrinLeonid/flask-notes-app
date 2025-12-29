from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Length

# Форма для создания и редактирования заметок
class NoteForm(FlaskForm):
    # Поле заголовка заметки — обязательно, максимум 150 символов
    title = StringField('Заголовок', validators=[DataRequired(), Length(max=150)])
    # Основной текст заметки — обязателен, ограничен 5000 символами
    content = TextAreaField('Содержимое', validators=[DataRequired(), Length(max=5000)])
    # Кнопка отправки формы
    submit = SubmitField('Сохранить')

# Форма для входа пользователя
class LoginForm(FlaskForm):
    # Имя пользователя — обязательно, ограничено 64 символами
    username = StringField('Имя пользователя', validators=[DataRequired(), Length(max=64)])
    # Кнопка отправки формы
    submit = SubmitField('Войти')
