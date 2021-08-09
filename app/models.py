from datetime import datetime
from time import time
import jwt # JSON web token, popular token standard
from app import db, login
# part of flask core package
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from hashlib import md5
from flask import current_app, url_for
from langdetect import detect, LangDetectException

# columns in tables can be accessed with Table.c.wanted_column or Table.column.wanted_column
followers = db.Table('followers',
	db.Column('follower_id', db.Integer, db.ForeignKey('user.id')),
	db.Column('followed_id', db.Integer, db.ForeignKey('user.id'))
)

# this class inherits from db.Model, a base class for all models
# UserMixin provides generic implementations for user classes
class User(UserMixin, db.Model):
	# fields, like the ones below, are created as instances of the db.Column class
	# the first argument is the field type
	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(64), index=True, unique=True)
	email = db.Column(db.String(120), index=True, unique=True)
	password_hash = db.Column(db.String(128))

	# defines a relationship, and is actually not a database field.
	# in one-to-many relationships, the "one" class houses the relationship, and is used as a convienient way to query and access the "many" classes
	# the backref allows the class on the other side of the relationship to reference this class with the appropriate reference tag
	# the lazy argument dictates how the query for the relationship is issued.
	posts = db.relationship('Post',	backref='author', lazy='dynamic')

	about_me = db.Column(db.String(140))
	last_seen = db.Column(db.DateTime, default=datetime.utcnow)

	followed = db.relationship('User', # Right side of this relationship. Follower or followed is another user
		secondary=followers, # configures association table with this relationship
		primaryjoin=(followers.c.follower_id == id), # links the left side with table
		secondaryjoin=(followers.c.followed_id == id), # links the right side with table
		backref=db.backref('followers', lazy='dynamic'), lazy='dynamic')

	# defines how to print this class
	def __repr__(self):
		return '<User {}>'.format(self.username)

	def set_password(self, password):
		self.password_hash = generate_password_hash(password)

	def check_password(self, password):
		return check_password_hash(self.password_hash, password)

	def follow(self, user):
		if not self.is_following(user):
			self.followed.append(user)

	def unfollow(self, user):
		if self.is_following(user):
			self.followed.remove(user)

	def is_following(self, user):
		return self.followed.filter(followers.c.followed_id == user.id).count() > 0

	def followed_posts(self):
		followed = Post.query.join( # join creates a temporary table with posts from all the users followed by another user
			followers, (followers.c.followed_id == Post.user_id)).filter( # find the posts from users followed by this user
				followers.c.follower_id == self.id)
		own = Post.query.filter_by(user_id=self.id)
		return followed.union(own).order_by(Post.timestamp.desc())

	def get_reset_password_token(self, expires_in=600):
		return jwt.encode({'reset_password': self.id, # first payload
			'exp': time() + expires_in}, # exp field is standard for jwt, and
			flask_app.config['SECRET_KEY'],
			algorithm='HS256') # HS256 is widely used for encoding

	@staticmethod
	def verify_reset_password_token(token):
		try:
			id = jwt.decode(token, flask_app.config['SECRET_KEY'],
				algorithms=['HS256'])['reset_password']
		except:
			return
		return User.query.get(id)

	def avatar(self, size):
		if size == 256:
			return url_for('static', filename='avatar256.png')
		elif size == 128:
			return url_for('static', filename='avatar128.png')
		elif size == 64:
			return url_for('static', filename='avatar64.png')
		elif size == 32:
			return url_for('static', filename='avatar32.png')
		elif size == 16:
			return url_for('static', filename='avatar16.png')
		#digest = md5(self.email.lower().encode('utf-8')).hexdigest()
		#return 'https://www.gravatar.com/avatar/{}?d=identicon&s={}'.format(digest, size)

class Post(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	body = db.Column(db.String(140))
	timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow) # passing the utcnow function not the result of it "utcnow" not "utcnow()". UTC is usually preferable

	# initializes user_id as a foreign key to user.id, referencing id from th user table. this particular call utilizes the database table name for the model instead of the name of the model class defined above
	user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

	language = db.Column(db.String(5), default = 'en')

	def get_language(self):
		if self.language is not None:
			return self.language
		l = ''
		try:
			l = detect(self.body)
		except LangDetectException:
			l = ''
		return l
	def __repr__(self):
		return '<Post {}>'.format(self.body)






# flask_login keeps track of the current user by storing its unique identifier in flask's "user session", a storage space assigned to each user who connects to the application.
# user_loader is used to load user classes into such sessions, and must be defined by us because flask_login doesn't know how the Classes are implemented
@login.user_loader
def load_user(id):
	return User.query.get(int(id))
