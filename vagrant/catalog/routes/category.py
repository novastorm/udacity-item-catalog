import flask
import httplib2
import json
import requests
import string

from database_setup import Base
from database_setup import Category
from database_setup import Item

from datetime import timedelta

from flask import abort
from flask import flash
from flask import jsonify
from flask import make_response
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for

from sqlalchemy import asc, desc
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
    categories = session.query(Category).order_by(asc(Category.label))

    items = session.query(Item).order_by(desc(Item.date)).limit(10)
    return render_template('showHome.html', categories=categories, items=items)


@category.route('/category/create', methods=['GET', 'POST'])
def createCategory():
    if request.method == 'POST':
        category = Category(
            label = request.form['input-label']
            )
        session.add(category)
        try:
            session.commit()
        except:
            session.rollback()
            flash('Category exists')
            return render_template('createCategory.html', category=category)

        session.refresh(category)
        flash('Category created')
        return redirect(url_for('category.showCategory', category_label=aCategory['label']))

    return render_template('createCategory.html')


@category.route('/category/<string:category_label>')
def showCategory(category_label):
    return render_template('showCategory.html', categories=categories, category=aCategory, items=items)


@category.route('/category/<string:category_label>/update', methods=['GET', 'POST'])
def updateCategory(category_label):
    if request.method == 'POST':
        flash('Category updated')
        return redirect(url_for('category.showCategory', category_label=aCategory['label']))

    return render_template('updateCategory.html', category=aCategory)


@category.route('/category/<string:category_label>/delete', methods=['GET', 'POST'])
def deleteCategory(category_label):
    if request.method == 'POST':
        flash('Category deleted')
        return redirect(url_for('category.listCategories'))

    return render_template('deleteCategory.html', category=aCategory)


@category.route('/category/<string:category_label>/create', methods=['GET', 'POST'])
def createCategoryItem(category_label):
    if request.method == 'POST':
        flash('Category item created')
        return redirect(url_for('category.showCategoryItem', category_label=aCategory['label'], item_label=aItem['label']))

    if category_label == '':
        category = { 'label': '' }
    else:
        category = aCategory
    return render_template('createCategoryItem.html', category=category, item=aItem)


@category.route('/category/<string:category_label>/<string:item_label>')
def showCategoryItem(category_label, item_label):
    return render_template('showCategoryItem.html', category=aCategory, item=aItem)


@category.route('/category/<string:category_label>/<string:item_label>/update', methods=['GET', 'POST'])
def updateCategoryItem(category_label, item_label):
    if request.method == 'POST':
        flash('Category updated')
        return redirect(url_for('category.showCategoryItem', category_label=aCategory['label'], item_label=aItem['label']))

    return render_template('updateCategoryItem.html', category=aCategory, item=aItem)


@category.route('/category/<string:category_label>/<string:item_label>/delete', methods=['GET', 'POST'])
def deleteCategoryItem(category_label, item_label):
    if request.method == 'POST':
        flash('Category item deleted')
        return redirect(url_for('category.showCategory', category_label=aCategory['label']))

    return render_template('deleteCategoryItem.html', category=aCategory, item=aItem)
