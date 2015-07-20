from database_setup import DatabaseEngineURL
from database_setup import Base
from database_setup import Category
from database_setup import Item

from flask import Flask
from flask import flash
from flask import make_response
from flask import redirect
from flask import render_template
from flask import request

from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker

import httplib2
import json
import requests
import string

APPLICATION_NAME = "Academy Concepts"

app = Flask(__name__)
engine = create_engine(DatabaseEngineURL)
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
DBH = DBSession()


if __name__ == '__main__':
  app.secret_key = 'super_secret_key'
  app.debug = True
  app.run(host = '0.0.0.0', port = 5000)
