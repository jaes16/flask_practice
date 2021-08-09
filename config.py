import os
from dotenv import load_dotenv


basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))

class Config(object):
	# this crytographic key is used to create signatures or tokens to prevent CSRF attacks
	SECRET_KEY = os.environ.get('SECRET_KEY') or 'you_will_never_not_guess_no_nothing'
	# provides the location of the application's database
	SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
	'sqlite:///' + os.path.join(basedir, 'app.db')
	# don't signal the application every time a change is about to be made in the database
	SQLALCHEMY_TRACK_MODIFICATIONS = False

	# adding mail server details, important for emailing error details and stack details when errors occur during deployment of the server.
	MAIL_SERVER = os.environ.get('MAIL_SERVER')
	MAIL_PORT = int(os.environ.get('MAIL_PORT') or 25)
	MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS') is not None
	MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
	MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')

	POSTS_PER_PAGE = 20

	TOKEN_EXPIRATION = 600

	ADMINS = ['flask_practice@flask_pratice.com']
	LANGUAGES = ['en', 'es']

	MS_TRANSLATOR_KEY = os.environ.get('MS_TRANSLATOR_KEY')
	MS_TRANSLATOR_REGION = 'koreacentral'
