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
#    app.run(debug=False, port=80, host='10.68.103.190')
    # app.run(debug=True, port=8080, host='0.0.0.0')
    app.run(debug=False, port=80, host='10.68.108.23')
    # app.run(debug=True, port=8800, host='localhost')
