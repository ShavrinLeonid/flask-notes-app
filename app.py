import os
import logging

from flask import (
    Flask, render_template, redirect,
    url_for, flash, session, abort, request
)

from config import Config
from models import db, Note, User
from forms import NoteForm, LoginForm
import bleach

# ---------------------- HTML sanitization ----------------------
ALLOWED_TAGS = ['b', 'i', 'u', 'em', 'strong', 'a', 'p', 'br', 'ul', 'ol', 'li']
ALLOWED_ATTRS = {'a': ['href', 'rel', 'target']}


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # ---------------------- Secure session cookies ----------------------
    app.config.update(
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE='Lax',
        SESSION_COOKIE_SECURE=False  # True только при HTTPS
    )

    # ---------------------- Database ----------------------
    db.init_app(app)

    try:
        os.makedirs(os.path.join(app.root_path, 'instance'), exist_ok=True)
    except OSError as e:
        logging.error(f"Failed to create instance directory: {e}")

    with app.app_context():
        db.create_all()

    # ---------------------- Security headers middleware ----------------------
    @app.after_request
    def add_security_headers(response):
        response.headers['Content-Security-Policy'] = (
            "default-src 'self'; "
            "style-src 'self' https://cdn.simplecss.org; "
            "script-src 'self'; "
            "img-src 'self' data:; "
            "font-src 'self'; "
            "connect-src 'self'; "
            "frame-ancestors 'none'; "
            "object-src 'none'; "
            "base-uri 'self'; "
            "form-action 'self';"
        )
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'

        # Скрываем сервер
        response.headers.pop('Server', None)
        return response

    # ---------------------- Authentication ----------------------
    @app.route('/register', methods=['GET', 'POST'])
    def register():
        if request.method == 'POST':
            username = request.form.get('username')
            password = request.form.get('password')

            if not username or not password:
                flash('Заполните все поля', 'danger')
                return redirect(url_for('register'))

            if User.query.filter_by(username=username).first():
                flash('Пользователь уже существует', 'danger')
                return redirect(url_for('register'))

            user = User(username=username)
            user.set_password(password)

            db.session.add(user)
            db.session.commit()

            flash('Регистрация успешна', 'success')
            return redirect(url_for('login'))

        return render_template('register.html')

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if request.method == 'POST':
            username = request.form.get('username')
            password = request.form.get('password')

            user = User.query.filter_by(username=username).first()

            if user and user.check_password(password):
                session['user'] = user.username
                flash('Успешный вход', 'success')
                return redirect(url_for('index'))

            flash('Неверные данные', 'danger')

        return render_template('login.html')

    @app.route('/logout')
    def logout():
        session.pop('user', None)
        flash('Вы вышли', 'info')
        return redirect(url_for('index'))

    # ---------------------- Main page ----------------------
    @app.route('/', methods=['GET', 'POST'])
    def index():
        note_form = NoteForm()
        login_form = LoginForm()

        if note_form.validate_on_submit():
            owner = session.get('user')
            if not owner:
                flash('Надо войти, чтобы добавить заметку.', 'warning')
                return redirect(url_for('index'))

            clean_content = bleach.clean(
                note_form.content.data,
                tags=ALLOWED_TAGS,
                attributes=ALLOWED_ATTRS,
                strip=True
            )

            note = Note(
                title=note_form.title.data.strip(),
                content=clean_content,
                owner=owner
            )
            db.session.add(note)
            db.session.commit()
            flash('Заметка создана', 'success')
            return redirect(url_for('index'))

        notes = Note.query.order_by(Note.created_at.desc()).all()
        return render_template(
            'index.html',
            notes=notes,
            form=note_form,
            login_form=login_form
        )

    # ---------------------- Edit note ----------------------
    @app.route('/edit/<int:note_id>', methods=['GET', 'POST'])
    def edit(note_id):
        note = Note.query.get_or_404(note_id)
        current_user = session.get('user')

        if not current_user or note.owner != current_user:
            abort(403)

        form = NoteForm(obj=note)

        if form.validate_on_submit():
            note.title = form.title.data.strip()
            note.content = bleach.clean(
                form.content.data,
                tags=ALLOWED_TAGS,
                attributes=ALLOWED_ATTRS,
                strip=True
            )
            db.session.commit()
            flash('Заметка успешно обновлена', 'success')
            return redirect(url_for('index'))

        return render_template('edit.html', form=form, note=note)

    # ---------------------- Delete note ----------------------
    @app.route('/delete/<int:note_id>', methods=['POST'])
    def delete(note_id):
        note = Note.query.get_or_404(note_id)
        current_user = session.get('user')

        if not current_user or note.owner != current_user:
            abort(403)

        db.session.delete(note)
        db.session.commit()
        flash('Заметка удалена', 'info')
        return redirect(url_for('index'))

    # ---------------------- Errors ----------------------
    @app.errorhandler(403)
    def forbidden(e):
        return "403 Forbidden", 403

    return app


if __name__ == '__main__':
    application = create_app()
    application.run(debug=True)
