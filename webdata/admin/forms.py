from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, SelectField, FileField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError, Regexp
from wtforms_sqlalchemy.fields import QuerySelectField
from flask_wtf.file import FileAllowed
from flask_login import current_user
from webdata.models import User, UserClass
import re

class EditUserForm(FlaskForm):
    
    name = StringField('Name', validators=[DataRequired(), Length(min=3, max=50)])
    email = StringField('Email', validators=[DataRequired(), Email(), Length(min=3, max=50)])
    phone_regex = r'^08{11}$'  # Adjust the regex according to your phone number format
    phone = StringField('Phone', validators=[
        DataRequired(),
        Length(min=10, max=13),
        Regexp(phone_regex, message="Phone number must be a 10-digit number")
    ])
    room_regex = r'^(A|B|AB)[0-9]{3}$'
    # Adjust the regex according to your phone number format
    room = StringField('Room', validators=[
        DataRequired(),
        Length(min=4, max=5),
        Regexp(room_regex, message="Room must be a 4-digit/5-digit number")
    ])
    user_type = SelectField('User Type', choices=[('0', 'Administrator'), ('1', 'Cashier'), ('2', 'Customer')])
    user_class = QuerySelectField(query_factory=lambda: UserClass.query.all(), get_label="name")
    profile_picture = FileField('Profile Picture', validators=[FileAllowed(['jpg', 'png'])])
    active_field = SelectField('Active', choices=[('1', 'Active'), ('0', 'Inactive')])
    submit = SubmitField('Sign Up')  

class AddUserForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(min=3, max=50)])
    email = StringField('Email', validators=[DataRequired(), Email(), Length(min=3, max=50)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8, max=50)])
    confirm = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    phone_regex = r'^08{11}$'  # Adjust the regex according to your phone number format
    phone = StringField('Phone', validators=[
        DataRequired(),
        Length(min=10, max=13),
        Regexp(phone_regex, message="Phone number must be a 10-digit number")
    ])
    room_regex = r'^(A|B|AB)[0-9]{3}$'
    # Adjust the regex according to your phone number format
    room = StringField('Room', validators=[
        DataRequired(),
        Length(min=4, max=5),
        Regexp(room_regex, message="Room must be a 4-digit/5-digit number")
    ])
    user_type = SelectField('User Type', choices=[('0', 'Administrator'), ('1', 'Cashier'), ('2', 'Customer')], default='2')
    user_class = QuerySelectField(query_factory=lambda: UserClass.query.all(), get_label="name")
    profile_picture = FileField('Profile Picture', validators=[FileAllowed(['jpg', 'png'])])
    active_field = SelectField('Active', choices=[ ('0', 'Inactive'), ('1', 'Active')], default='1')
    submit = SubmitField('Sign Up')
    def validate_password_confirm(self, confirm):
        if self.password.data != confirm.data:
            raise ValidationError('Password does not match')

class ChangeUserPasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8, max=50)])
    confirm = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Change Password')
    
    def validate_password_confirm(self, confirm):
        if self.password.data != confirm.data:
            raise ValidationError('Password does not match')
        
class EditClassForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(min=3, max=50)])
    submit = SubmitField('Save Changes')