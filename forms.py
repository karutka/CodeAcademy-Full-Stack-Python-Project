from flask_wtf import FlaskForm
from wtforms import SubmitField, BooleanField, StringField, PasswordField, FloatField, SelectField, SelectMultipleField, \
    widgets
from wtforms.validators import DataRequired, ValidationError, EqualTo
import app


class RegistrationForm(FlaskForm):
    username = StringField('Username', [DataRequired()])
    password = PasswordField('Password', [DataRequired()])
    approved_password = PasswordField('Repeat password', [EqualTo('password', "Password must be identical")])
    submit = SubmitField('Register')

    def check_username(self, username):
        user = app.User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('This username is already taken. Please choose different one.')

class LoginForm(FlaskForm):
    username = StringField('Username', [DataRequired()])
    password = PasswordField('Password', [DataRequired()])
    remember = BooleanField('Remember me')
    submit = SubmitField('Log In')
    
class CategoryForm(FlaskForm):
    category = StringField('Category', [DataRequired()])
    submit = SubmitField('Add')
    
class NoteForm(FlaskForm):
    title = StringField('Note title', [DataRequired()])
    text = StringField('Note text', [DataRequired()])
    category = SelectField('Categories', choices=[])
    submit = SubmitField('Submit')
    
class MultiForm(SelectMultipleField):
    widget = widgets.ListWidget(prefix_label=False)
    option_widget = widgets.CheckboxInput()


class SearchForm(FlaskForm):
    title = StringField("Title")
    category = StringField("Category")
    categories = MultiForm("Categories")
    submit = SubmitField("Submit")