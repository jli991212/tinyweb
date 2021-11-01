from flask_wtf import FlaskForm
from flask_login import current_user
from wtforms import StringField, PasswordField, SubmitField, BooleanField, IntegerField, FileField, SelectField,DecimalField,TextAreaField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from unwrap.models import User


class RegistrationForm(FlaskForm):
    firstname = StringField('First Name',
                           validators=[DataRequired(), Length(min=2, max=20)])
    lastname = StringField('Last Name',
                           validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=9, max=20)])
    confirm_password = PasswordField('Confirm Password',
                                     validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError("That email is taken. Please choose a different one")


class LoginForm(FlaskForm):
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Sign in')

class UpdateAccountForm(FlaskForm):
    firstname = StringField('First Name',
                           validators=[DataRequired(), Length(min=2, max=20)])
    lastname = StringField('Last Name',
                           validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    submit = SubmitField('Update')

    def validate_email(self, email):
        if email.data != current_user.email:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('That email is taken. Please choose a different one.')
class updateproductForm(FlaskForm):
    name = StringField('Product Name',validators=[DataRequired()])
    price = DecimalField('Product price' ,validators=[DataRequired()])
    number =IntegerField('Product number', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[DataRequired(), Length(min=2, max=200)])
    image = FileField(' upload a image')
    submit = SubmitField('Update')
    category = SelectField('Select a category', validators=[DataRequired()], choices=[(1,'materiel'),(2,'catalyst')],coerce=int)

class addproductsForm(FlaskForm):
    name = StringField('Product Name',validators=[DataRequired()])
    price = DecimalField('Product price' ,validators=[DataRequired()])
    description =TextAreaField('Description', validators=[DataRequired(), Length(min=2, max=200)])
    number = IntegerField('Product number', validators=[DataRequired()])
    image = FileField(' upload a image')
    submit = SubmitField('Add')
    category = SelectField('Set a category', validators=[DataRequired()], choices=[(1,'materiel'),(2,'catalyst')],coerce=int)

