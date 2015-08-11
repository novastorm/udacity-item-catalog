"""API data feature

Generates JSON for available information.
"""


import flask
import json

from database_setup import Category
from database_setup import Item

from flask import abort
from flask import jsonify

from sqlalchemy import asc, desc
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.exc import NoResultFound


# get database session
_DBSession = sessionmaker()
_DBH = _DBSession()

api_v1 = flask.Blueprint('api_v1', __name__)


@api_v1.route('/category-master-detail.json')
def api_v1_showCategoryMasterDetailJSON():
    """Return a list of categories and associated items.

    Returns:
      A list of set of tuples, each of which contains (id, label, items)
        id: category's unique id
        label: the category label
        items: a dictionary of tuples, each of which contains (
            id, label, date, description, iamge_url, category_id)
            id: item's unique id
            label: item label
            date: creation date
            description: item's description
            iamge_url: URL to the item image
            category_id: the associated category id
    """
    categories = _DBH.query(Category).all()
    return jsonify(Categories=[category.serializeExpanded for category in categories])


@api_v1.route('/category.json')
def api_v1_listCategoryJSON():
    """Return a list of categories.

    Returns:
      A list of set of tuples, each of which contains (id, label, items)
        id: category's unique id
        label: the category label
    """
    categories = _DBH.query(Category).all()
    return jsonify(Categories=[category.serialize for category in categories])

@api_v1.route('/category/<string:category_label>.json')
def api_v1_showCategoryJSON(category_label):
    """Return respective category and associated items.

    Returns:
      A tuple containing (id, label, items)
        id: category's unique id
        label: the category label
        items: a dictionary of tuples, each of which contains (
            id, label, date, description, iamge_url, category_id)
            id: item's unique id
            label: item label
            date: creation date
            description: item's description
            iamge_url: URL to the item image
            category_id: the associated category id
    """
    try:
        category = _DBH.query(Category).filter_by(label=category_label).one()
    except NoResultFound:
        return abort(404)

    return jsonify(Category=category.serializeExpanded)


@api_v1.route('/category/<string:category_label>/<string:item_label>.json')
def api_v1_showCategoryItemJSON(category_label, item_label):
    """Return category item information.

    Returns:
      A dictionary of tuples, each of which contains (
        id, label, date, description, iamge_url, category_id)
        id: item's unique id
        label: item label
        date: creation date
        description: item's description
        iamge_url: URL to the item image
        category_id: the associated category id
    """
    try:
        category = _DBH.query(Category).filter_by(label=category_label).one()
    except NoResultFound:
        return abort(404)

    try:
        item = _DBH.query(Item).filter_by(label=item_label, category_id=category.id).one()
    except NoResultFound:
        return abort(404)

    return jsonify(Item=item.serialize)
