import flask
import json

from database_setup import Category
from database_setup import Item

from flask import abort
from flask import jsonify

from sqlalchemy import asc, desc
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.exc import NoResultFound


DBSession = sessionmaker()
DBH = DBSession()

api_v1 = flask.Blueprint('api_v1', __name__)


@api_v1.route('/category-master-detail.json')
def api_v1_showCategoryMasterDetailJSON():
    categories = DBH.query(Category).all()
    return jsonify(Categories=[category.serializeExpanded for category in categories])


@api_v1.route('/category.json')
def api_v1_listCategoryJSON():
    categories = DBH.query(Category).all()
    return jsonify(Categories=[category.serialize for category in categories])

@api_v1.route('/category/<string:category_label>.json')
def api_v1_showCategoryJSON(category_label):
    try:
        category = DBH.query(Category).filter_by(label=category_label).one()
    except NoResultFound:
        return abort(404)

    return jsonify(Category=category.serializeExpanded)


@api_v1.route('/category/<string:category_label>/<string:item_label>.json')
def api_v1_showCategoryItemJSON(category_label, item_label):
    try:
        category = DBH.query(Category).filter_by(label=category_label).one()
    except NoResultFound:
        return abort(404)

    try:
        item = DBH.query(Item).filter_by(label=item_label, category_id=category.id).one()
    except NoResultFound:
        return abort(404)

    return jsonify(Item=item.serialize)
