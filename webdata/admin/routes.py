from flask import Blueprint, render_template, url_for, flash, redirect, request, abort, jsonify, make_response, session

from webdata import db, bcrypt, app
from flask_login import login_user, current_user, logout_user, login_required
from webdata.main.forms import LoginForm, RegistrationForm

from flask_cors import CORS, cross_origin

from werkzeug.utils import secure_filename

from webdata.models import User, RegistrationProfile, UserClass, UserRoom, Product

from webdata.admin.forms import EditUserForm, ChangeUserPasswordForm, AddUserForm, EditClassForm, AddClassForm, EditRoomForm, AddRoomForm, AddProductForm

from pytz import timezone
from datetime import datetime
from collections import OrderedDict
from PIL import Image

import uuid as uuid
import os
import json
import re

admin = Blueprint('admin', __name__)

CORS(admin, resources={r"/api/*": {"origins": "*"}})

def save_image(form_picture, user_id):
    pic_filename = secure_filename(form_picture.filename)
    pic_name = str(uuid.uuid1()) + "_" + str(user_id)
    pic_path = os.path.join(app.root_path, 'static/profile_pictures', pic_name)
    form_picture.save(pic_path)
    return pic_name

@admin.route("/")
@login_required
def index():
    if current_user.user_type != 0:
        abort(403)
    return render_template('admin/index.html')



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
    return render_template('admin/add_product.html', addProductForm=addProductForm)

@admin.route("/products/product_types")
@login_required
def product_types():
    return "test"



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
            # output_size = (125, 125)
            if not '.' in profile_picture.filename or profile_picture.filename.rsplit('.', 1)[1].lower() not in ALLOWED_EXTENSIONS:
                flash(f"Profile picture must be a jpg or png file!", 'danger')
                return redirect(url_for('admin.add_user'))
            pic_name = str(uuid.uuid1()) + "_" + str(user.id) 
            profile_picture.save(os.path.join(app.config['UPLOAD_FOLDER'], pic_name))
            user.profile_picture = pic_name
            
            # i = Image.open(os.path.join(app.config['UPLOAD_FOLDER'], pic_name))
            # i.thumbnail(output_size)
            # i.save(os.path.join(app.config['UPLOAD_FOLDER'], pic_name))
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
            if not '.' in profile_picture.filename or profile_picture.filename.rsplit('.', 1)[1].lower() not in ALLOWED_EXTENSIONS:
                flash(f"Profile picture must be a jpg or png file!", 'danger')
                return redirect(url_for('admin.add_user'))
            if user.profile_picture != 'default.png':
                if os.path.exists(os.path.join(app.config['UPLOAD_FOLDER'], user.profile_picture)):
                    os.remove(os.path.join(app.config['UPLOAD_FOLDER'], user.profile_picture))
            user.profile_picture = profile_picture.filename
            # pic_filename = secure_filename(profile_picture.filename)
            pic_name = str(uuid.uuid1()) + "_" + str(user.id)
            profile_picture.save(os.path.join(app.config['UPLOAD_FOLDER'], pic_name))
            user.profile_picture = pic_name
        
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