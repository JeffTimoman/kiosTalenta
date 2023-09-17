from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, SelectField, FileField, IntegerField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError, Regexp
from wtforms_sqlalchemy.fields import QuerySelectField
from flask_wtf.file import FileAllowed
from flask_login import current_user
from webdata.models import User, UserClass, UserRoom, ProductType, Product
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
    room = QuerySelectField(query_factory=lambda: UserRoom.query.order_by(UserRoom.name.asc()).all(), get_label="name")
    user_type = SelectField('User Type', choices=[('0', 'Administrator'), ('1', 'Cashier'), ('2', 'Customer')])
    user_class = QuerySelectField(query_factory=lambda:UserClass.query.order_by(UserClass.name.asc()).all(), get_label="name")
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
    room = QuerySelectField(query_factory=lambda: UserRoom.query.order_by(UserRoom.name.asc()).all(), get_label="name")
    user_type = SelectField('User Type', choices=[('0', 'Administrator'), ('1', 'Cashier'), ('2', 'Customer')], default='2')
    user_class = QuerySelectField(query_factory=lambda: UserClass.query.order_by(UserClass.name.asc()).all(), get_label="name")
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
    id = StringField('ID', validators=[DataRequired(), Length(min=3, max=50)])
    name = StringField('Name', validators=[DataRequired(), Length(min=3, max=50)])
    submit = SubmitField('Save Changes')
    

class AddClassForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(min=3, max=50)])
    submit = SubmitField('Add Class')

class EditRoomForm(FlaskForm):
    id = StringField('ID', validators=[DataRequired(), Length(min=3, max=50)])
    name = StringField('Name', validators=[DataRequired(), Length(min=3, max=50)])
    submit = SubmitField('Save Changes')
    
class AddRoomForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(min=3, max=50)])
    submit = SubmitField('Add Room')
    
class AddProductForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(min=3, max=50)])
    code = StringField('Code', validators=[DataRequired(), Length(min=3, max=50)])
    barcode = StringField('Barcode', validators=[DataRequired(), Length(min=3, max=50), Regexp(r'^\d+$', message="Barcode must be a number")])
    stock = IntegerField('Stock', validators=[DataRequired()])
    price = IntegerField('Price', validators=[DataRequired()])
    product_type = QuerySelectField(query_factory=lambda: ProductType.query.order_by(ProductType.name.asc()).all(), get_label="name")
    submit = SubmitField('Add Product')
    
    def validate_code_unique(self, code):
        product = Product.query.filter_by(code=self.code.data).first()
        if product:
            raise ValidationError('Code already exists')
    
    def validate_barcode_unique(self, barcode):
        product = Product.query.filter_by(barcode=self.barcode.data).first()
        if product:
            raise ValidationError('Barcode already exists')
        
    def validate_stock(self, stock):
        if self.stock.data < 0:
            raise ValidationError('Stock must be greater than 0')
    
    def validate_price(self, price):
        if self.price.data < 0:
            raise ValidationError('Price must be greater than 0')
    
    def validate_product_type(self, product_type):
        if self.product_type.data is None:
            raise ValidationError('Product Type must be selected')
    
    def validate_barcode_number(self, barcode):
        for char in self.barcode.data:
            if not char.isdigit():
                raise ValidationError('Barcode must be a number')
            
class AddStockForm(FlaskForm):
    barcode = StringField('Barcode', validators=[DataRequired(), Length(min=3, max=50), Regexp(r'^\d+$', message="Barcode must be a number")])
    stock = IntegerField('Stock', validators=[DataRequired()])
    submit = SubmitField('Add Stock')
    
    def validate_barcode(self, barcode):
        product = Product.query.filter_by(barcode=self.barcode.data).first()
        if product is None:
            raise ValidationError('Barcode does not exist')

class EditProductForm(FlaskForm):
    id = StringField('ID', validators=[DataRequired(), Length(min=3, max=50)])
    name = StringField('Name', validators=[DataRequired(), Length(min=3, max=50)])
    code = StringField('Code', validators=[DataRequired(), Length(min=3, max=50)])
    barcode = StringField('Barcode', validators=[DataRequired(), Length(min=3, max=50), Regexp(r'^\d+$', message="Barcode must be a number")])
    stock = IntegerField('Stock', validators=[DataRequired()])
    price = IntegerField('Price', validators=[DataRequired()])