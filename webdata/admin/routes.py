from flask import Blueprint, render_template, url_for, flash, redirect, request, abort, jsonify, make_response, session

from webdata import db, bcrypt, app, thisConfig
from flask_login import login_user, current_user, logout_user, login_required
from webdata.main.forms import LoginForm, RegistrationForm

from flask_cors import CORS, cross_origin

from werkzeug.utils import secure_filename

from webdata.models import User, RegistrationProfile, UserClass, UserRoom, Product, ProductType, ProductTransaction, ProductTransactionDetail

from webdata.admin.forms import EditUserForm, ChangeUserPasswordForm, AddUserForm, EditClassForm, AddClassForm, EditRoomForm, AddRoomForm, AddProductForm, AddStockForm, EditProductForm, AddProductTypeForm, EditProductTypeForm

from pytz import timezone
from datetime import datetime
from collections import OrderedDict
from PIL import Image

import uuid as uuid
import os
import json
import re
import json

# import logging
# logging.basicConfig()
# logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)

admin = Blueprint('admin', __name__)

CORS(admin, resources={r"/api/*": {"origins": "*"}})

def save_image(form_picture, user_id):
    pic_filename = secure_filename(form_picture.filename)
    pic_name = str(uuid.uuid1()) + "_" + str(user_id)
    pic_path = os.path.join(app.root_path, 'static/profile_pictures', pic_name)
    form_picture.save(pic_path)
    return pic_name

from datetime import datetime
from pytz import timezone

def product_transaction_code_generator():
    today_date = datetime.now(timezone('Asia/Jakarta'))
    year = today_date.strftime("%Y")
    month = today_date.strftime("%m")
    date = today_date.strftime("%d")
    # hour:minute
    hour = today_date.strftime("%H")
    minute = today_date.strftime("%M")

    start_of_day = today_date.replace(hour=0, minute=0, second=0, microsecond=0)
    end_of_day = today_date.replace(hour=23, minute=59, second=59, microsecond=999999)

    transaction_today = ProductTransaction.query.filter(
        ProductTransaction.date_created >= start_of_day,
        ProductTransaction.date_created <= end_of_day
    ).count()

    return f"PR.{year}{month}{date}.{hour}:{minute}.{transaction_today + 1}.{thisConfig.SHOP_CODE}"


@admin.route("/", methods=['GET', 'POST'])
@login_required
def index():
    if current_user.user_type != 0:
        abort(403)
    text = None
    data_api = None 
    if request.method == 'POST':
        text = request.form.get('bambang')
        data_api = 'proses abcd'
        
    return render_template('admin/index.html', text=text)

@admin.route('/cashier', methods=['GET', 'POST'])
@login_required
def cashier():

    return render_template('admin/cashier.html')

@admin.route('/transaction/product/offline', methods=['GET', 'POST'])
@login_required
def transaction_product_offline():
    transaction_offlines = ProductTransaction.query.filter_by(transaction_type=0).all()
    print(transaction_offlines)
    return render_template('admin/transaction_product_offline.html', transaction_offlines=transaction_offlines)

@admin.route('/products/product_types', methods=['GET', 'POST'])
@login_required
def product_types():
    if current_user.user_type != 0:
        abort(403)
    product_types = ProductType.query.all()
    addProductTypeForm = AddProductTypeForm()
    editProductTypeForm = EditProductTypeForm()
    
    if request.method == 'POST':
        action = request.args.get('action')
        if action == 'add':
            name = addProductTypeForm.name.data
            if addProductTypeForm.validate_on_submit():
                
                check_name = ProductType.query.filter_by(name=name).first()
                if check_name is not None:
                    flash(f"Product Type {name} already exists!", 'danger')
                    return redirect(url_for('admin.product_types'))
                
                if name == '' or name == None:
                    flash(f"Name cannot be empty!", 'danger')
                    return redirect(url_for('admin.product_types'))
                
                if len(name) < 3 or len(name) > 50:
                    flash(f"Name must be between 3 and 50 characters!", 'danger')
                    return redirect(url_for('admin.product_types'))
                
                data = ProductType(name=name)
                db.session.add(data)
                db.session.commit()
                flash(f"Product Type {name} has been added!", 'success')
                return redirect(url_for('admin.product_types'))
            else :
                for error in addProductTypeForm.errors:
                    the_error_text = addProductTypeForm.errors[error][0]
                    flash(f"{error} : {the_error_text}", 'danger')
                redirect(url_for('admin.product_types'))
        if action == 'edit':
            if editProductTypeForm.validate_on_submit():
                name = editProductTypeForm.name.data
                id = editProductTypeForm.id.data
                
                data = ProductType.query.filter_by(id=id).first()
                check_name = ProductType.query.filter_by(name=name).first()
                
                if data is None:
                    flash(f"Product Type not found!", 'danger')
                    return redirect(url_for('admin.product_types'))
                if data.name == name:
                    flash(f"No changes made!", 'info')
                    return redirect(url_for('admin.product_types'))
                if check_name is not None:
                    flash(f"Product Type {name} already exists!", 'danger')
                    return redirect(url_for('admin.product_types')) 
                
                data.name = name
                db.session.commit()
                flash(f"Product Type with id : {id} has been updated!", 'success')
                return redirect(url_for('admin.product_types'))
            else :
                for error in editProductTypeForm.errors:
                    the_error_text = editProductTypeForm.errors[error][0]
                    flash(f"{error} : {the_error_text}", 'danger')
                redirect(url_for('admin.product_types'))    
    return render_template('admin/product_types.html', product_types=product_types, addProductTypeForm=addProductTypeForm, editProductTypeForm=editProductTypeForm)

@admin.route('/products/product_type/<int:id>', methods=['GET', 'POST'])
@login_required
def product_type(id):
    return 'hai'

@admin.route('/products/edit_product/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_product(id):
    if current_user.user_type != 0:
        abort(403)
    product = Product.query.filter_by(id=id).first()
    if product is None:
        flash(f"Product not found!", 'danger')
        return redirect(url_for('admin.products'))
    editProductForm = EditProductForm()
    
    if request.method == 'POST':
        if editProductForm.validate_on_submit():
            name = editProductForm.name.data
            price = editProductForm.price.data
            stock = editProductForm.stock.data
            product_type = editProductForm.product_type.data.id
            code = editProductForm.code.data
            barcode = editProductForm.barcode.data
            
            check_barcode = Product.query.filter_by(barcode=barcode).first()
            check_code = Product.query.filter_by(code=code).first()
            if check_barcode is not None and check_barcode.id != product.id:
                flash(f"Barcode {barcode} already exists!", 'danger')
                return redirect(url_for('admin.edit_product', id=id))
            if check_code is not None and check_code.id != product.id:
                flash(f"Code {code} already exists!", 'danger')
                return redirect(url_for('admin.edit_product', id=id))
            
            if name == product.name and price == product.price and stock == product.stock and product_type == product.product_type and code == product.code and barcode == product.barcode:
                flash(f"No changes made!", 'info')
                return redirect(url_for('admin.edit_product', id=id))
            
            if name == '' or name == None:
                flash(f"Name cannot be empty!", 'danger')
                return redirect(url_for('admin.edit_product', id=id))
            
            if len(name) < 3 or len(name) > 50:
                flash(f"Name must be between 3 and 50 characters!", 'danger')
                return redirect(url_for('admin.edit_product', id=id))
            
            if stock < 0:
                flash(f"Stock must be greater than 0!", 'danger')
                return redirect(url_for('admin.edit_product', id=id))
            
            if price < 0:
                flash(f"Price must be greater than 0!", 'danger')
                return redirect(url_for('admin.edit_product', id=id))
            
            if product_type == None or product_type == '':
                flash(f"Product Type cannot be empty!", 'danger')
                return redirect(url_for('admin.edit_product', id=id))
            
            if code == '' or code == None:
                flash(f"Code cannot be empty!", 'danger')
                return redirect(url_for('admin.edit_product', id=id))
            
            if len(code) < 3 or len(code) > 50:
                flash(f"Code must be between 3 and 50 characters!", 'danger')
                return redirect(url_for('admin.edit_product', id=id))
            
            if barcode == '' or barcode == None:
                flash(f"Barcode cannot be empty!", 'danger')
                return redirect(url_for('admin.edit_product', id=id))
            
            if len(barcode) < 3 or len(barcode) > 50:
                flash(f"Barcode must be between 3 and 50 characters!", 'danger')
                return redirect(url_for('admin.edit_product', id=id))
            
            product.name = name
            product.price = price
            product.stock = stock
            product.product_type = product_type
            product.code = code
            product.barcode = barcode
            db.session.commit()
            flash(f"Product {name} has been updated!", 'success')
            return redirect(url_for('admin.edit_product', id=id))
        else : 
            for error in editProductForm.errors:
                the_error_text = editProductForm.errors[error][0]
                flash(f"{error} : {the_error_text}", 'danger')
            redirect(url_for('admin.edit_product', id=id))
            
    return render_template('admin/edit_products.html', product=product, editProductForm=editProductForm)

@admin.route("/products")
@login_required
def products():
    if current_user.user_type != 0:
        abort(403)
        
    products = Product.query.all()
    return render_template('admin/products.html', products=products)

@admin.route("/products/add_product", methods=['GET', 'POST'])
@login_required
def add_product():
    if current_user.user_type != 0:
        abort(403)
    
    addProductForm = AddProductForm()
    
    if request.method == 'POST':
        if addProductForm.validate_on_submit():
            name = addProductForm.name.data
            price = addProductForm.price.data
            stock = addProductForm.stock.data
            product_type = addProductForm.product_type.data.id
            code = addProductForm.code.data
            barcode = addProductForm.barcode.data
            
            check_barcode = Product.query.filter_by(barcode=barcode).first()
            check_code = Product.query.filter_by(code=code).first()
            if check_barcode is not None:
                flash(f"Barcode {barcode} already exists!", 'danger')
                return redirect(url_for('admin.add_product'))
            
            if check_code is not None:
                flash(f"Code {code} already exists!", 'danger')
                return redirect(url_for('admin.add_product'))
            
            data = Product(name=name, price=price, stock=stock, product_type=product_type, code=code, barcode=barcode)
            db.session.add(data)
            db.session.commit()
            flash(f"Product {name} has been added!", 'success')
            return redirect(url_for('admin.add_product'))
        else : 
            for error in addProductForm.errors:
                the_error_text = addProductForm.errors[error][0]
                flash(f"{error} : {the_error_text}", 'danger')
            redirect(url_for('admin.add_product'))
        
    return render_template('admin/add_product.html', addProductForm=addProductForm)

@admin.route("/products/add_stock_barcode", methods=['GET', 'POST'])
@login_required
def add_stock_2():
    addStockForm = AddStockForm()
    if request.method == 'POST':
        if addStockForm.validate_on_submit():
            product = Product.query.filter_by(barcode=addStockForm.barcode.data).first()
            if product is None:
                flash(f"Product with barcode {addStockForm.barcode.data} not found!", 'danger')
                return redirect(url_for('admin.add_stock'))
            if (addStockForm.stock.data < 0):
                flash(f"Stock must be greater than 0!", 'danger')
                return redirect(url_for('admin.add_stock'))
            product.stock += addStockForm.stock.data
            db.session.commit()
            flash(f"Stock for product {product.name} has been added!", 'success')
            return redirect(url_for('admin.add_stock_2'))
        else : 
            for error in addStockForm.errors:
                the_error_text = addStockForm.errors[error][0]
                flash(f"{error} : {the_error_text}", 'danger')
    return render_template('/admin/add_stock.html', addStockForm=addStockForm)

@admin.route("/products/add_stock", methods=['GET', 'POST'])
@login_required
def add_stock():
    if request.method == 'POST':
        
        product_barcode = request.form.get('barcode')
        stock = request.form.get('stock')
        
        product = Product.query.filter_by(barcode=product_barcode).first()
        if product is None:
            flash(f"Product with barcode {product_barcode} not found!", 'danger')
            return redirect(url_for('admin.add_stock'))
        
        if (int(stock) < 0):
            flash(f"Stock must be greater than 0!", 'danger')
            return redirect(url_for('admin.add_stock'))
        
        product.stock += int(stock)
        db.session.commit()
        flash(f"Stock for product {product.name} has been added!", 'success')
        return redirect(url_for('admin.add_stock'))
        
    return render_template('/admin/add_stock_2.html')


@admin.route("products/delete_product")
@login_required
def delete_product():
    ids = request.args.getlist('id')
    flash("This feature is not yet implemented!", "danger")
    return redirect(url_for('admin.products'))
    

@admin.route("/users/user_classes", methods=['GET', 'POST'])
@login_required
def user_classes():
    if current_user.user_type != 0:
        abort(403)
    classes = UserClass.query.all()
    
    editClassForm = EditClassForm()
    addClassForm = AddClassForm()
    if request.method == 'POST':
        action = request.args.get('action')
        if action == 'edit':
            name = editClassForm.name.data
            id = editClassForm.id.data
            
            data = UserClass.query.filter_by(id=id).first()
            check_name = UserClass.query.filter_by(name=name).first()
            
            if data is None:
                flash(f"Class not found!", 'danger')
                return redirect(url_for('admin.user_classes'))
            if data.name == name:
                flash(f"No changes made!", 'info')
                return redirect(url_for('admin.user_classes'))
            if check_name is not None:
                flash(f"Class {name} already exists!", 'danger')
                return redirect(url_for('admin.user_classes'))
            
            if name == '' or name == None:
                flash(f"Name cannot be empty!", 'danger')
                return redirect(url_for('admin.user_classes'))
            
            if len(name) < 3 or len(name) > 50:
                flash(f"Name must be between 3 and 50 characters!", 'danger')
                return redirect(url_for('admin.user_classes'))
            
            data.name = name
            db.session.commit()
            flash(f"Class with id : {id} has been updated!", 'success')
            return redirect(url_for('admin.user_classes'))
        if action == 'add':
            name = addClassForm.name.data
            
            check_name = UserClass.query.filter_by(name=name).first()
            if check_name is not None:
                flash(f"Class {name} already exists!", 'danger')
                return redirect(url_for('admin.user_classes'))
            
            if name == '' or name == None:
                flash(f"Name cannot be empty!", 'danger')
                return redirect(url_for('admin.user_classes'))
            
            if len(name) < 3 or len(name) > 50:
                flash(f"Name must be between 3 and 50 characters!", 'danger')
                return redirect(url_for('admin.user_classes'))
            
            data = UserClass(name=name)
            db.session.add(data)
            db.session.commit()
            flash(f"Class {name} has been added!", 'success')
        
    return render_template('admin/user_classes.html', classes=classes, editClassForm=editClassForm, addClassForm=addClassForm)

@admin.route("/users/user_classes/delete_class/<int:id>", methods=['POST', 'GET'])
@login_required
def delete_class(id):
    if current_user.user_type != 0:
        abort(403)
    # return redirect(url_for('admin.user_classes'))
    user_class = UserClass.query.filter_by(id=id).first()
    if user_class is None:
        flash(f"User class not found!", 'danger')
        return redirect(url_for('admin.user_classes'))
    
    if request.method == 'POST':
        csrf_token = session.get('csrf_token')
        if not csrf_token or csrf_token != request.form.get('csrf_token'):
            abort(403)
        db.session.delete(user_class)
        db.session.commit()
        flash(f"User class {user_class.name} has been deleted!", 'success')
        return redirect(url_for('admin.user_classes'))
    return render_template('admin/delete_class.html', user_class=user_class)
    

@admin.route("/users/user_classes/user_class/<int:id>", methods=['GET', 'POST'])
@login_required
def user_class(id):
    if current_user.user_type != 0:
        abort(403)
        
    user_class = UserClass.query.filter_by(id=id).first()
    if user_class is None:
        flash(f"User class not found!", 'danger')
        return redirect(url_for('admin.user_classes'))
    
    
    return render_template('admin/user_class.html', user_class=user_class)

@admin.route("/users/registration_profiles")
@login_required
def registration_profiles():
    today_date = [datetime.now(timezone('Asia/Jakarta')).strftime("%A"), datetime.now(timezone('Asia/Jakarta')).strftime(" · %B %d, %Y · %I:%M %p")]
    flash(f"You are logged in as {current_user.name.title()}", 'success')
    return render_template('admin/registration_profiles.html', today_date=today_date)

@admin.route('/users/add_user', methods=['GET', 'POST'])
@login_required
def add_user():
    if current_user.user_type != 0:
        abort(403)
    addUserForm = AddUserForm()
    if request.method == 'POST':
        name = addUserForm.name.data
        email = addUserForm.email.data
        password = addUserForm.password.data
        confirm = addUserForm.confirm.data
        active = addUserForm.active_field.data
        if active == '1':
            active = True
        else:
            active = False
        phone = None
        room = None
        user_class = None
        role = addUserForm.user_type.data
        print(role)
        if role == None or role == '':
            flash(f"Role cannot be empty!", 'danger')
            return redirect(url_for('admin.add_user'))
        
        if role == '2' or role == 2:
            phone = addUserForm.phone.data
            room = addUserForm.room.data.id
            user_class = addUserForm.user_class.data.id
        
        check_email = User.query.filter_by(email=email).first()
        if check_email is not None:
            flash(f"Email {email} already exists!", 'danger')
            return redirect(url_for('admin.add_user'))

        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, email):
            flash(f"Email {email} is not valid!", 'danger')
            return redirect(url_for('admin.add_user'))
        
        if name == '' or name == None:
            flash(f"Name cannot be empty!", 'danger')
            return redirect(url_for('admin.add_user'))
        
        if len(name) < 3 or len(name) > 50:
            flash(f"Name must be between 3 and 50 characters!", 'danger')
            return redirect(url_for('admin.add_user'))
        
        if password == '' or password == None:
            flash(f"Password cannot be empty!", 'danger')
            return redirect(url_for('admin.add_user'))
        
        if password != confirm:
            flash(f"Password and Confirm Password must be the same!", 'danger')
            return redirect(url_for('admin.add_user'))
        
        if len(password) < 8 or len(password) > 50:
            flash(f"Password must be between 8 and 50 characters!", 'danger')
            return redirect(url_for('admin.add_user'))
        if role == 2 or role == '2':
            
            if phone == None or phone == '':
                flash(f"Phone cannot be empty!", 'danger')
                return redirect(url_for('admin.add_user'))

            phone_pattern = r'^08[0-9]{9,}$'
            if len(phone) < 10 or len(phone) > 13:
                flash(f"Phone must be between 10 and 13 characters!", 'danger')
                return redirect(url_for('admin.add_user'))
            
            if not re.match(phone_pattern, phone):
                flash(f"Phone number must be a 10-digit number!", 'danger')
                return redirect(url_for('admin.add_user'))
            
            if room == None or room == '':
                flash(f"Room cannot be empty!", 'danger')
                return redirect(url_for('admin.add_user'))
            
            check_room = UserRoom.query.filter_by(id=room).first()
            if check_room is None:
                flash(f"Room {room.name} does not exist!", 'danger')
                return redirect(url_for('admin.add_user'))
        
        user = None
        if role == '2' or role == 2:
            user = User(name=name, email=email, password=bcrypt.generate_password_hash(password).decode('utf-8'), active=active, phone=phone, room=room, user_class_id=user_class, date_created=datetime.now(timezone('Asia/Jakarta')), user_type=role)
        else: 
            user = User(name=name, email=email, password=bcrypt.generate_password_hash(password).decode('utf-8'), active=active, date_created=datetime.now(timezone('Asia/Jakarta')), user_type=role)
        
        profile_picture = request.files['profile_picture']
        ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
        
        if profile_picture.filename != '':
            output_size = (500, 500)
            if not '.' in profile_picture.filename or profile_picture.filename.rsplit('.', 1)[1].lower() not in ALLOWED_EXTENSIONS:
                flash(f"Profile picture must be a jpg or png file!", 'danger')
                return redirect(url_for('admin.add_user'))
            pic_name = str(uuid.uuid1()) + "_" + str(user.id)  + '.jpg'
            profile_picture.save(os.path.join(app.config['UPLOAD_FOLDER'], pic_name))
            user.profile_picture = pic_name
            
            i = Image.open(os.path.join(app.config['UPLOAD_FOLDER'], pic_name))
            i.thumbnail(output_size)
            i.save(os.path.join(app.config['UPLOAD_FOLDER'], pic_name))
        else:
            user.profile_picture = 'default.png'
        print(name, email, password, active, phone, room, user_class, profile_picture)
        print(user.name, user.email, user.password, user.active, user.phone, user.room, user.user_class_id, user.date_created, user.profile_picture)
        db.session.add(user)
        db.session.commit()
        flash(f"User {name.title()} has been added!", 'success')
        return redirect(url_for('admin.add_user'))

    return render_template('admin/add_user.html', addUserForm=addUserForm)

@admin.route("/users")
@login_required
def user_profiles():
    today_date = [datetime.now(timezone('Asia/Jakarta')).strftime("%A"), datetime.now(timezone('Asia/Jakarta')).strftime(" · %B %d, %Y · %I:%M %p")]
    users = User.query.all()
    flash(f"You are logged in as {current_user.name.title()}", 'success')
    return render_template('admin/user_profiles.html', today_date=today_date, users=users)

@admin.route('/users/edit_user/<int:user_id>', methods=['GET', 'POST'])
@login_required
def edit_user(user_id):
    prev = request.referrer
    if current_user.user_type != 0:
        abort(403)
    user = User.query.filter_by(id=user_id).first()
    if user is None:
        flash(f"User not found!", 'danger')
        return redirect(url_for('admin.user_profiles'))
    
    editUserForm = EditUserForm()
    if request.method == "POST":
        name = editUserForm.name.data
        email = editUserForm.email.data
        role = editUserForm.user_type.data
        active = editUserForm.active_field.data
        profile_picture = request.files['profile_picture']
        phone = None
        room = None
        user_class = None
        
        if user.user_type == 2:
            phone = editUserForm.phone.data
            room = editUserForm.room.data.id
            user_class = editUserForm.user_class.data.id
        if active == '1':
            active = True
        else:
            active = False
            
        if str(name) == str(user.name) and str(email) == str(user.email) and str(phone) == str(user.phone) and str(room) == str(user.room) and str(role) == str(user.user_type) and str(user_class) == str(user.user_class_id) and str(active) == str(user.active) and profile_picture.filename == '':
            flash(f"No changes made!", 'info')
            return redirect(prev)
        
        if email == None or email == '': 
            flash(f"Email cannot be empty!", 'danger')
            return redirect(url_for('admin.edit_user', user_id=user_id))
        
        if user.email != email:
            check_email = User.query.filter_by(email=email).first()
            if check_email is not None:
                flash(f"Email {email} already exists, cannot change1", 'danger')
                return redirect(url_for('admin.edit_user', user_id=user_id))

        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, email):
            flash(f"Email {email} is not valid!", 'danger')
            return redirect(url_for('admin.edit_user', user_id=user_id))
            
        if name == '' or name == None:
            flash(f"Name cannot be empty!", 'danger')
            return redirect(url_for('admin.edit_user', user_id=user_id))
        
        if len(name) < 3 or len(name) > 50:
            flash(f"Name must be between 3 and 50 characters!", 'danger')
            return redirect(url_for('admin.edit_user', user_id=user_id))
        
        if role == None or role == '':
            flash(f"Role cannot be empty!", 'danger')
            return redirect(url_for('admin.edit_user', user_id=user_id))
        
        if user.user_type == 2 and role == '2':
            phone_pattern = r'^08[0-9]{9,}$'
            if phone == None or phone == '':
                flash(f"Phone cannot be empty!", 'danger')
                return redirect(url_for('admin.edit_user', user_id=user_id))
            
            if len(phone) < 10 or len(phone) > 13:
                flash(f"Phone must be between 10 and 13 characters!", 'danger')
                return redirect(url_for('admin.edit_user', user_id=user_id))
            
            if not re.match(phone_pattern, phone):
                flash(f"Phone number must be a 10-digit number!", 'danger')
                return redirect(url_for('admin.edit_user', user_id=user_id))
            
            if room == None or room == '':
                flash(f"Room cannot be empty!", 'danger')
                return redirect(url_for('admin.edit_user', user_id=user_id))
            
            check_room = UserRoom.query.filter_by(id=room).first()
            if check_room is None:
                flash(f"Room {room.name} does not exist!", 'danger')
                return redirect(url_for('admin.edit_user', user_id=user_id))
                
        ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
        
        if profile_picture.filename != '':
            output_size = (500, 500)
            if not '.' in profile_picture.filename or profile_picture.filename.rsplit('.', 1)[1].lower() not in ALLOWED_EXTENSIONS:
                flash(f"Profile picture must be a jpg or png file!", 'danger')
                return redirect(url_for('admin.add_user'))
            if user.profile_picture != 'default.png':
                if os.path.exists(os.path.join(app.config['UPLOAD_FOLDER'], user.profile_picture)):
                    os.remove(os.path.join(app.config['UPLOAD_FOLDER'], user.profile_picture))
            user.profile_picture = profile_picture.filename
            # pic_filename = secure_filename(profile_picture.filename)
            pic_name = str(uuid.uuid1()) + "_" + str(user.id) + '.jpg'
            profile_picture.save(os.path.join(app.config['UPLOAD_FOLDER'], pic_name))
            user.profile_picture = pic_name
            i = Image.open(os.path.join(app.config['UPLOAD_FOLDER'], pic_name))
            i.thumbnail(output_size)
            i.save(os.path.join(app.config['UPLOAD_FOLDER'], pic_name))
        
        user.email = email
        user.name = name
        user.email = email
        user.phone = phone
        user.room = room
        user.user_type = role
        user.user_class_id = user_class
        user.active = active
        
        # if role != 2: 
        #     user.user_class_id = None
        #     user.room = None
        #     user.phone = None
        #     user.active = True
        # print(email, name, phone, room, role, user_class, active, profile_picture)
        # print(user.email, user.name, user.phone, user.room, user.user_type, user.user_class_id, user.active, user.profile_picture)
        db.session.commit()
        flash(f"User {user.name.title()} has been updated!", 'success')
        # return redirect(url_for('admin.edit_user', user_id=user_id))
        return redirect(prev)
        
    
    return render_template('admin/edit_user.html', user=user, editUserForm=editUserForm)

@admin.route('/users/change_password/<int:user_id>', methods=['GET', 'POST'])
@login_required
def change_password(user_id):
    if current_user.user_type != 0:
        abort(403)
    user = User.query.filter_by(id=user_id).first()
    if user is None:
        flash(f"User not found!", 'danger')
        return redirect(url_for('admin.user_profiles'))
    
    changeUserPasswordForm = ChangeUserPasswordForm()
    if request.method == "POST":
        if changeUserPasswordForm.validate_on_submit():
            password = changeUserPasswordForm.password.data
            confirm = changeUserPasswordForm.confirm.data
            if password != confirm:
                flash(f"Password and Confirm Password must be the same!", 'danger')
                return redirect(url_for('admin.change_password', user_id=user_id))
            user.password = bcrypt.generate_password_hash(password).decode('utf-8')
            db.session.commit()
            print(user.password)
            flash(f"User {user.name.title()}'s password has been changed!", 'success')
            return redirect(url_for('admin.user_profiles'))
        else:
            flash(f"Password and Confirm Password must be the same!", 'danger')
            return redirect(url_for('admin.change_password', user_id=user_id))
    
    return render_template('admin/change_password.html', user=user, changeUserPasswordForm=changeUserPasswordForm)

@admin.route('/users/user_rooms', methods=['GET', 'POST'])
@login_required
def user_rooms():
    if current_user.user_type != 0:
        abort(403)
    
    rooms = UserRoom.query.all()
    editRoomForm = EditRoomForm()
    addRoomForm = AddRoomForm()
    
    if request.method == 'POST':
        action = request.args.get('action')
        
        if action == 'add':
            name = addRoomForm.name.data
            if name == '' or name == None:
                flash(f"Name cannot be empty!", 'danger')
                return redirect(url_for('admin.user_rooms'))
            
            if len(name) < 3 or len(name) > 50:
                flash(f"Name must be between 3 and 50 characters!", 'danger')
                return redirect(url_for('admin.user_rooms'))
            
            check_name = UserRoom.query.filter_by(name=name).first()
            if check_name is not None:
                flash(f"Room {name} already exists!", 'danger')
                return redirect(url_for('admin.user_rooms'))
            
            room = UserRoom(name=name)
            db.session.add(room)
            db.session.commit()
            flash(f"Room {name} has been added!", 'success')
            return redirect(url_for('admin.user_rooms'))
        
        if action == 'edit':
            name = editRoomForm.name.data
            id = editRoomForm.id.data
            
            if name == '' or name == None:
                flash(f"Name cannot be empty!", 'danger')
                return redirect(url_for('admin.user_rooms'))
            
            if len(name) < 3 or len(name) > 50:
                flash(f"Name must be between 3 and 50 characters!", 'danger')
                return redirect(url_for('admin.user_rooms'))
            
            data = UserRoom.query.filter_by(id=id).first()
            check_name = UserRoom.query.filter_by(name=name).first()
            
            if data is None:
                flash(f"Room not found!", 'danger')
                return redirect(url_for('admin.user_rooms'))
            
            if data.name == name:
                flash(f"No changes made!", 'info')
                return redirect(url_for('admin.user_rooms'))
            
            if check_name is not None:
                flash(f"Room {name} already exists!", 'danger')
                return redirect(url_for('admin.user_rooms'))
            
            data.name = name
            db.session.commit()
            flash(f"Room with id : {id} has been updated!", 'success')
            return redirect(url_for('admin.user_rooms'))
    return render_template('admin/user_rooms.html', rooms=rooms, editRoomForm=editRoomForm, addRoomForm=addRoomForm)

@admin.route('/users/user_room/<int:id>', methods=['GET', 'POST'])
@login_required
def user_room(id):
    if current_user.user_type != 0:
        abort(403)
        
    room = UserRoom.query.filter_by(id=id).first()
    if room is None:
        flash(f"Room not found!", 'danger')
        return redirect(url_for('admin.user_rooms'))
    
    return render_template('admin/user_room.html', room=room)

@admin.route('/users/user_rooms/delete_room/<int:id>', methods=['GET', 'POST'])
@login_required
def delete_room(id):
    if current_user.user_type != 0:
        abort(403)
    room = UserRoom.query.filter_by(id=id).first()
    if room is None:
        flash(f"Room not found!", 'danger')
        return redirect(url_for('admin.user_rooms'))
    
    if request.method == 'POST':
        csrf_token = session.get('csrf_token')
        if not csrf_token or csrf_token != request.form.get('csrf_token'):
            abort(403)
        db.session.delete(room)
        db.session.commit()
        flash(f"Room {room.name} has been deleted!", 'success')
        return redirect(url_for('admin.user_rooms'))
    
    return render_template('admin/delete_room.html', room=room)

@admin.route('/api/get_registration_profiles', methods=['GET'])
def get_registration_profiles():
    if not current_user.is_authenticated:
        abort(403)
    if current_user.user_type != 0:
        abort(403)
    registration_profiles = RegistrationProfile.query.all()

    data = []
    for profile in registration_profiles:
        profile_data = OrderedDict([
            ('ID', profile.id),
            ('Email', profile.email),
            ('Name', profile.name),
            ('Phone', profile.phone),
            ('Room', profile.room),
            ('Class', profile.user_class)
        ])
        data.append(profile_data)
    return json.dumps(data)

@admin.route('/api/activate_user', methods=['POST'])
def activate_user():
    if not current_user.is_authenticated:
        abort(403)
    if current_user.user_type != 0:
        abort(403)
    
    if request.method == "POST":
        checked = request.json.get('checked')
        counter = 0
        user = None
        for _id in checked:
            user = User.query.filter_by(id=_id).first()
            if user is None:
                continue
            
            if user.active == 1:
                continue
            
            user.active = 1
            db.session.commit()
            counter += 1
        if counter == 1:
            flash(f"{user.name.title()} has been activated!", 'info')
        elif counter == 0:
            flash(f"No changes made!", 'info')
        else:
            flash(f"{counter} User has been activated!", 'info')
    return make_response(jsonify({'status': 'success'}), 200)

@admin.route('/api/deactivate_user', methods=['POST'])
def deactivate_user():
    if not current_user.is_authenticated:
        abort(403)
    if current_user.user_type != 0:
        abort(403)
        
    if request.method == "POST":
        checked = request.json.get('checked')
        counter = 0
        user = None
        for _id in checked:
            user = User.query.filter_by(id=_id).first()
            if user is None:
                continue
            
            if user.active == 0:
                continue
            
            if user.user_type == 0:
                flash(f"Cannot deactivate {user.name.title()}!", 'info')
                continue
            
            user.active = 0
            db.session.commit()
            counter += 1
        if counter == 1:
            flash(f"{user.name.title()} has been deactivated!", 'info')
        elif counter == 0:
            flash(f"No changes made!", 'info')
        else:
            flash(f"{counter} User has been deactivated!", 'info')
    return make_response(jsonify({'status': 'success'}), 200)

@admin.route('/api/approve_registration_profile', methods=['POST'])
def approve_registration_profile():
    if not current_user.is_authenticated:
        abort(403)
    if current_user.user_type != 0:
        abort(403)
        
    if request.method == "POST":
        checked = request.json.get('checked')
        if len(checked) == 0:
            return make_response(jsonify({'status': 'failed'}), 200)
        counter = 0
        register_info = None
        for tmp in checked: 
            register_info = RegistrationProfile.query.filter_by(id=tmp).first()
            if register_info is None:
                continue
            room_id = UserRoom.query.filter_by(name=register_info.room).first().id
            if room_id is None:
                continue
            class_id = UserClass.query.filter_by(name=register_info.user_class).first().id
            user = User(name=register_info.name, email=register_info.email, password=register_info.password, active=1, phone=register_info.phone, room=room_id, user_class_id=class_id, date_created=datetime.now(timezone('Asia/Jakarta')))
            db.session.add(user)
            db.session.delete(register_info)
            db.session.commit()
            counter += 1
        if counter == 0:
            flash(f"No changes made!", 'info')
        elif counter == 1:
            flash(f"{register_info.name.title()}'s registration profile has been approved", 'info')
        else:
            flash(f"{counter} Registration profile has been approved", 'info')
    return make_response(jsonify({'status': 'success'}), 200)

@admin.route('/api/reject_registration_profile', methods=['POST'])
def reject_registration_profile():
    if not current_user.is_authenticated:
        abort(403)
    if current_user.user_type != 0:
        abort(403)
        
    if request.method == 'POST':
        checked = request.json.get('checked')
        if len(checked) == 0:
            return make_response(jsonify({'status': 'failed'}), 200)
        counter = 0
        register_info = None
        for tmp in checked:
            register_info = RegistrationProfile.query.filter_by(id=tmp).first()
            if register_info is None:
                continue
            db.session.delete(register_info)
            db.session.commit()
            counter += 1
        if counter == 0:
            flash(f"No changes made!", 'info')
        elif counter == 1:
            flash(f"{register_info.name.title()}'s registration profile has been rejected", 'info')
        else: 
            flash(f"{counter} Registration profile has been rejected", 'info')
    return make_response(jsonify({'status': 'success'}), 200)

@admin.route('/api/product_detail', methods=['GET'])
def api_get_product_detail():
    barcode = request.args.get('barcode')
    if not current_user.is_authenticated:
        make_response(jsonify({'status': 403}), 403)
    if current_user.user_type != 0:
        make_response(jsonify({'status': 403}), 403)
        
    product = Product.query.filter_by(barcode=barcode).first()
    if product is None:
        return make_response(jsonify({'status': 404}), 404)
    
    data = {
        'id' : product.id,
        'barcode': product.barcode,
        'name' : product.name,
        'code' : product.code,
        'stock' : product.stock,
        'sold' : product.sold,
        'price' : product.price,
        'product_type' : product.product_type_name,
    }
    return make_response(jsonify({'data' : data, 'status': 200}), 200)

@admin.route('/delete_user', methods=['POST', 'GET'])
@admin.route('/delete_user', methods=['POST', 'GET'])
@login_required
def delete_user():
    if current_user.user_type != 0:
        abort(403)
    
    flash(f"This feature is still under development, try again later!", 'info')
    return redirect(url_for('admin.user_profiles'))
        
    user_id = request.args.get('id')
    users = []
    for _id in user_id:
        user = User.query.filter_by(id=_id).first()
        if user is None:
            continue
        users.append(user)
    print(users)
    return render_template('admin/delete_user.html', ids=user_id)

@admin.route('/api/get_product_data', methods=['GET', 'POST'])
@login_required
def api_get_product_data():
    search = request.args.get('search')
    page = request.args.get('page')

    products_query = Product.query.filter(
        (Product.name.ilike(f"%{search}%")) |
        (Product.barcode.ilike(f"%{search}%"))
    )

    per_page = 10
    products_paginated = products_query.paginate(page=int(page), per_page=per_page)

    results = []
    for product in products_paginated.items:
        results.append({
            'id': product.barcode,
            'text': product.barcode + " - " + product.name,
            'name': product.name,
            'real_id': product.id,
            'stock': product.stock,
            'price': product.price,
        })

    return jsonify({
        'results': results,
        'pagination': {
            'more': products_paginated.has_next
        }
    })

@admin.route('/api/get_customer_data', methods=['GET', 'POST'])
@login_required
def api_get_customer_data():
    search = request.args.get('search')
    page = request.args.get('page')

    users_query = User.query.filter(
        (User.name.ilike(f"%{search}%")) |
        (User.email.ilike(f"%{search}%"))
    ).filter_by(user_type=2)

    per_page = 10
    users_paginated = users_query.paginate(page=int(page), per_page=per_page)

    results = []
    for user in users_paginated.items:
        results.append({
            'id': user.id,
            'text': user.name + " - " + user.user_class_name,
            'name': user.name,
            'email': user.email,
        })

    return jsonify({
        'results': results,
        'pagination': {
            'more': users_paginated.has_next
        }
    })
    


@app.route('/admin/api/submit_product_transaction', methods=['POST'])
@login_required
def api_submit_product_transaction():
    if current_user.user_type != 0:
        return jsonify({'status': 'fail', 'message': 'Access denied'}), 403

    data = request.get_json()
    print(data)
    customer = data['customer']
    product_bought = data['productTransactionDetails']
    payment_method = data['paymentMethod']
    
    print(customer)

    # Validate the data (you can add more validation as needed)
    if not customer or not payment_method or not product_bought:
        return jsonify({'status': 'fail', 'message': 'Invalid data'}), 400

    if User.query.filter_by(id=customer).first() is None:
        return jsonify({'status': 'fail', 'message': 'Customer not found'}), 404
    
    for product in product_bought:
        temp = Product.query.filter_by(id=product['id']).first()
        if temp is None:
            return jsonify({'status': 'fail', 'message': 'Product not found'}), 404
        
        if temp.stock < int(product['quantity']):
            return jsonify({'status': 'fail', 'message': 'Product out of stock'}), 400
    transaction_code = product_transaction_code_generator()
    productTransaction = ProductTransaction(payment_method=payment_method, cashier_id=current_user.id, customer_id=customer, transaction_code=transaction_code)
    db.session.add(productTransaction)
    db.session.commit()
    
    for product in product_bought:
        temp = Product.query.filter_by(id=product['id']).first()
        temp.stock -= product['quantity']
        temp.sold += product['quantity']
        db.session.commit()
        productTransactionDetail = ProductTransactionDetail(product_id=product['id'], transaction_id=productTransaction.id, quantity=product['quantity'], current_price=product['price'])
        db.session.add(productTransactionDetail)
        db.session.commit()
    flash('Transaction processed successfully', 'success')
    
    # Assuming the transaction was successful
    return jsonify({'status': 'success', 'message': 'Transaction processed successfully'}), 200
