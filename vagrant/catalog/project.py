from flask import Flask

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.exc import NoResultFound

from database_setup import DatabaseEngineURL
from database_setup import Base
from database_setup import User

from routes.api_v1 import api_v1
from routes.auth import auth
from routes.category import category
from routes.feed import feed

APPLICATION_NAME = "Item Catalog"

app = Flask(__name__)
engine = create_engine(DatabaseEngineURL)
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
DBH = DBSession()

app.register_blueprint(auth)
app.register_blueprint(category)
app.register_blueprint(api_v1, url_prefix='/api/v1')
app.register_blueprint(feed, url_prefix='/feed')


@app.context_processor
def utility_processor():
    def getUserId(email):
        try:
            user = DBH.query(User).filter_by(email=email).one()
        except NoResultFound:
            return None

        return user.id


    def getUserInformation(user_id):
        try:
            user = DBH.query(User).filter_by(id=user_id).one()
        except NoResultFound:
            return None

        return user

    return dict(
        getUserId=getUserId, getUserInformation=getUserInformation)


if __name__ == '__main__':
  app.secret_key = 'super_secret_key'
  app.debug = True
  app.run(host = '0.0.0.0', port = 5000)
