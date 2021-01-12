import os
from datetime import timedelta

# Determine the folder of the top-level directory of this project
BASEDIR = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    FLASK_ENV = 'development'
    DEBUG = False
    TESTING = False
    SECRET_KEY = os.getenv('SECRET_KEY', default='02\xa1\xa8h\x10\xbc\x10\xba/\xccft!\x84=W\xafWk\xe5\\\xee\xc6\xfe\x184\xe8\xfam\xf4 ')
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL',
                                        default=f"sqlite:///{os.path.join(BASEDIR, 'instance', 'app.db')}")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    BCRYPT_LOG_POUNDS = 4
    WTF_CSRF_ENABLED = True
    REMEMBER_COOKIE_DURATION = timedelta(days=14)
    MAIL_SERVER = 'smtp.googlemail.com'
    MAIL_PORT = 465
    MAIL_USE_TLS = False
    MAIL_USE_SSL = True
    MAIL_USERNAME = os.getenv('MAIL_USERNAME', default='flaskcoursetest@gmail.com')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD', default='FlaskCourseTest@2020')
    MAIL_DEFAULT_SENDER = os.getenv('MAIL_USERNAME', default='flaskcoursetest@gmail.com')
    ALPHA_VANTAGE_API_KEY = os.getenv('ALPHA_VANTAGE_API_KEY', default='9FDV49MCJYZY8J19')
    LOG_TO_STDOUT = os.getenv('LOG_TO_STDOUT', default=False)
class ProductionConfig(Config):
    FLASK_ENV = 'production'
    

class DevelopmentConfig(Config):
    DEBUG = True


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.getenv('TEST_DATABASE_URI',
                                        default=f"sqlite:///{os.path.join(BASEDIR, 'instance', 'test.db')}")