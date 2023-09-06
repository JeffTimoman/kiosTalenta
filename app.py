from webdata import app

def createsuperuser():
    from webdata.models import User
    from webdata import bcrypt
    from getpass import getpass
    from webdata import db
    
    email = input("Email: ")
    name = input("Name: ")
    password = bcrypt.generate_password_hash(getpass("Password: ")).decode('utf-8')
    user_type = 0
    active = 1
    
    user = User(name=name, email=email, password=password, user_type=user_type, active=active)
    db.session.add(user)
    db.session.commit()
    

if __name__ == "__main__":
#    app.run(debug=True, port=80, host='10.68.103.107')
#     app.run(debug=True, port=80, host='172.30.3.164')
    app.run(debug=True, port=8800, host='localhost')
