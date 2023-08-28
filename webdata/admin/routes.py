from flask import Blueprint, render_template, url_for, flash, redirect, request, abort, jsonify, make_response

from webdata import db, bcrypt, app
from flask_login import login_user, current_user, logout_user, login_required
from webdata.main.forms import LoginForm, RegistrationForm

from flask_cors import CORS, cross_origin

from werkzeug.utils import secure_filename

from webdata.models import User, RegistrationProfile, UserClass

from webdata.admin.forms import EditUserForm, ChangeUserPasswordForm, AddUserForm

from pytz import timezone
from datetime import datetime
from collections import OrderedDict

import uuid as uuid
import os
import json
import re

admin = Blueprint('admin', __name__)

CORS(admin, resources={r"/api/*": {"origins": "*"}})

@admin.route("/")
@admin.route("/users")
@login_required
def index():
    if current_user.user_type != 0:
        abort(403)
    return render_template('admin/index.html')

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
    return render_template('admin/add_user.html', addUserForm=addUserForm)


@admin.route("/users/user_profiles")
@login_required
def user_profiles():
    today_date = [datetime.now(timezone('Asia/Jakarta')).strftime("%A"), datetime.now(timezone('Asia/Jakarta')).strftime(" · %B %d, %Y · %I:%M %p")]
    users = User.query.with_entities(
        User.id,
        User.name,
        User.email,
        User.date_created,
        User.last_login,
        User.last_ip,
        User.user_type,
        User.active,
        User.room
    ).all()
    flash(f"You are logged in as {current_user.name.title()}", 'success')
    return render_template('admin/user_profiles.html', today_date=today_date, users=users)

@admin.route('/users/edit_user/<int:user_id>', methods=['GET', 'POST'])
@login_required
def edit_user(user_id):
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
            room = editUserForm.room.data
            user_class = editUserForm.user_class.data.id
        
        if active == '1':
            active = True
        else:
            active = False
            
        if str(name) == str(user.name) and str(email) == str(user.email) and str(phone) == str(user.phone) and str(room) == str(user.room) and str(role) == str(user.user_type) and str(user_class) == str(user.user_class_id) and str(active) == str(user.active) and profile_picture.filename == '':
            flash(f"No changes made!", 'info')
            return redirect(url_for('admin.user_profiles'))
        
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
            
            room_pattern = r'^(A|B|AB)[0-9]{3}$'
            if room == None or room == '':
                flash(f"Room cannot be empty!", 'danger')
                return redirect(url_for('admin.edit_user', user_id=user_id))
            
            if len(room) < 4 or len(room) > 5:
                flash(f"Room must be between 4 and 5 characters!", 'danger')
                return redirect(url_for('admin.edit_user', user_id=user_id))
            
            if not re.match(room_pattern, room):
                flash(f"Room must be a 4-digit/5-digit number!", 'danger')
                return redirect(url_for('admin.edit_user', user_id=user_id))      
        
        
        if profile_picture.filename != '':
            if user.profile_picture != 'default.png':
                if os.path.exists(os.path.join(app.config['UPLOAD_FOLDER'], user.profile_picture)):
                    os.remove(os.path.join(app.config['UPLOAD_FOLDER'], user.profile_picture))
            user.profile_picture = profile_picture.filename
            pic_filename = secure_filename(profile_picture.filename)
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
        return redirect(url_for('admin.user_profiles'))
        
    
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


@admin.route("/users/user_classes")
@login_required
def user_classes():
    today_date = [datetime.now(timezone('Asia/Jakarta')).strftime("%A"), datetime.now(timezone('Asia/Jakarta')).strftime(" · %B %d, %Y · %I:%M %p")]
    classes = UserClass.query.all()
    flash(f"You are logged in as {current_user.name.title()}", 'success')
    return render_template('admin/user_classes.html', today_date=today_date, classes=classes)


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
            class_id = UserClass.query.filter_by(name=register_info.user_class).first().id
            user = User(name=register_info.name, email=register_info.email, password=register_info.password, active=1, phone=register_info.phone, room=register_info.room, user_class_id=class_id, date_created=datetime.now(timezone('Asia/Jakarta')))
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