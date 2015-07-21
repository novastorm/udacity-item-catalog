from database_setup import DatabaseEngineURL
from database_setup import Base

from flask import Flask

from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker

from routes.category import category

APPLICATION_NAME = "Item Catalog"

app = Flask(__name__)
engine = create_engine(DatabaseEngineURL)
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
DBH = DBSession()

app.register_blueprint(category)

if __name__ == '__main__':
  app.secret_key = 'super_secret_key'
  app.debug = True
  app.run(host = '0.0.0.0', port = 5000)
