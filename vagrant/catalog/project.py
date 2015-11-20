""" Catalog of Items

This application provides a list of items within a variety of categories and
integrates third party user registration and authentication.

This product demonstrates a CRUD web application, OAuth integration, and security
measures to address CSRF.
"""

from flask import Flask

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.exc import NoResultFound

from database_setup import DatabaseEngineURL
from database_setup import Base
from database_setup import User

from routes import auth
from routes.api_v1 import api_v1 as _api_v1_blueprint
from routes.auth import auth as _auth_blueprint
from routes.category import category as _category_blueprint
from routes.feed import feed as _feed_blueprint

APPLICATION_NAME = "Item Catalog"

app = Flask(__name__)
engine = create_engine(DatabaseEngineURL)
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
DBH = DBSession()

app.register_blueprint(_auth_blueprint)
app.register_blueprint(_category_blueprint)
app.register_blueprint(_api_v1_blueprint, url_prefix='/api/v1')
app.register_blueprint(_feed_blueprint, url_prefix='/feed')


@app.context_processor
def utility_processor():
    """Provides addtional utility functions for use within templates."""
    return dict(
        getUserId=auth.getUserId,
        getUserInformation=auth.getUserInformation)

app.secret_key = 'super_secret_key'

if __name__ == '__main__':
  app.debug = True
  app.run(host = '0.0.0.0', port = 5000)
