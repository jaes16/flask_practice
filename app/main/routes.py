from app import db
from app.main import bp
from app.models import User, Post
from app.main.forms import PostForm, EditProfileForm, EmptyForm

from flask import current_app, render_template, flash, redirect, url_for, request, g, jsonify
from flask_login import current_user, login_required
from werkzeug.urls import url_parse
from datetime import datetime
from langdetect import detect, LangDetectException
from flask_babel import get_locale, _
from app.translate import translate

# The @before_request decorator from Flask register the decorated function to be executed right before the view function
@bp.before_request
def before_request():
	if current_user.is_authenticated:
		current_user.last_seen = datetime.utcnow()
		db.session.commit()
	g.locale = str(get_locale())


# routes '/index' to the function 'index()'
@bp.route('/', methods=['GET', 'POST'])
@bp.route('/index')
@login_required
def index():
	form = PostForm()
	if form.validate_on_submit():
		language = ''
		try:
			language = detect(form.post.data)
		except LangDetectException:
			language = ''
		post = Post(body=form.post.data, author=current_user, language=language)
		db.session.add(post)
		db.session.commit()
		flash('Blog post submitted!')
		return redirect(url_for('main.index'))
	page = request.args.get('page', 1, type=int)
	posts = current_user.followed_posts().paginate(page, current_app.config['POSTS_PER_PAGE'], False)
	next_url = url_for('main.index', page=posts.next_num) if posts.has_next else None
	prev_url = url_for('main.index', page=posts.prev_num) if posts.has_prev else None
	return render_template('index.html', title='Home', form=form, posts=posts.items, next_url=next_url, prev_url=prev_url)



# user page
@bp.route('/user/<username>')
@login_required
def user(username):
	user = User.query.filter_by(username=username).first_or_404()
	form = EmptyForm()
	return render_template('user.html', user=user, posts=user.posts, form=form)


@bp.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
	form = EditProfileForm()
	if form.validate_on_submit():
		current_user.username = form.username.data
		current_user.about_me = form.about_me.data
		db.session.commit()
		flash('Your changes have been saved.')
		return redirect(url_for('main.index'))
	elif request.method == 'GET':
		form.username.data = current_user.username
		form.about_me.data = current_user.about_me
	return render_template('edit_profile.html', title='Edit Profile', form=form)


@bp.route('/follow/<username>', methods=['POST'])
@login_required
def follow(username):
	form = EmptyForm()
	if form.validate_on_submit():
		user = User.query.filter_by(username=username).first()
		if user is None:
			flash('User {} not found.'.format(username))
			return redirect(url_for('main.index'))
		if user == current_user:
			flash('You cannot follow yourself!')
			return redirect(url_for('main.user', username=username))
		current_user.follow(user)
		db.session.commit()
		flash('You are following {}!'.format(username))
		return redirect(url_for('main.user', username=username))
	else:
		return redirect(url_for('main.index'))


@bp.route('/unfollow/<username>', methods=['POST'])
@login_required
def unfollow(username):
	form = EmptyForm()
	if form.validate_on_submit():
		user = User.query.filter_by(username=username).first()
		if user is None:
			flash('User {} not found.'.format(username))
			return redirect(url_for('main.index'))
		if user == current_user:
			flash('You cannot unfollow yourself!')
			return redirect(url_for('main.user', username=username))
		current_user.unfollow(user)
		db.session.commit()
		flash('You are not following {}.'.format(username))
		return redirect(url_for('main.user', username=username))
	else:
		return redirect(url_for('main.index'))


@bp.route('/explore')
@login_required
def explore():
	# use request.args to get information of user request.
	page = request.args.get('page', 1, type=int)
	# paginate retrieves only the desired page of results
	posts = Post.query.order_by(Post.timestamp.desc()).paginate(page, current_app.config['POSTS_PER_PAGE'], False)
	next_url = url_for('main.explore', page=posts.next_num) if posts.has_next else None
	prev_url = url_for('main.explore', page=posts.prev_num) if posts.has_prev else None
	return render_template('index.html', title='Explore', posts=posts.items, next_url=next_url, prev_url=prev_url)


@bp.route('/translate', methods=['POST'])
@login_required
def translate_text():
	return jsonify({'text': translate(request.form['text'], request.form['source_language'], request.form['dest_language'])})
