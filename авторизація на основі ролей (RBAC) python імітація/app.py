from flask import Flask, render_template, redirect, url_for, request
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import secrets

# Ініціалізація додатка та бази даних
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SECRET_KEY'] = secrets.token_hex(32)  # Генерація випадкового секретного ключа
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Створення моделі користувачів з ролями
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    role = db.Column(db.String(50), nullable=False)  # Роль користувача (user або admin)

# Завантаження користувача по id
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Створення головної сторінки
@app.route('/')
def home():
    return render_template('home.html')

# Сторінка для користувача
@app.route('/user')
@login_required
def user_page():
    if current_user.role == 'admin':
        return redirect(url_for('admin_page'))
    return render_template('user.html')

# Сторінка для адміністратора
@app.route('/admin')
@login_required
def admin_page():
    if current_user.role != 'admin':
        return redirect(url_for('user_page'))
    return render_template('admin.html')

# Сторінка для логіну
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:  # Перевірка пароля
            login_user(user)
            return redirect(url_for('home'))
    return render_template('login.html')

# Сторінка для реєстрації
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        role = request.form['role']
        new_user = User(username=username, password=password, role=role)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('register.html')

# Вихід з системи
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

if __name__ == '__main__':
    # Встановлення контексту програми
    with app.app_context():
        db.create_all()  # Створюємо таблиці в базі даних

    app.run(debug=True)
