# the start of all things flask
from flask import Flask, request
from config import Config
# for sql database
from flask_sqlalchemy import SQLAlchemy
# for better relational database migration
# because relational databases use classes and objects, changes in those classes and objects require changes in the database to update to those new changes
from flask_migrate import Migrate
from flask_login import LoginManager
import logging
# for debugging, sending errors to email or logging to file
from logging.handlers import SMTPHandler, RotatingFileHandler
import os
from flask_mail import Mail
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from flask_babel import Babel


app = Flask(__name__)
app.config.from_object(Config)
# database
db = SQLAlchemy()
# migration engine
migrate = Migrate()

# loginManager from flask_login requires implementation of these four properties, but otherwise can support any user class
# is_authenticated: a property that is True if the user has valid credentials or False otherwise.
# is_active: a property that is True if the user's account is active or False otherwise.
# is_anonymous: a property that is False for regular users, and True for a special, anonymous user.
# get_id(): a method that returns a unique identifier for the user as a string (unicode, if using Python 2).
login = LoginManager()
login.login_view = 'auth.login'
login.login_message = 'Please log in to access this page.'
mail = Mail()
# for css facelift
bootstrap = Bootstrap()
# for timezone conversion
moment = Moment()
# for translations
babel = Babel()


def create_app(config_class=Config):
	db.init_app(app)
	migrate.init_app(app, db)
	login.init_app(app)
	mail.init_app(app)
	bootstrap.init_app(app)
	moment.init_app(app)
	babel.init_app(app)

	from app.errors import bp as errors_bp
	app.register_blueprint(errors_bp)
	from app.auth import bp as auth_bp
	app.register_blueprint(auth_bp)
	from app.main import bp as main_bp
	app.register_blueprint(main_bp)


	# if the server is not running in debug mode, we need another way of receiving errors: emails
	if not app.debug:
		# if there is a dictionary containing configuration options for the mail_server. We added it in the config
		if app.config['MAIL_SERVER']:
			auth = None
			if app.config['MAIL_USERNAME'] or app.config['MAIL_PASSWORD']:
				auth = (app.config['MAIL_USERNAME'], app.config['MAIL_PASSWORD'])
			secure = None
			if app.config['MAIL_USE_TLS']:
				secure = ()
			mail_handler = SMTPHandler(
				mailhost=(app.config['MAIL_SERVER'], app.config['MAIL_PORT']),
				fromaddr='no-reply@' + app.config['MAIL_SERVER'],
				toaddrs=app.config['ADMINS'], subject='Microblog Failure',
				credentials=auth, secure=secure)
			mail_handler.setLevel(logging.ERROR)
			app.logger.addHandler(mail_handler)

		# we want to have a log file for the server, as we may want to see failure conditions that do not lead to Python exceptions
		if not os.path.exists('logs'): # if there is no logs directory, create one
			os.mkdir('logs')
		# rotating logs ensure that the file does not exceed a certain length (in this case 10kb,) and allows backups
		file_handler = RotatingFileHandler('logs/microblog.log', maxBytes=10240, backupCount=10)
		file_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
		file_handler.setLevel(logging.INFO)
		app.logger.addHandler(file_handler)

		# the levels of logging are: DEBUG, INFO, WARNING, ERROR and CRITICAL.
		app.logger.setLevel(logging.INFO)
		app.logger.info('Microblog startup')

	return app

@babel.localeselector
def get_locale():
	# client request sends something like this: Accept-Language: da, en-gb;q=0.8, en;q=0.7, q being the weight
	#return request.accept_languages.best_match(flask_app.config['LANGUAGES'])
	return 'es'

from app import models
