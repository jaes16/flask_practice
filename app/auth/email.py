from app.email import send_email
from flask import render_template, current_app

def send_password_reset_email(user):
	token = user.get_reset_password_token()
	subject = 'Flask_Practice: Password Reset'
	sender = current_app.config['ADMINS'][0]
	recipients = [user.email]
	text_body=render_template('email/reset_password.txt',user=user, token=token)
	html_body=render_template('email/reset_password.html',user=user, token=token)
	send_email(subject, sender, recipients, text_body, html_body)
