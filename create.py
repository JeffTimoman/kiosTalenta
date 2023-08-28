from flask import Flask, render_template, request
from webdata.models import *
from flask_sqlalchemy import SQLAlchemy
from webdata.config import Config
from flask_bcrypt import Bcrypt
import os, datetime
from random import randint
thisConfig = Config()
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = thisConfig.DB_URL
app.config["SQLALCHEMY_TRACK_MODIFICITION"] = False
db.init_app(app)
bcrypt = Bcrypt(app)

def main():
	print(thisConfig.DB_URL)
	db.create_all()

def main():
    user_classes = ['PPBP 1', 'PPBP 2', 'PPBP 3', 'PPBP 4', 'PPBP 5', 'PPBP 6', 'PPTI 14', 'PPTI 15', 'PPTI 16', 'PPTI 17', 'PPTI 18', 'PPTI 19']
    for classes in user_classes: 
        user_class = UserClass(name=classes)
        db.session.add(user_class)
        db.session.commit()

def main():
    password = bcrypt.generate_password_hash("admin123").decode('utf-8')
    user1 = User(name="admin", email="admin@admin.com", password=str(bcrypt.generate_password_hash("admin123").decode('utf-8')), user_type=0)
    user2 = User(name="cashier", email="cashier@admin.com",  password=str(bcrypt.generate_password_hash("admin123").decode('utf-8')), user_type=2)
    user3 = User(name="customer", email="customer@admin.com",  password=str(bcrypt.generate_password_hash("admin123").decode('utf-8')), user_type=3, active=1, phone="081373118686", room="B526", user_class_id=8, date_created=datetime.datetime.now())
    db.session.add(user1)
    db.session.add(user2)
    db.session.add(user3)
    db.session.commit()

def main():
    for i in range(100):
        email = f"customer{i+1}@admin.com"
        password = bcrypt.generate_password_hash("admin123").decode('utf-8')
        name = "customer"+str(i+1)
        phone = "081373118686"
        room = "B526"
        user_class = "ppti_15"
        user = RegistrationProfile(email=email, password=password, name=name, phone=phone, room=room, user_class=user_class)
        db.session.add(user)
        db.session.commit()
    
# def main():
#     password = bcrypt.generate_password_hash("admin123").decode('utf-8')
#     for i in range(100):
#         user = User(name="customer"+str(i)+"@gmail.com", email=f"customer{i}", password=password, user_type=3, active=randint(0,1))
#         db.session.add(user)
#         db.session.commit()
#         user_attribute = UserAttribute(user_id=user.id, phone="081373118686", room=f"B{str(i).zfill(3)}")
#         db.session.add(user_attribute)
#         db.session.commit()

# def main():
#     password = bcrypt.generate_password_hash("admin123").decode('utf-8')
#     for i in range(20):
#         user = User(name='Cashier'+str(i), email=f'cashier{i}@gmail.com', password=password, user_type=2, active=randint(0,1))
#         db.session.add(user)
#         db.session.commit() 
if __name__ == "__main__":
	with app.app_context():
		main()