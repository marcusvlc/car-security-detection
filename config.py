#SECRET_KEY = os.environ.get('FLASK_SECRET_KEY', 'secret-key')  # TODO

SERVER_URL = "localhost"
SERVER_PORT = 5000
SECRET_KEY = "banana"

# # Change this atributes with your mysql information
# DB_USERNAME = 'root'
# DB_PASSWORD = 'root'
# DB_NAME = 'hpedb'

# SQLALCHEMY_DATABASE_URI = 'sqlite:////tmp/test' + str(random.randint(1,1000)) + '.db'
SQLALCHEMY_DATABASE_URI = 'postgresql://cxcktulw:f41MkSMGXxEYr30odAmxRT4a9NmYibSF@queenie.db.elephantsql.com:5432/cxcktulw'

SQLALCHEMY_TRACK_MODIFICATIONS = False