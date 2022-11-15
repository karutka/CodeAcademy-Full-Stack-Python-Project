import os

from flask import Flask, flash, redirect, render_template, request, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap5
from flask_moment import Moment
from flask_fontawesome import FontAwesome
from flask_login import (
    LoginManager,
    UserMixin,
    current_user,
    logout_user,
    login_user,
    login_required,
)
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
login_manager.login_view = "login"
login_manager.login_message_category = "info"


class User(db.Model, UserMixin):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(
        "Username", db.String(64), unique=True, index=True, nullable=False
    )
    password = db.Column(
        "Password", db.String(64), unique=True, index=True, nullable=False
    )


class Note(db.Model):
    __tablename__ = "note"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column("Title", db.String)
    text = db.Column("Text", db.String)
    category_id = db.Column(db.Integer, db.ForeignKey("category.id"))
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    user = db.relationship("User", lazy=True)


class Category(db.Model):
    __tablename__ = "category"
    id = db.Column(db.Integer, primary_key=True)
    category = db.Column("Category", db.String)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    user = db.relationship("User", lazy=True)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/homepage/", methods=["GET", "POST"])
def homepage():
    return render_template("homepage.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("index"))
    form = forms.LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get("next")
            return redirect(next_page) if next_page else redirect(url_for("index"))
        else:
            flash("Login failed. Check username and password", "danger")
    return render_template("login.html", title="Log in", form=form)


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("index"))


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route("/register", methods=["GET", "POST"])
def register():
    db.create_all()
    if current_user.is_authenticated:
        return redirect(url_for("index"))
    form = forms.RegistrationForm()
    if form.validate_on_submit():
        encrypted_password = bcrypt.generate_password_hash(form.password.data).decode(
            "utf-8"
        )
        user = User(username=form.username.data, password=encrypted_password)
        db.session.add(user)
        db.session.commit()
        flash("Successfully signed up! You csn log in.", "success")
        return redirect(url_for("index"))
    return render_template("register.html", title="Register", form=form)


@app.route("/notes", methods=["GET", "POST"])
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


@app.route("/create_note/<int:category_id>", methods=["GET", "POST"])
@login_required
def create_note(category_id):
    db.create_all()
    form = forms.NoteForm()
    categories = get_categories()
    form.category.choices = [
        (str(category.id), category.category) for category in get_categories()
    ]

    if len(form.category.choices) == 0:
        flash("No categories found, you must create one first!", "error")
        return create_category()

    if form.validate_on_submit():
        create_note = Note(
            title=form.title.data,
            text=form.text.data,
            category_id=form.category.data,
            user_id=current_user.id,
        )
        db.session.add(create_note)
        db.session.commit()
        flash(f"Note created", "success")
        return redirect(url_for("notes"))
    else:
        selected_category = [
            category.id for category in categories if category_id == category.id
        ]
        if selected_category:
            form.category.default = str(selected_category[0])
            form.process()
        return render_template("create_note.html", form=form, categories=categories)


@app.route("/update_note/<int:id>", methods=["GET", "POST"])
@login_required
def update_note(id):
    form = forms.NoteForm()
    note = Note.query.get(id)
    form.category.choices = [
        (str(category.id), category.category) for category in get_categories()
    ]
    if form.validate_on_submit():
        note.title = form.title.data
        note.text = form.text.data
        note.category_id = form.category.data
        db.session.commit()
        return redirect(url_for("notes"))
    return render_template("modify_note.html", form=form, note=note)


@app.route("/delete_note/<int:id>")
@login_required
def delete_note(id):
    note = Note.query.get(id)
    db.session.delete(note)
    db.session.commit()
    return redirect(url_for("notes"))


@login_required
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
    all_notes = get_notes()
    return render_template(
        "categories.html",
        title="Categories",
        all_categories=all_categories,
        all_notes=all_notes,
    )

@login_required
def get_categories():
    try:
        all_categories = Category.query.filter_by(user_id=current_user.id).all()
    except:
        all_categories = []
    return all_categories


@login_required
def get_notes():
    try:
        all_notes = Note.query.filter_by(user_id=current_user.id).all()
    except:
        all_notes = []
    return all_notes


@app.route("/create_category", methods=["GET", "POST"])
@login_required
def create_category():
    db.create_all()
    form = forms.CategoryForm()
    if form.validate_on_submit():
        create_category = Category(category=form.category.data, user_id=current_user.id)
        db.session.add(create_category)
        db.session.commit()
        flash(f"New category was added", "success")
        return redirect(url_for("categories"))
    return render_template("create_category.html", title="New category", form=form)


@app.route("/delete_category/<int:id>")
@login_required
def delete_category(id):
    note = Category.query.get(id)
    db.session.delete(note)
    db.session.commit()

    notes = get_notes()
    combined_notes = [note.id for note in notes if id == note.category_id]

    if combined_notes:
        for combined_note in combined_notes:
            delete_note(combined_note)

    return redirect(url_for("categories"))


@app.route("/modify_category/<int:id>", methods=["GET", "POST"])
@login_required
def modify_category(id):
    form = forms.CategoryForm()
    category = Category.query.get(id)
    if form.validate_on_submit():
        category.category = form.category.data
        db.session.commit()
        return redirect(url_for("categories"))
    return render_template("modify_category.html", form=form, category=category)


@app.route("/search", methods=["GET", "POST"])
@login_required
def search():
    db.create_all()
    wanted_title = None
    wanted_category = []
    search_form = forms.SearchForm()
    search_form.categories.choices = [
        (str(category.id), category.category) for category in get_categories()
    ]
    if search_form.validate_on_submit():
        wanted_title = search_form.title.data
        wanted_category = search_form.categories.data

    is_search = wanted_title or wanted_category

    if is_search:
        try:
            all_notes = Note.query.filter_by(user_id=current_user.id).all()
            for note in list(all_notes):
                if wanted_title and wanted_title.lower() not in note.title.lower():
                    all_notes.remove(note)
                    continue

                if wanted_category and str(note.category_id) not in wanted_category:
                    all_notes.remove(note)
                    continue

                category_text = get_category_name(note.category_id)

                if category_text:
                    note.category = category_text

        except:
            all_notes = []
    else:
        all_notes = []
    return render_template(
        "search.html", title="Search", all_notes=all_notes, search_form=search_form
    )


@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404


@app.errorhandler(500)
def internal_server_error(e):
    return render_template("500.html"), 500


@app.errorhandler(403)
def forbidden(e):
    return render_template("403.html"), 403
