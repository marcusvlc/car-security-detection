'''
Flask extensions for the app
'''
from flask_socketio import SocketIO
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy

class Cors:
    def init_app(self, app):
        return CORS(app)


socketio = SocketIO()
cors = Cors()
db = SQLAlchemy()