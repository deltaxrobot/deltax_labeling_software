import os
 
class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'cc-ma-doan-ra-dc'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///database.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAX_CONTENT_LENGTH = 160 * 1024 * 1024
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 465
    MAIL_USERNAME = '3ddanang.net@gmail.com'
    MAIL_PASSWORD = 'IMWI052841566'
    MAIL_USE_TLS = False
    MAIL_USE_SSL = True
    MAIL_DEFAULT_SENDER = '3ddanang.net@gmail.com'