from app.__init__ import App
from app.ext import db

app = App.create_app('config')

SERVER_URL = app.config['SERVER_URL']
SERVER_PORT = app.config['SERVER_PORT']

with app.app_context():
	db.create_all()

if(__name__ == "__main__"):
    app.run(host=SERVER_URL, port=SERVER_PORT, debug=True, threaded=True)