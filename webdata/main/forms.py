from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError, Regexp
from wtforms_sqlalchemy.fields import QuerySelectField
from flask_login import current_user
from webdata.models import User, UserClass, UserRoom

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email(), Length(min=3, max=50)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8, max=50)])
    remember = BooleanField('Remember Me', default=True)
    submit = SubmitField('Login')
    
class RegistrationForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(min=3, max=50)])
    email = StringField('Email', validators=[DataRequired(), Email(), Length(min=3, max=50)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8, max=50)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    phone_regex = r'^08{11}$'  # Adjust the regex according to your phone number format
    phone = StringField('Phone', validators=[
        DataRequired(),
        Length(min=10, max=13),
        Regexp(phone_regex, message="Phone number must be a 10-digit number")
    ])
    room = QuerySelectField(query_factory=lambda: UserRoom.query.all(), get_label="name")
    user_class = QuerySelectField(query_factory=lambda: UserClass.query.all(), get_label="name")
    submit = SubmitField('Sign Up')
    
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('That email is taken. Please choose a different one.')
        
