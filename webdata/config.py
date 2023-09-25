import os
class Config():
    def __init__(self):
        self.DB_PLATFORM = 'mysql+pymysql'
        # self.DB_PLATFORM = 'postgresql
        self.DB_SERVER = 'localhost'
        self.DB_NAME = 'kiosTalenta'
        self.DB_USERNAME = 'root'
        self.DB_PASSWORD = ''
        self.DB_PORT = '3306'
        
        self.SECRET_KEY = os.environ.get('SECRET_KEY')

        self.DB_URL = f'{self.DB_PLATFORM}://{self.DB_USERNAME}:{self.DB_PASSWORD}@{self.DB_SERVER}:{self.DB_PORT}/{self.DB_NAME}'
        self.UPLOAD_FOLDER = os.path.join(os.getcwd(), 'webdata/static/profile_pictures')
        self.SHOP_CODE = 'RTB1'
        # self.MAIL_PORT = 465
        # self.MAIL_SERVER = os.environ.get('MAIL_SERVER')
        # self.MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
        # self.MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
        # self.MAIL_USE_SSL = True
        # self.MAIL_USE_TLS = False