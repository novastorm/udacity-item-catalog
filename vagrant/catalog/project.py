import httplib2
import json
import requests
import string

from database_setup import Base
from database_setup import Course
from database_setup import DatabaseEngineURL
from database_setup import Exercise
from database_setup import Skill

from flask import Flask
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


@app.route('/')
@app.route('/course')
def listCourses():
    courses = session.query(Course).order_by(asc(Course.label))
    return render_template('courseList.html', courses=courses)


@app.route('/course/create', methods=['GET','POST'])
def createCourse():
    if request.method == 'POST':
        course = Course(
            label=request.form['input-label']
            )
        session.add(course)
        session.commit()
        session.refresh(course)
        return redirect(url_for('updateCourse', course_id=course.id))
    else:
        return render_template('courseCreate.html')


@app.route('/course/<int:course_id>')
def showCourse(course_id):
    course = session.query(Course).filter_by(id=course_id).one()
    return render_template('courseDetail.html', course=course)


@app.route('/course/<int:course_id>/update', methods=['GET','POST'])
def updateCourse(course_id):
    course = session.query(Course).filter_by(id=course_id).one()
    if request.method == 'POST':
        course.label = request.form['input-label']
        course.description = request.form['input-description']
        session.add(course)
        session.commit()
        return redirect(url_for('showCourse', course_id=course.id))
    else:
        return render_template('courseUpdate.html', course=course)


@app.route('/course/<int:course_id>/delete', methods=['GET','POST'])
def deleteCourse(course_id):
    course = session.query(Course).filter_by(id=course_id).one()
    if request.method == 'POST':
        session.delete(course)
        session.commit()
        return redirect(url_for('listCourses'))
    else:
        return render_template('courseDelete.html', course=course)


@app.route('courses/')

@app.route('/course/<int:course_id>/skill')
def listCourseSkills(course_id):
    return  "list course %s skills" % course_id


@app.route('/course/<int:course_id>/skills/create', methods=['GET','POST'])
def createCourseSkill(course_id):
    return  "create course %s skill" % course_id


@app.route('/course/<int:course_id>/skill/<int:skill_id>')
def showCourseSkill(course_id, skill_id):
    return  "show course %s skill %s" % (course_id, skill_id)


@app.route('/course/<int:course_id>/skill/<int:skill_id>/update', methods=['GET','POST'])
def updateCourseSkill(course_id, skill_id):
    return  "update course %s skill %s" % (course_id, skill_id)


@app.route('/course/<int:course_id>/skill/<int:skill_id>/delete', methods=['GET','POST'])
def deleteCourseSkill(course_id, skill_id):
    return  "delete course %s skill %s" % (course_id, skill_id)


@app.route('/course/<int:course_id>/exercise')
def listCourseExercises(course_id):
    return  "list course %s exercises" % course_id


@app.route('/course/<int:course_id>/exercise/create', methods=['GET','POST'])
def createCourseExercise(course_id):
    return  "create course %s exercise" % course_id


@app.route('/course/<int:course_id>/exercise/<int:exercise_id>')
def showCourseExercise(course_id, exercise_id):
    return  "show course %s exercise %s" % (course_id, exercise_id)


@app.route('/course/<int:course_id>/exercise/<int:exercise_id>/update', methods=['GET','POST'])
def updateCourseExercise(course_id, exercise_id):
    return  "update course %s exercise %s" % (course_id, exercise_id)


@app.route('/course/<int:course_id>/exercise/<int:exercise_id>/delete', methods=['GET','POST'])
def deleteCourseExercise(course_id, exercise_id):
    return  "delete course %s exercise %s" % (course_id, exercise_id)


if __name__ == '__main__':
  app.secret_key = 'super_secret_key'
  app.debug = True
  app.run(host = '0.0.0.0', port = 5000)
