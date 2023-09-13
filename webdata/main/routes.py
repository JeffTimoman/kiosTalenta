from flask import Blueprint, render_template, url_for, flash, redirect, request, abort

from webdata import db, bcrypt
from flask_login import login_user, current_user, logout_user, login_required
from webdata.main.forms import LoginForm, RegistrationForm

from webdata.models import User, RegistrationProfile
from pytz import timezone
from datetime import datetime

main = Blueprint('main', __name__)

# import logging
# logging.basicConfig()
# logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)

@main.route("/")
@login_required
def index():
    if current_user.user_type == 0:
        return redirect(url_for('admin.index'))
    
    if current_user.user_type == 1:
        return 'Cashier Page'
    
    if current_user.user_type == 2:
        return 'Customer Page'
 
    if current_user.user_type == 3:
        return 'Customer Page'

@main.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    loginForm = LoginForm()
    registrationForm = RegistrationForm()
    
    if request.method == 'POST':
        if request.args.get('action') == 'register':
            user = User.query.filter_by(email=registrationForm.email.data).first()
            if user: 
                flash('That email is taken. Please choose a different one.', 'danger')
                return redirect(url_for('main.login'))
            user = RegistrationProfile.query.filter_by(email=registrationForm.email.data).first()
            if user:
                flash('That email is taken. Please choose a different one.', 'danger')
                return redirect(url_for('main.login'))
            registration = RegistrationProfile(email=registrationForm.email.data, name=registrationForm.name.data, password=str(bcrypt.generate_password_hash(registrationForm.password.data).decode('utf-8')), phone=registrationForm.phone.data, room=registrationForm.room.data.name, user_class=registrationForm.user_class.data.name)
            print(registration.room)
            db.session.add(registration)
            db.session.commit()
            flash('Your account has been created! Wait for admin to approve your account', 'success')
            return redirect(url_for('main.login'))
        
        if request.args.get('action') == 'login' and loginForm.validate_on_submit():
            user = User.query.filter_by(email=loginForm.email.data).first()
            if user and user.user_type != 0 and user.active == False:
                flash('Your account is not active. Please contact admin', 'danger')
                return redirect(url_for('main.login'))
            
            if user and bcrypt.check_password_hash(user.password, loginForm.password.data):        
                login_user(user, remember=loginForm.remember.data)
                user.last_login = datetime.now(timezone('Asia/Jakarta'))
                user.last_ip = request.remote_addr
                db.session.commit()
                return redirect(url_for('main.index'))
            else : 
                flash('Login Unsuccessful. Please check email and password', 'danger')
                return redirect(url_for('main.login'))
    return render_template('/main/login.html', title='Login', loginForm=loginForm, registrationForm=registrationForm)

@main.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.login'))

