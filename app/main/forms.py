from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField
from wtforms.validators import ValidationError, DataRequired, Length
from app.models import User
from flask_login import current_user

class PostForm(FlaskForm):
	body = TextAreaField('Post Something', validators=[DataRequired(), Length(min=1,max=140)])
	submit = SubmitField('Post')

class EditProfileForm(FlaskForm):
	username = StringField('Username', validators=[DataRequired(), Length(min=1,max=20)])
	about_me = TextAreaField('About Me', validators=[Length(min=1, max=140)])
	submit = SubmitField('Register')

	def validate_username(self, username):
		if username.data != current_user.username:
			user = User.query.filter_by(username=username.data).first()
			if user is not None:
				raise ValidationError('Please use a different username.')


class EmptyForm(FlaskForm):
	submit = SubmitField('Submit')
