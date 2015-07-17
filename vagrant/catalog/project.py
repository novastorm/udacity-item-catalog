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


@app.route('/')
@app.route('/course')
def listCourses():
    courses = session.query(Course).order_by(asc(Course.label))
    return render_template('listCourses.html', courses=courses)


@app.route('/course/create', methods=['GET','POST'])
def createCourse():
    if request.method == 'POST':
        course = Course(
            label=request.form['input-label']
            )
        session.add(course)
        try:
            session.commit()
        except:
            session.rollback()
            flash('Course label exists')
            return render_template('createCourse.html', course=course)

        session.refresh(course)
        return redirect(url_for('updateCourse', course_id=course.id))
    else:
        return render_template('createCourse.html')


@app.route('/course/<int:course_id>')
def showCourse(course_id):
    try:
        course = session.query(Course).filter_by(id=course_id).one()
    except:
        return redirect(url_for('listCourses')), 404

    return render_template('showCourse.html', course=course)


@app.route('/course/<int:course_id>/update', methods=['GET','POST'])
def updateCourse(course_id):
    try:
        course = session.query(Course).filter_by(id=course_id).one()
    except:
        return redirect(url_for('listCourses')), 404

    if request.method == 'POST':
        updates = Course(
            label = request.form['input-label'],
            description = request.form['input-description']
            )

        try:
            existingCourse = session.query(Course).filter(Course.label==updates.label, Course.id!=course_id).one()
            flash('Course label exists')
            return render_template('updateCourse.html', course=course, courseUpdates=updates)
        except:
            course.label = updates.label
            course.description = updates.description
            session.add(course)
            session.commit()
            return redirect(url_for('showCourse', course_id=course.id))
    else:
        return render_template('updateCourse.html', course=course)


@app.route('/course/<int:course_id>/delete', methods=['GET','POST'])
def deleteCourse(course_id):
    try:
        course = session.query(Course).filter_by(id=course_id).one()
    except:
        return abort(404)

    if request.method == 'POST':
        session.delete(course)
        session.commit()
        return redirect(url_for('listCourses'))
    else:
        return render_template('deleteCourse.html', course=course)


@app.route('/course/JSON')
def listCoursesJSON():
    courses = session.query(Course).all()
    return jsonify(courses=[course.serialize for course in courses])


@app.route('/course/<int:course_id>/JSON')
def showCourseJSON(course_id):
    try:
        course = session.query(Course).filter_by(id=course_id).one()
    except:
        return abort(404)

    return jsonify(course=course.serialize)


@app.route('/course/<int:course_id>/skill')
def listCourseSkills(course_id):
    try:
        course = session.query(Course).filter_by(id=course_id).one()
    except:
        return redirect(url_for('listCourses'))

    skills = session.query(Skill).filter_by(course_id=course.id).order_by(asc(Skill.label)).all()
    return render_template('listCourseSkills.html', course=course, skills=skills)


@app.route('/course/<int:course_id>/skill/create', methods=['GET','POST'])
def createCourseSkill(course_id):
    course = session.query(Course).filter_by(id=course_id).one()
    if request.method == 'POST':
        skill = Skill(
            course_id=course.id,
            label=request.form['input-label']
            )
        session.add(skill)
        try:
            session.commit()
        except:
            session.rollback()
            flash('Course skill label exists')
            return render_template('createCourseSkill.html', course=course, skill=skill)

        session.refresh(skill)
        return redirect(url_for('updateCourseSkill', course_id=course.id, skill_id=skill.id))
    else:
        return render_template('createCourseSkill.html', course=course)


@app.route('/course/<int:course_id>/skill/<int:skill_id>')
def showCourseSkill(course_id, skill_id):
    course = session.query(Course).filter_by(id=course_id).one()
    skill = session.query(Skill).filter_by(id=skill_id).one()
    return render_template('showCourseSkill.html', course=course, skill=skill)


@app.route('/course/<int:course_id>/skill/<int:skill_id>/update', methods=['GET','POST'])
def updateCourseSkill(course_id, skill_id):
    try:
        course = session.query(Course).filter_by(id=course_id).one()
    except:
        return redirect(url_for('listCourses')), 404

    try:
        skill = session.query(Skill).filter_by(id=skill_id).one()
    except:
        return redirect(url_for('listCourseSkills', course_id=course.id)), 404

    if request.method == 'POST':
        updates = Skill(
            label = request.form['input-label'],
            description = request.form['input-description']
            )
        try:
            print "check for existing"
            existingSkill = session.query(Skill).filter(Skill.course_id==course_id, Skill.label==updates.label, Skill.id!=skill.id).one()
            flash('Course skill label exists')
            return render_template('updateCourseSkill.html', course=course, skill=skill, skillUpdates=updates)
        except:
            print "does not exist"
            skill.label = updates.label
            skill.description = updates.description
            session.add(skill)
            session.commit()
            return redirect(url_for('showCourseSkill', course_id=course.id, skill_id=skill.id))
    else:
        return render_template('updateCourseSkill.html', course=course, skill=skill)


@app.route('/course/<int:course_id>/skill/<int:skill_id>/delete', methods=['GET','POST'])
def deleteCourseSkill(course_id, skill_id):
    try:
        course = session.query(Course).filter_by(id=course_id).one()
    except:
        return redirect(url_for('listCourses')), 404

    try:
        skill = session.query(Skill).filter_by(id=skill_id).one()
    except:
        return redirect(url_for('listCourseSkills', course_id=course.id)), 404

    if request.method == 'POST':
        session.delete(skill)
        session.commit()
        return redirect(url_for('listCourseSkills', course_id=course.id))
    else:
        return render_template('deleteCourseSkill.html', course=course, skill=skill)


@app.route('/course/<int:course_id>/exercise')
def listCourseExercises(course_id):
    try:
        course = session.query(Course).filter_by(id=course_id).one()
    except:
        return redirect(url_for('listCourses'))

    exercises = session.query(Exercise).filter_by(course_id=course_id).order_by(asc(Exercise.label)).all()

    return render_template('listCourseExercises.html', course=course, exercises=exercises)


@app.route('/course/<int:course_id>/exercise/create', methods=['GET','POST'])
def createCourseExercise(course_id):
    try:
        course = session.query(Course).filter_by(id=course_id).one()
    except:
        return redirect(url_for('listCourses'))

    if request.method == 'POST':
        exercise = Exercise(
            course_id = course.id,
            label = request.form['input-label']
            )
        session.add(exercise)
        try:
            session.commit()
        except:
            session.rollback()
            flash('Course exercise label exists')
            return render_template('createCourseExercise.html', course=course, exercise=exercise)

        session.refresh(exercise)
        return redirect(url_for('updateCourseExercise', course_id=course.id, exercise_id=exercise.id))
    else:
        return render_template('createCourseExercise.html', course=course)


@app.route('/course/<int:course_id>/exercise/<int:exercise_id>')
def showCourseExercise(course_id, exercise_id):
    try:
        course = session.query(Course).filter_by(id=course_id).one()
    except:
        return redirect(url_for('listCourses')), 404

    try:
        exercise = session.query(Exercise).filter_by(id=exercise_id).one()
    except:
        return redirect(url_for('listCoursesExercises', course_id=course.id)), 404

    return render_template('showCourseExercise.html', course=course, exercise=exercise)


@app.route('/course/<int:course_id>/exercise/<int:exercise_id>/update', methods=['GET','POST'])
def updateCourseExercise(course_id, exercise_id):
    try:
        course = session.query(Course).filter_by(id=course_id).one()
    except:
        return redirect(url_for('listCourses')), 404

    try:
        exercise = session.query(Exercise).filter_by(id=exercise_id).one()
    except:
        return redirect(url_for('listCoursesExercises', course_id=course.id)), 404

    if request.method == 'POST':
        updates = Exercise(
            label = request.form['input-label'],
            task = request.form['input-task']
            )
        try:
            existingExercise = session.query(Exercise).filter(Exercise.course_id==course.id, Exercise.label==updates.label, Exercise.id!=exercise.id).one()
            flash('Course exercise label exists')
            return render_template('updateCourseExercise.html', course=course, exercise=exercise, exerciseUpdates=updates)
        except:
            exercise.label = updates.label
            exercise.task = updates.task
            session.add(exercise)
            session.commit()
            return redirect(url_for('showCourseExercise', course_id=course.id, exercise_id=exercise.id))
    else:
        return render_template('updateCourseExercise.html', course=course, exercise=exercise)


@app.route('/course/<int:course_id>/exercise/<int:exercise_id>/delete', methods=['GET','POST'])
def deleteCourseExercise(course_id, exercise_id):
    try:
        course = session.query(Course).filter_by(id=course_id).one()
    except:
        return redirect(url_for('listCourses')), 404

    try:
        exercise = session.query(Exercise).filter_by(id=exercise_id).one()
    except:
        return redirect(url_for('listCourseExercises', course_id=course.id)), 404

    if request.method == 'POST':
        session.delete(exercise)
        session.commit()
        return redirect(url_for('listCourseExercises', course_id=course.id))
    else:
        return render_template('deleteCourseExercise.html', course=course, exercise=exercise)


if __name__ == '__main__':
  app.secret_key = 'super_secret_key'
  app.debug = True
  app.run(host = '0.0.0.0', port = 5000)
