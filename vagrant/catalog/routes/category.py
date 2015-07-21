import flask
import httplib2
import json
import requests
import string

from database_setup import Base
from database_setup import Category
from database_setup import Item

from flask import abort
from flask import flash
from flask import jsonify
from flask import make_response
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for

from sqlalchemy import asc
from sqlalchemy.orm import sessionmaker


DBSession = sessionmaker()
session = DBSession()

category = flask.Blueprint('category', __name__)

@category.route('/')
@category.route('/category')
def listCategoryies():
    return "List Categories"


@category.route('/category/create')
def createCategory():
    return "create category"


@category.route('/category/<string:category_label>/update')
def updateCategory(category_label):
    return "update %s" % category_label


@category.route('/category/<string:category_label>/delete')
def deleteCategory(category_label):
    return "delete %s" % category_label


@category.route('/category/<string:category_label>/create')
def createCategoryItem(category_label):
    return "create %s item" % category_label


@category.route('/category/<string:category_label>/<string:item_label>')
def showCategoryItem(category_label, item_label):
    return "show %s item %s" % (category_label, item_label)


@category.route('/category/<string:category_label>/<string:item_label>/update')
def updateCategoryItem(category_label, item_label):
    return "update %s %s" % (category_label, item_label)


@category.route('/category/<string:category_label>/<string:item_label>/delete')
def deleteCategoryItem(category_label, item_label):
    return "delete %s %s" % (category_label, item_label)
