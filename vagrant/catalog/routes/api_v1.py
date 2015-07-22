import flask
import json
import sqlalchemy.exc
import sqlalchemy.orm.exc

from database_setup import Category
from database_setup import Item

from flask import abort
from flask import jsonify

from sqlalchemy import asc, desc
from sqlalchemy.orm import sessionmaker


DBSession = sessionmaker()
session = DBSession()

api_v1 = flask.Blueprint('api_v1', __name__)


@api_v1.route('/category-master-detail.json')
def api_v1_showCategoryMasterDetailJSON():
    return "api_v1_showCategoryMasterDetailJSON"


@api_v1.route('/category.json')
def api_v1_listCategoriesJSON():
    return "api_v1_listCategoryJSON"


@api_v1.route('/category/<string:category_label>.json')
def api_v1_showCategoryJSON(category_label):
    return "api_v1_listCategoryJSON %s" % category_label


@api_v1.route('/category/<string:category_label>/<string:item_label>.json')
def api_v1_showCategoriesItemJSON(category_label, item_label):
    return "api_v1_listCategoryItemJSON %s %s" % (category_label, item_label)
