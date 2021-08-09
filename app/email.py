from flask_mail import Message
from app import mail
from threading import Thread
from flask import current_app

# sends email in background, so we can return to service in the foreground
def send_async_email(app, msg):
	with app.app_context():
		mail.send(msg)

def send_email(subject, sender, recipients, text_body, html_body):
	msg = Message(subject, sender=sender, recipients=recipients)
	msg.body = text_body
	msg.html = html_body
	# asynchronous email send, because email sending can take a few seconds, which is way too slow
	Thread(target=send_async_email, args=(current_app._get_current_object(), msg)).start()
