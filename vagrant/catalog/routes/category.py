import flask
import httplib2
import json
import requests
import string
import sqlalchemy.exc
import sqlalchemy.orm.exc

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
        except sqlalchemy.exc.IntegrityError, err:
            print err
            session.rollback()
            flash('Category exists')
            return render_template('createCategory.html', category=category)

        session.refresh(category)
        flash('Category created')
        return redirect(url_for('category.showCategory', category_label=category.label))

    return render_template('createCategory.html')


@category.route('/category/<string:category_label>')
def showCategory(category_label):
    try:
        category = session.query(Category).filter_by(label=category_label).one()
    except sqlalchemy.orm.exc.NoResultFound:
        return redirect(url_for('category.listCategories')), 404

    categories = session.query(Category).order_by(asc(Category.label)).all()
    items = session.query(Item).filter_by(category_id=category.id).all()

    return render_template('showCategory.html',
        categories=categories,
        category=category,
        items=items)


@category.route('/category/<string:category_label>/update', methods=['GET', 'POST'])
def updateCategory(category_label):
    try:
        category = session.query(Category).filter_by(label=category_label).one()
    except sqlalchemy.orm.exc.NoResultFound:
        return redirect(url_for('category.listCategories')), 404

    if request.method == 'POST':
        updates = Category(label=request.form['input-label'])

        try:
            # test if label exists
            session.query(Category)\
            .filter(
                Category.label==updates.label,
                Category.id!=category.id
            )\
            .one()
        except sqlalchemy.orm.exc.NoResultFound:
            # expect no duplicate records
            pass
        else:
            flash('Category label exists')
            return render_template('updateCategory.html',
                category=category,
                categoryUpdates=updates)

        category.label = updates.label
        session.add(category)
        session.commit()
        flash('Category updated')
        return redirect(url_for('category.showCategory',
            category_label=category.label))

    return render_template('updateCategory.html', category=category)


@category.route('/category/<string:category_label>/delete', methods=['GET', 'POST'])
def deleteCategory(category_label):
    try:
        category = session.query(Category).filter_by(label=category_label).one()
    except sqlalchemy.orm.exc.NoResultFound:
        return redirect(url_for('category.listCategories')), 404

    if request.method == 'POST':
        session.delete(category)
        session.commit()
        flash('Category deleted')
        return redirect(url_for('category.listCategories'))

    return render_template('deleteCategory.html', category=category)


@category.route('/category/create-item', methods=['GET', 'POST'])
@category.route('/category/<string:category_label>/create', methods=['GET', 'POST'])
def createCategoryItem(category_label=None):
    if category_label == None:
        category = { 'label': '' }
    else:
        try:
            category = session.query(Category).filter_by(label=category_label).one()
        except sqlalchemy.orm.exc.NoResultFound:
            return redirect(url_for('category.listCategories')), 404

    categories = session.query(Category).order_by(asc(Category.label)).all()

    if request.method == 'POST':
        item = Item(
            label = request.form['input-label'],
            description = request.form['input-description'],
            category_id = request.form['input-category-id']
            )

        if request.form['input-label'] == "":
            flash('Item label required')
            return render_template('createCategoryItem.html', categories=categories, category=category, item=item)

        try:
            category = session.query(Category).filter_by(id=item.category_id).one()
        except sqlalchemy.orm.exc.NoResultFound:
            return redirect(url_for('category.listCategories')), 404

        session.add(item)

        try:
            session.commit()
        except sqlalchemy.exc.IntegrityError:
            session.rollback()
            flash('%s item label exists' % category.label)
            return render_template('createCategoryItem.html', categories=categories, category=category, item=item)
        except Exception, err:
            print Exception, err
            abort()

        session.refresh(item)
        flash('%s item created' % category.label)
        return redirect(url_for('category.showCategoryItem', category_label=category.label, item_label=item.label))

    return render_template('createCategoryItem.html', categories=categories, category=category)


@category.route('/category/<string:category_label>/<string:item_label>')
def showCategoryItem(category_label, item_label):
    try:
        category = session.query(Category).filter_by(label=category_label).one()
    except sqlalchemy.orm.exc.NoResultFound:
        return redirect(url_for('category.listCategories')), 404

    try:
        item = session.query(Item).filter_by(label=item_label).one()
    except sqlalchemy.orm.exc.NoResultFound:
        return redirect(url_for('category.showCategory', category_label=category.label)), 404

    return render_template('showCategoryItem.html', category=category, item=item)


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
