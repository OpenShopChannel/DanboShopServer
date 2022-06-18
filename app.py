from flask import Flask
from models import db
from flask_migrate import Migrate

from hbb.routes import hbb
from api.routes import api
from admin.routes import admin
from updater.routes import updater
import config
from utils import create_storage_dirs

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = config.SQLALCHEMY_DATABASE_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True
app.secret_key = config.secret_key

app.register_blueprint(hbb)
app.register_blueprint(api)
app.register_blueprint(admin)
app.register_blueprint(updater)

db.init_app(app)
migrate = Migrate(app, db)


@app.before_first_request
def initialize_server():
    # Ensure our database is present.
    db.create_all()

    # Create needed directories, if necessary.
    create_storage_dirs()


@app.route('/')
def hello_world():
    return 'Open Shop Server'


if __name__ == '__main__':
    app.run(port=80)
