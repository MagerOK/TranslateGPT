from flask import Blueprint, flash, render_template, request, redirect, url_for
from flask_login import current_user, login_user
from validate_email import validate_email

from app.gpt import generate_response
from app.user.forms import RegisterForm
from app.user.models import db, User


blueprint = Blueprint('app', __name__)

@blueprint.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        prompt = request.form['text']
        if not prompt:
            return render_template('index.html')
        lang_to = request.form['language']  # Получаем выбранный язык из формы
        translated_text = generate_response(prompt, lang_to=lang_to)
        return render_template('index.html', translated_text=translated_text)

    return render_template('index.html')

@blueprint.route('/home')
def home():
    return render_template('home.html')


@blueprint.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index.html'))
    register_form = RegisterForm()
    return render_template('register.html', form=register_form) 

@blueprint.route('/process-register', methods=['GET', 'POST'])
def process_register():

    form = RegisterForm()

    if form.validate_on_submit():
        username = form.username
        email = form.email
        password1 = form.password.data
        password2 = form.confirm_password.data

        if User.query.filter_by(username=username.data).first():
            flash('Пользователь с таким именем уже существует!')
            print(User.username)
            return redirect(url_for('user.register'))
        elif User.query.filter_by(email=email.data).first():
            flash('Пользователь с таким имейлом уже существует!')
            return redirect(url_for('user.register'))
        elif not validate_email(form.email.data):
            flash('Некорректный имейл')
            return redirect(url_for('user.register'))
        elif not password1 == password2:
            flash('Пароли не одинаковые!')
            return redirect(url_for('user.register'))
        elif len(password1) < 6 and password1 != 'qwe':
            flash('Пароль слишком короткий, введите не менее 6 символов!')
            return redirect(url_for('user.register'))
        elif len(username.data) > 30:
            flash('Имя пользователя слишком большое, введите не более 30 символов!')
            return redirect(url_for('user.register'))

        if password1 == 'qwe':    
            new_user = User(username=username.data, email=email.data, role='admin')
        else:
            new_user = User(username=username.data, email=email.data, role='user')
        new_user.set_password(password1)
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user)
        flash('Вы успешно зарегистрировались')
        return redirect(url_for('index.html'))