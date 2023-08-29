from flask import Blueprint, render_template, url_for, flash, redirect, request, abort, session
from flask_login import login_user, current_user, logout_user, login_required

from webdata import db, bcrypt
from webdata.models import User, UserClass

from flask_cors import CORS, cross_origin
from flask import jsonify

api = Blueprint('api', __name__)

CORS = CORS(api, resources={r"/api/*": {"origins": "*"}})

tokens = 'louwis_api'
@api.route('/get_all_users', methods=['GET'])
def get_all_users():
    users = User.query.all()
    # get only name and email
    output = []
    for user in users:
        user_data = {}
        user_data['id'] = user.id
        user_data['name'] = user.name
        user_data['email'] = user.email
        output.append(user_data)
        
    return jsonify({'users' : output})

@api.route('/get_user/<id>', methods=['GET'])
def get_user(id):
    user = User.query.get(id)
    # tokens = request.headers.get('token')
    tokens = request.args.get('token')
    if tokens != 'louwis_api':
        return jsonify({'message' : 'Invalid token!', 'status': 403}, 403)
    if not user:
        return jsonify({'message' : 'No user found!', 'status': 403}, 403)
    
    user_data = {}
    user_data['id'] = user.id
    user_data['name'] = user.name
    user_data['email'] = user.email
    user_data['phone'] = user.phone
    user_data['room'] = user.room
    user_data['user_type'] = user.user_type
    user_data['user_class'] = user.user_class
    user_data['profile_picture'] = user.profile_picture
    user_data['active'] = user.active
    user_data['last_ip'] = user.last_ip
    user_data['date_created'] = user.date_created
    user_data['last_login'] = user.last_login
    
    return jsonify({'user' : user_data, 'status': 200}, 200)