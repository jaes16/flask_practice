from app import create_app, db, cli
from app.models import User, Post

app = create_app()
cli.register(app)

# decorator to create context for shell, flask shell
@app.shell_context_processor
def make_shell_context():
	# shell automatically imports app
	# set so that we don't have to import in shell
    return {'db': db, 'User': User, 'Post': Post}
