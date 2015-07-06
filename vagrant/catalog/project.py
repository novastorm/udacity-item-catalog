from database_setup import Base
from database_setup import Course
from database_setup import Skill
from database_setup import Exercise
from database_setup import DatabaseEngineURL

from flask import Flask
from flask import flash
from flask import make_response
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for

from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker

import httplib2
import json
import requests
import string

from testdata import courses, course


APPLICATION_NAME = "Academy Concepts"

app = Flask(__name__)
engine = create_engine(DatabaseEngineURL)
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
DBH = DBSession()


@app.route('/')
@app.route('/courses')
def listCourses():
    return render_template('courseList.html', courses=courses)


@app.route('/courses/create', methods=['GET','POST'])
def createCourse():
    if request.method == 'POST':
        return redirect(url_for('updateCourse', course_id=course['id']))
    else:
        return render_template('courseCreate.html', course=course)


@app.route('/courses/<int:course_id>')
def showCourse(course_id):
    return render_template('courseDetail.html', course=course)


@app.route('/courses/<int:course_id>/update', methods=['GET','POST'])
def updateCourse(course_id):
    if request.method == 'POST':
        return redirect(url_for('showCourse', course_id=course['id']))
    else:
        return render_template('courseUpdate.html', course=course)


@app.route('/courses/<int:course_id>/delete', methods=['GET','POST'])
def deleteCourse(course_id):
    if request.method == 'POST':
        return redirect(url_for('listCourses'))
    else:
        return render_template('courseDelete.html', course=course)


@app.route('/courses/<int:course_id>/skills')
def listCourseSkills(course_id):
    return  "list course %s skills" % course_id


@app.route('/courses/<int:course_id>/skills/create', methods=['GET','POST'])
def createCourseSkill(course_id):
    return  "create course %s skill" % course_id


@app.route('/courses/<int:course_id>/skills/<int:skill_id>')
def showCourseSkill(course_id, skill_id):
    return  "show course %s skill %s" % (course_id, skill_id)


@app.route('/courses/<int:course_id>/skills/<int:skill_id>/update', methods=['GET','POST'])
def updateCourseSkill(course_id, skill_id):
    return  "update course %s skill %s" % (course_id, skill_id)


@app.route('/courses/<int:course_id>/skills/<int:skill_id>/delete', methods=['GET','POST'])
def deleteCourseSkill(course_id, skill_id):
    return  "delete course %s skill %s" % (course_id, skill_id)


@app.route('/courses/<int:course_id>/exercises')
def listCourseExercises(course_id):
    return  "list course %s exercises" % course_id


@app.route('/courses/<int:course_id>/exercises/create', methods=['GET','POST'])
def createCourseExercise(course_id):
    return  "create course %s exercise" % course_id


@app.route('/courses/<int:course_id>/exercises/<int:exercise_id>')
def showCourseExercise(course_id, exercise_id):
    return  "show course %s exercise %s" % (course_id, exercise_id)


@app.route('/courses/<int:course_id>/exercises/<int:exercise_id>/update', methods=['GET','POST'])
def updateCourseExercise(course_id, exercise_id):
    return  "update course %s exercise %s" % (course_id, exercise_id)


@app.route('/courses/<int:course_id>/exercises/<int:exercise_id>/delete', methods=['GET','POST'])
def deleteCourseExercise(course_id, exercise_id):
    return  "delete course %s exercise %s" % (course_id, exercise_id)


if __name__ == '__main__':
  app.secret_key = 'super_secret_key'
  app.debug = True
  app.run(host = '0.0.0.0', port = 5000)
