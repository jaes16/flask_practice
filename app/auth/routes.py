from app import db
from app.auth import bp
from app.models import User, Post
from app.auth.forms import LoginForm, RegistrationForm, ResetPasswordEmailForm, ResetPasswordForm
from app.auth.email import send_password_reset_email

from flask import render_template, flash, redirect, url_for, request
from flask_login import current_user, login_user, login_required, logout_user
from werkzeug.urls import url_parse
from datetime import datetime
from flask_babel import _


# routes login, and "methods" allows this view function to accept both GET and POST requests
@bp.route('/login', methods=['GET', 'POST'])
def login():

	form = LoginForm()

	# validate_on_submit does all the form processing work. It returns false on a GET request, so when the browers asks for the form, this code will immediately render the login template.
	# if the browser sends a POST request, it will gather all the information, and if the info is not valid, it will again render the login template
	if form.validate_on_submit():
		# get the first user with this username
		attempted_user = User.query.filter_by(username=form.username.data).first() # there is only one user per username
		# if there is a user with this username, check if the password matches
		if attempted_user is None or not attempted_user.check_password(form.password.data):
			# flash a login error
			flash(_("Invalid username or password"))
			return redirect(url_for('auth.login')) # try again, fool!
		# if the username and password match, set as current user
		login_user(attempted_user, remember=form.remember_me.data)
		# in case this was a redirect, get the url of the page to return
		next_page = request.args.get('next') # request.args has the info given with the user request
		if not next_page or url_parse(next_page).netloc != '':
			next_page = url_for('main.index')
		return redirect(next_page)
	return render_template('auth/login.html', title='Sign In', form=form)


# logout
@bp.route('/logout')
def logout():
	logout_user()
	return redirect(url_for('main.index'))


@bp.route('/register', methods=['GET', 'POST'])
def register():

	if current_user.is_authenticated:
		return redirect(url_for('main.index')) # if we're already logged in, go back to index

	form = RegistrationForm()

	if form.validate_on_submit():
		user = User(username=form.username.data, email=form.email.data)
		user.set_password(form.password.data)
		db.session.add(user)
		db.session.commit()
		login_user(user)
		next_page = request.args.get('next') # in case this was a redirect, this will get the url of the page to return
		if not next_page or url_parse(next_page).netloc != '':
			next_page = url_for('main.index')
		return redirect(next_page)
	return render_template('auth/register.html', title='Registration', form=form)


@bp.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
	form = ResetPasswordEmailForm()
	if form.validate_on_submit():
		user = User.query.filter_by(email=form.email.data).first()
		send_password_reset_email(user)
		flash('Check your email for the instructions to reset your password')
		return redirect(url_for('auth.login'))
	return render_template('auth/reset_password_request.html', title='Reset Password', form=form)


@bp.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
	if current_user.is_authenticated:
		return redirect(url_for('main.index'))
	user = User.verify_reset_password_token(token)
	if not user:
		return redirect(url_for('main.index'))
	form = ResetPasswordForm()
	if form.validate_on_submit():
		user.set_password(form.password.data)
		db.session.commit()
		flash('Your password has been reset.')
		return redirect(url_for('auth.login'))
	return render_template('auth/reset_password.html', form=form)
