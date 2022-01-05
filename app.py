from flask import Flask
from models import db
from flask_migrate import Migrate

from hbb.routes import hbb
from api.routes import api
from admin.routes import admin
import config

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = config.SQLALCHEMY_DATABASE_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = config.secret_key

app.register_blueprint(hbb)
app.register_blueprint(api)
app.register_blueprint(admin)

db.init_app(app)
migrate = Migrate(app, db)


@app.before_first_request
def create_table():
    db.create_all()


@app.route('/')
def hello_world():
    return 'Open Shop Server'


if __name__ == '__main__':
    app.run(port=80)
