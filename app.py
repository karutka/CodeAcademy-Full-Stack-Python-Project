import os

from flask import Flask, flash, redirect, render_template, request, session, url_for
from flask_sqlalchemy import SQLAlchemy
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
from flask_wtf import FlaskForm
from flask_bootstrap import Bootstrap5
from flask_moment import Moment
from flask_fontawesome import FontAwesome
from flask_login import LoginManager, UserMixin, current_user, logout_user, login_user, login_required
from flask_bcrypt import Bcrypt
import forms

basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)

app.config["SECRET_KEY"] = "0918273645"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(
    basedir, "data.sqlite"
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)
bootstrap = Bootstrap5(app)
moment = Moment(app)
fa = FontAwesome(app)

bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'register'
login_manager.login_message_category = 'info'


class User(db.Model, UserMixin):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column('Username', db.String(64), unique=True, index=True, nullable=False)
    password = db.Column('Password', db.String(64), unique=True, index=True, nullable=False)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = forms.LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('index'))
        else:
            flash('Login failed. Check username and password', 'danger')
    return render_template('login.html', title='Log in', form=form)

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('index'))

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route("/register", methods=["GET", "POST"])
def register():
    db.create_all()
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = forms.RegistrationForm()
    if form.validate_on_submit():
        encrypted_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, password=encrypted_password)
        db.session.add(user)
        db.session.commit()
        flash('Successfully signed up! You csn log in.', 'success')
        return redirect(url_for('index'))
    return render_template('register.html', title='Register', form=form)

@app.route("/homepage/", methods=["GET", "POST"])
def homepage():
    return render_template("homepage.html")