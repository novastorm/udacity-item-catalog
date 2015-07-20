import httplib2
import json
import requests
import string

from database_setup import Base
from database_setup import Course
from database_setup import DatabaseEngineURL
from database_setup import Exercise
from database_setup import Skill

from flask import Blueprint
from flask import Flask
from flask import abort
from flask import flash
from flask import jsonify
from flask import make_response
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for

from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker


APPLICATION_NAME = "Academy Concepts"

app = Flask(__name__)
engine = create_engine(DatabaseEngineURL)
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

api_v1 = Blueprint('api_v1', __name__)


@api_v1.route('/course/json')
def APIv1_listCoursesJSON():
    courses = session.query(Course).all()
    return jsonify(Courses=[course.serialize for course in courses])

# @api_v1.route('/course/')
