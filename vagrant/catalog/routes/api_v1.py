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


DBSession = sessionmaker()
session = DBSession()

api_v1 = Blueprint('api_v1', __name__)


@api_v1.route('/json/course/')
def API_v1_listCoursesJSON():
    courses = session.query(Course).all()
    return jsonify(Courses=[course.serialize for course in courses])


@api_v1.route('/json/course/<int:course_id>')
def API_v1_showCourseJSON(course_id):
    try:
        course = session.query(Course).filter_by(id=course_id).one()
    except:
        return abort(404)

    return jsonify(Course=course.serialize)


@api_v1.route('/json/course/<int:course_id>/skill')
def API_v1_listCourseSkillsJSON(course_id):
    try:
        course = session.query(Course).filter_by(id=course_id).one()
    except:
        return abort(404)

    skills = session.query(Skill).filter_by(course_id=course.id).all()
    return jsonify(Skills=[skill.serialize for skill in skills])


@api_v1.route('/json/course/<int:course_id>/skill/<int:skill_id>')
def API_v1_showCourseSkillJSON(course_id, skill_id):
    try:
        course = session.query(Course).filter_by(id=course_id).one()
    except:
        return abort(404)

    try:
        skill = session.query(Skill).filter_by(id=skill_id).one()
    except:
        return abort(404)

    return jsonify(Skill=skill.serialize)
