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
    categories = session.query(Category).all()
    return jsonify(Categories=[category.serializeExpanded for category in categories])


@api_v1.route('/category.json')
def api_v1_listCategoryJSON():
    categories = session.query(Category).all()
    return jsonify(Categories=[category.serialize for category in categories])

@api_v1.route('/category/<string:category_label>.json')
def api_v1_showCategoryJSON(category_label):
    try:
        category = session.query(Category).filter_by(label=category_label).one()
    except sqlalchemy.orm.exc.NoResultFound:
        return abort(404)

    return jsonify(Category=category.serializeExpanded)


@api_v1.route('/category/<string:category_label>/<string:item_label>.json')
def api_v1_showCategoryItemJSON(category_label, item_label):
    try:
        category = session.query(Category).filter_by(label=category_label).one()
    except sqlalchemy.orm.exc.NoResultFound:
        return abort(404)

    try:
        item = session.query(Item).filter_by(label=item_label, category_id=category.id).one()
    except sqlalchemy.orm.exc.NoResultFound:
        return abort(404)

    return jsonify(Item=item.serialize)
