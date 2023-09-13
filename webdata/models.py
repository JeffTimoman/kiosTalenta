from datetime import datetime 
from pytz import timezone
# from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
# from flask import current_app, Flask
from flask_login import UserMixin
from webdata import db, app, login_manager

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class UserRoom(db.Model):
    __tablename__ = 'user_rooms'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), unique=True)
    date_created = db.Column(db.DateTime, default=datetime.now(timezone('Asia/Jakarta')))
    
    @property
    def user_count(self):
        return User.query.filter_by(room=self.id).count()
    
    @property 
    def member(self):
        return User.query.filter_by(room=self.id).all()
    
class UserClass(db.Model):
    __tablename__ = 'user_class'   
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), unique=True)
    date_created = db.Column(db.DateTime, default=datetime.now(timezone('Asia/Jakarta')))

    users = db.relationship('User', backref='user_class', cascade='all, delete-orphan')
    
    @property
    def user_count(self):
        return User.query.filter_by(user_class_id=self.id).count()

    @property
    def member(self):
        result = User.query.filter_by(user_class_id=self.id).all()
        return result
    def __repr__(self):
        return f"UserClass('{self.name}')"

class RegistrationProfile(db.Model):
    __tablename__ = 'registration_profiles'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(60), unique=True)
    name = db.Column(db.String(30))
    password = db.Column(db.String(60))
    phone = db.Column(db.String(20), default=None)
    room = db.Column(db.String(10), default=None)
    user_class = db.Column(db.String(30), default=None)
    
    def __repr__(self):
        return f"RegistrationProfile('{self.email}', '{self.name}', '{self.phone}', '{self.room}', '{self.user_class}')"

class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30))
    email = db.Column(db.String(60), unique=True)
    password = db.Column(db.String(60))
    date_created = db.Column(db.DateTime, default=datetime.now(timezone('Asia/Jakarta')))
    last_login = db.Column(db.DateTime, default=None)

    user_type = db.Column(db.Integer, default=2)
    active = db.Column(db.Boolean, default=True)
    last_ip = db.Column(db.String(20), default=None)
    #0 : ADMIN
    #1 : CASHIER
    #2 : CUSTOMER
    
    phone = db.Column(db.String(20), default=None)
    room = db.Column(db.Integer(), db.ForeignKey('user_rooms.id', ondelete='SET NULL'), default=None)
    profile_picture = db.Column(db.String(50), default="default.png")
    
    user_class_id = db.Column(db.Integer, db.ForeignKey('user_class.id', ondelete='CASCADE'), default=None)
    
    @property
    def user_class_name(self):
        result = UserClass.query.filter_by(id=self.user_class_id).first()
        return result.name
    
    @property
    def room_name(self):
        result = UserRoom.query.filter_by(id=self.room).first()
        if result is None:
            return "----"
        return result.name
    

    def __repr__(self):
        return f"User('{self.name}', '{self.email}', '{self.user_type}', '{self.active}')"
    
class ProductType(db.Model):
    __tablename__ = 'product_types'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30))
    date_created = db.Column(db.DateTime, default=datetime.now(timezone('Asia/Jakarta')))

    def __repr__(self):
        return f"ProductType('{self.name}')"
    
class Product(db.Model):
    __tablename__ = 'products'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    product_type = db.Column(db.Integer, db.ForeignKey('product_types.id', ondelete='CASCADE'))
    
    sold = db.Column(db.Integer, default=0)
    stock = db.Column(db.Integer)
    price = db.Column(db.Integer)

    code = db.Column(db.String(50))
    barcode = db.Column(db.String(50))

    date_created = db.Column(db.DateTime, default=datetime.now(timezone('Asia/Jakarta')))
    last_modified = db.Column(db.DateTime, default=datetime.now(timezone('Asia/Jakarta')))
    
    @property
    def product_type_name(self):
        result = ProductType.query.filter_by(id=self.product_type).first()
        return result.name

class ProductTransaction(db.Model):
    __tablename__ = 'product_transactions'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    cashier_id = db.Column(db.Integer, db.ForeignKey('users.id'), default= None)
    date_created = db.Column(db.DateTime, default=datetime.now(timezone('Asia/Jakarta')))
    
    transaction_type = db.Column(db.Integer)
    # 0 : OFFLINE
    # 1 : ONLINE

class ProductTransactionDetail(db.Model):
    __tablename__ = 'product_transaction_details'
    transaction_id = db.Column(db.Integer, db.ForeignKey('product_transactions.id'), primary_key=True, autoincrement=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), primary_key=True, autoincrement=False)
    
    quantity = db.Column(db.Integer)
    current_price = db.Column(db.Integer)
    
    date_created = db.Column(db.DateTime, default=datetime.now(timezone('Asia/Jakarta')))


class ProductTransactionAttribute(db.Model):
    __tablename__ = 'product_transaction_attributes'
    transaction_id = db.Column(db.Integer, db.ForeignKey('product_transactions.id'), primary_key=True, autoincrement=False)

    payment_status = db.Column(db.Integer, default=0)
    payment_prove = db.Column(db.String(100))
    payment_approve_by = db.Column(db.Integer, db.ForeignKey('users.id'), default= None)
    
    deliver_status = db.Column(db.Integer, default=0)
    deliver_by = db.Column(db.Integer, db.ForeignKey('users.id'), default= None)
    # 0 : PENDING
    # 1 : APPROVED

    date_created = db.Column(db.DateTime, default=datetime.now(timezone('Asia/Jakarta')))

class ShoppingCart(db.Model):
    __tablename__ = 'shopping_carts'
    # id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True, autoincrement=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), primary_key=True, autoincrement=False)
    quantity = db.Column(db.Integer)


class LaundryProvider(db.Model):
    __tablename__ = 'laundry_providers'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    date_created = db.Column(db.DateTime, default=datetime.now(timezone('Asia/Jakarta')))

class LaundryType(db.Model):
    __tablename__ = 'laundry_types'
    id = db.Column(db.Integer, primary_key=True)
    provider_id = db.Column(db.Integer, db.ForeignKey('laundry_providers.id'))

    name = db.Column(db.String(50))
    price = db.Column(db.Integer)
    
    date_created = db.Column(db.DateTime, default=datetime.now(timezone('Asia/Jakarta')))
    date_modified = db.Column(db.DateTime, default=datetime.now(timezone('Asia/Jakarta')))

class LaundryTransaction(db.Model):
    __tablename__ = 'laundry_transactions'
    id = db.Column(db.Integer, primary_key=True)
    
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    cashier_id = db.Column(db.Integer, db.ForeignKey('users.id'), default=None)
    
    laundry_type_id = db.Column(db.Integer, db.ForeignKey('laundry_types.id'))
    quantity = db.Column(db.Float)
    
    cloth_count = db.Column(db.Integer)
    pick_status = db.Column(db.Integer, default=0)

    date_created = db.Column(db.DateTime, default=datetime.now(timezone('Asia/Jakarta')))

class SuggestionBox(db.Model):
    __tablename__ = 'suggestion_boxes'
    id = db.Column(db.Integer, primary_key=True)
    message = db.Column(db.String(100))
    date_created = db.Column(db.DateTime, default=datetime.now(timezone('Asia/Jakarta')))
    