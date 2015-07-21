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

categories = [
    {
        'id': '1',
        'label': 'Maritial Arts'
    },
    {
        'id': '2',
        'label': 'Hockey'
    },
    {
        'id': '3',
        'label': 'Softball'
    }
]

aCategory = {
    'id': '1',
    'label': 'Maritial Arts'
}

items = [
    {
        'id': '1',
        'label': 'Fingerless gloves',
        'date': '2015-07-20',
        'description': 'Gloves with fingers cut out to allowing for direct contact with environment.',
        'category_id': '1',
    },
    {
        'id': '2',
        'label': 'Padded headgear',
        'date': '2015-07-10',
        'description': 'Padded headgear to provide some head protection.',
        'category_id': '1',
    }
]

aItem = {
    'id': '1',
    'label': 'Fingerless gloves',
    'date': '2015-07-20',
    'description': 'Gloves with fingers cut out to allowing for direct contact with environment.',
    'category_id': '1',
}


@category.route('/')
@category.route('/category')
def listCategories():
    return render_template('showHome.html', categories=categories, items=items)


@category.route('/category/create')
def createCategory():
    return render_template('createCategory.html')


@category.route('/category/<string:category_label>')
def showCategory(category_label):
    return render_template('showCategory.html', categories=categories, category=aCategory, items=items)


@category.route('/category/<string:category_label>/update', methods=['GET', 'POST'])
def updateCategory(category_label):
    if request.method == 'POST':
        flash('Category updated')
        return redirect(url_for('category.showCategory', category_label=aCategory['label']))
    else:
        return render_template('updateCategory.html', categories=categories, category=aCategory)


@category.route('/category/<string:category_label>/delete', methods=['GET', 'POST'])
def deleteCategory(category_label):
    if request.method == 'POST':
        flash('Category deleted')
        return redirect(url_for('category.listCategories'))
    else:
        return render_template('deleteCategory.html', categories=categories, category=aCategory)


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