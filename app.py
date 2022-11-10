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

class Category(db.Model):
    __tablename__ = "category"
    id = db.Column(db.Integer, primary_key=True)
    category = db.Column("Category", db.String)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    user = db.relationship("User", lazy=True)
    
class Note(db.Model):
    __tablename__ = "note"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column("Title", db.String)
    text = db.Column("Text", db.String)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'))
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    user = db.relationship("User", lazy=True)

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

@app.route("/notes")
@login_required
def notes():
    db.create_all()
    try:
        all_notes = Note.query.filter_by(user_id=current_user.id).all()
        for note in all_notes:
            category_text = get_category_name(note.category_id)

            if category_text:
                note.category = category_text

    except:
        all_notes = []
    return render_template("notes.html", all_notes=all_notes)

@app.route("/create_note", methods=["GET", "POST"])
@login_required
def create_note():
    db.create_all()
    form = forms.NoteForm()

    categories = get_categories()
    form.category.choices = [(category.id, category.category) for category in categories]
    if form.validate_on_submit():
        create_note = Note(title=form.title.data, text=form.text.data,
                                 category_id=form.category.data, user_id=current_user.id)
        db.session.add(create_note)
        db.session.commit()
        flash(f"Note created", 'success')
        return redirect(url_for('notes'))

    return render_template("create_note.html", form=form, categories=categories)

def get_category_name(id):
    category_text = Category.query.filter_by(user_id=current_user.id, id=id).all()

    if len(category_text) == 1:
        return category_text[0].category
    else:
        return None

@app.route("/categories")
@login_required
def categories():
    db.create_all()
    all_categories = get_categories()
    return render_template('categories.html', title='Categories', all_categories=all_categories)

def get_categories():
    try:
        all_categories = Category.query.filter_by(user_id=current_user.id).all()
    except:
        all_categories = []
    return all_categories

@app.route("/create_category", methods=["GET", "POST"])
@login_required
def create_category():
    db.create_all()
    form = forms.CategoryForm()
    if form.validate_on_submit():
        create_category = Category(category=form.category.data, user_id=current_user.id)
        db.session.add(create_category)
        db.session.commit()
        flash(f"New category was added", 'success')
        return redirect(url_for('categories'))
    return render_template('create_category.html', title='New category', form=form)

@app.route("/delete_category/<int:id>")
@login_required
def delete_category(id):
    note = Category.query.get(id)
    db.session.delete(note)
    db.session.commit()
    return redirect(url_for('categories'))

@app.route("/modify_category/<int:id>", methods=['GET', 'POST'])
@login_required
def modify_category(id):
    form = forms.CategoryForm()
    category = Category.query.get(id)
    if form.validate_on_submit():
        category.category = form.category.data
        db.session.commit()
        return redirect(url_for('categories'))
    return render_template("modify_category.html", form=form, category=category)

@app.route("/search")
@login_required
def search():
    return render_template('search.html', title='Search')