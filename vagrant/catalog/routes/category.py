import flask
import random
import string

from database_setup import Category
from database_setup import Item

from flask import abort
from flask import flash
from flask import redirect
from flask import render_template
from flask import request
from flask import session as login_session
from flask import url_for

from sqlalchemy import asc, desc
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.exc import NoResultFound


DBSession = sessionmaker()
DBH = DBSession()

category = flask.Blueprint('category', __name__)


def generateNonce(length=8):
    if '_nonce' not in login_session:
        login_session['_nonce'] = ''.join(random.choice(string.digits) for x in xrange(8))
    return login_session['_nonce']


def isValidNonce(nonce):
    session_nonce = None
    if '_nonce' in login_session:
        session_nonce = login_session['_nonce']
        del login_session['_nonce']
    return session_nonce and (session_nonce == nonce)


@category.route('/')
@category.route('/category')
def showCategoryMasterDetail():
    categories = DBH.query(Category).order_by(asc(Category.label))
    items = DBH.query(Item).order_by(desc(Item.date)).limit(10)

    if 'name' in login_session:
        template_file = 'showCategoryMasterDetail.html'
    else:
        template_file = 'showPublicCategoryMasterDetail.html'

    return render_template(template_file, categories=categories, items=items)


@category.route('/category/create', methods=['GET', 'POST'])
def createCategory():
    if 'name' not in login_session:
        return redirect(url_for('auth.showLogin'))

    if request.method == 'POST':
        nonce = request.form['nonce']
        if not isValidNonce(nonce):
            abort(403)

        category = Category(
            label = request.form['input-label']
            )

        if not category.label:
            flash('Label required')
            return render_template(
                'createCategory.html', category=category,
                nonce=generateNonce())

        DBH.add(category)
        try:
            DBH.commit()
        except IntegrityError, err:
            print err
            DBH.rollback()
            flash('Category exists')
            return render_template(
                'createCategory.html', category=category,
                nonce=generateNonce())

        DBH.refresh(category)
        flash('Category created')
        return redirect(url_for('category.showCategory',
            category_label=category.label))

    return render_template('createCategory.html', nonce=generateNonce())


@category.route('/category/<string:category_label>')
def showCategory(category_label):
    try:
        category = DBH.query(Category).filter_by(label=category_label).one()
    except NoResultFound:
        return redirect(url_for('category.showCategoryMasterDetail')), 404

    categories = (
        DBH.query(Category)
        .order_by(asc(Category.label))
        .all()
        )
    items = (
        DBH.query(Item)
        .filter_by(category_id=category.id)
        .order_by(asc(Item.label))
        .all()
        )

    if 'name' in login_session:
        template_file = 'showCategory.html'
    else:
        template_file = 'showPublicCategory.html'

    return render_template(
        template_file, categories=categories, category=category, items=items)


@category.route('/category/<string:category_label>/update',
    methods=['GET', 'POST'])
def updateCategory(category_label):
    if 'name' not in login_session:
        return redirect(url_for('auth.showLogin'))

    try:
        category = DBH.query(Category).filter_by(label=category_label).one()
    except NoResultFound:
        return redirect(url_for('category.showCategoryMasterDetail')), 404

    items = DBH.query(Item).filter_by(category_id=category.id).all()

    if request.method == 'POST':
        nonce = request.form['nonce']
        if not isValidNonce(nonce):
            abort(403)

        updates = Category(label=request.form['input-label'])

        try:
            # test if label exists
            (
                DBH.query(Category)
                .filter(
                    Category.label==updates.label, Category.id!=category.id)
                .one()
            )
        except NoResultFound:
            # expect no duplicate records
            pass
        else:
            flash('Category label exists')
            return render_template(
                'updateCategory.html', category=category,
                categoryUpdates=updates, items=items, nonce=generateNonce())

        category.label = updates.label
        DBH.add(category)
        DBH.commit()
        flash('Category updated')
        return redirect(url_for('category.showCategory',
            category_label=category.label))

    return render_template('updateCategory.html', category=category,
        items=items, nonce=generateNonce())


@category.route('/category/<string:category_label>/delete',
    methods=['GET', 'POST'])
def deleteCategory(category_label):
    if 'name' not in login_session:
        return redirect(url_for('auth.showLogin'))

    try:
        category = DBH.query(Category).filter_by(label=category_label).one()
    except NoResultFound:
        return redirect(url_for('category.showCategoryMasterDetail')), 404

    items = DBH.query(Item).filter_by(category_id=category.id).all()

    if len(items) > 0:
        flash('Category not empty')
        return render_template(
            'updateCategory.html', category=category, items=items,
            nonce=generateNonce())


    if request.method == 'POST':
        nonce = request.form['nonce']
        if not isValidNonce(nonce):
            abort(403)

        DBH.delete(category)
        DBH.commit()
        flash('Category deleted')
        return redirect(url_for('category.showCategoryMasterDetail'))

    return render_template(
        'deleteCategory.html', category=category, nonce=generateNonce())


@category.route('/category/create-item', methods=['GET', 'POST'])
@category.route('/category/<string:category_label>/create',
    methods=['GET', 'POST'])
def createCategoryItem(category_label=None):
    if 'name' not in login_session:
        return redirect(url_for('auth.showLogin'))

    if category_label == None:
        category = { 'label': '' }
    else:
        try:
            category = (
                DBH.query(Category)
                .filter_by(label=category_label)
                .one()
                )
        except NoResultFound:
            return redirect(url_for('category.showCategoryMasterDetail')), 404

    categories = DBH.query(Category).order_by(asc(Category.label)).all()

    if request.method == 'POST':
        nonce = request.form['nonce']
        if not isValidNonce(nonce):
            abort(403)

        item = Item(
            label = request.form['input-label'],
            description = request.form['input-description'],
            category_id = request.form['input-category-id'],
            user_id = login_session['user_id']
            )

        if request.form['input-label'] == "":
            flash('Item label required')
            return render_template('createCategoryItem.html',
                categories=categories, category=category, item=item,
                nonce=generateNonce())

        try:
            category = DBH.query(Category).filter_by(id=item.category_id).one()
        except NoResultFound:
            return redirect(url_for('category.showCategoryMasterDetail')), 404

        DBH.add(item)

        try:
            DBH.commit()
        except IntegrityError:
            DBH.rollback()
            flash('%s item label exists' % category.label)
            return render_template('createCategoryItem.html',
                categories=categories, category=category, item=item,
                nonce=generateNonce())
        except Exception, err:
            print Exception, err
            abort()

        DBH.refresh(item)
        flash('%s item created' % category.label)
        return redirect(url_for('category.showCategoryItem',
            category_label=category.label, item_label=item.label))

    return render_template(
        'createCategoryItem.html', categories=categories, category=category,
        nonce=generateNonce())


@category.route('/category/<string:category_label>/<string:item_label>')
def showCategoryItem(category_label, item_label):
    try:
        category = DBH.query(Category).filter_by(label=category_label).one()
    except NoResultFound:
        return redirect(url_for('category.showCategoryMasterDetail')), 404

    try:
        item = (
            DBH.query(Item)
            .filter_by(label=item_label, category_id=category.id)
            .one()
            )
    except NoResultFound:
        return redirect(
            url_for(
                'category.showCategory',
                category_label=category.label)), 404

    if 'name' in login_session:
        template_file = 'showCategoryItem.html'
    else:
        template_file = 'showPublicCategoryItem.html'

    return render_template(template_file, item=item)


@category.route('/category/<string:category_label>/<string:item_label>/update',
    methods=['GET', 'POST'])
def updateCategoryItem(category_label, item_label):
    if 'name' not in login_session:
        return redirect(url_for('auth.showLogin'))

    try:
        category = DBH.query(Category).filter_by(label=category_label).one()
    except NoResultFound:
        return redirect(url_for('category.showCategoryMasterDetail')), 404

    try:
        item = (
            DBH.query(Item)
            .filter_by(label=item_label, category_id=category.id)
            .one()
            )
    except NoResultFound:
        return redirect(
            url_for(
                'category.showCategory',
                category_label=category.label)), 404

    categories = DBH.query(Category).order_by(asc(Category.label)).all()

    if request.method =='POST':
        nonce = request.form['nonce']
        if not isValidNonce(nonce):
            abort(403)

        updates = Item(
            label = request.form['input-label'],
            description = request.form['input-description'],
            category_id = request.form['input-category-id']
            )

        try:
            updatedCategory = (
                DBH.query(Category)
                .filter_by(id=updates.category_id)
                .one()
                )
        except NoResultFound:
            return redirect(url_for('category.showCategoryMasterDetail')), 404

        try:
            # test if item label exists
            (
                DBH.query(Item)
                .filter(
                    Item.label==updates.label,
                    Item.category_id==updates.category_id,
                    Item.id!=item.id
                    )
                .one()
            )
        except NoResultFound:
            # expect no duplicate records
            pass
        else:
            flash('%s item label exists' % updatedCategory.label)
            return render_template(
                'updateCategoryItem.html', categories=categories, item=item,
                itemUpdates=updates, nonce=generateNonce())

        item.label = updates.label
        item.description = updates.description
        item.category_id = updates.category_id
        DBH.add(item)
        DBH.commit()
        DBH.refresh(item)
        flash('%s item updated' % item.category.label)
        return redirect(
            url_for('category.showCategoryItem',
            category_label=item.category.label,
            item_label=item.label))

    return render_template(
        'updateCategoryItem.html', categories=categories, item=item,
        nonce=generateNonce())


@category.route('/category/<string:category_label>/<string:item_label>/delete',
    methods=['GET', 'POST'])
def deleteCategoryItem(category_label, item_label):
    if 'name' not in login_session:
        return redirect(url_for('auth.showLogin'))

    try:
        category = DBH.query(Category).filter_by(label=category_label).one()
    except NoResultFound:
        return redirect(url_for('category.showCategoryMasterDetail')), 404

    try:
        item = (
            DBH.query(Item)
            .filter_by(label=item_label, category_id=category.id)
            .one()
            )
    except NoResultFound:
        return redirect(
            url_for(
                'category.showCategory',
                category_label=category.label)), 404

    if request.method == 'POST':
        nonce = request.form['nonce']
        if not isValidNonce(nonce):
            abort(403)

        DBH.delete(item)
        DBH.commit()
        flash('Category item deleted')
        return redirect(
            url_for(
                'category.showCategory',
                category_label=category.label))

    return render_template('deleteCategoryItem.html', item=item, nonce=generateNonce())
