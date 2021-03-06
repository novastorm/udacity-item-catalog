"""Category and Category Item features

Provides routes, view and processing for Category and Category Item objects.
"""


import flask
import random
import string

from flask import abort
from flask import flash
from flask import redirect
from flask import render_template
from flask import request
from flask import session as _login_session
from flask import url_for

from sqlalchemy import asc, desc
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.exc import NoResultFound

from database_setup import Category
from database_setup import Item

from routes import auth

# get database session
_DBSession = sessionmaker()
_DBH = _DBSession()

category = flask.Blueprint('category', __name__)


def _generateNonce(length=8):
    """Generate a nonce value of the given length."""
    if '_nonce' not in _login_session:
        _login_session['_nonce'] = ''.join(random.choice(string.digits) for x in xrange(8))
    return _login_session['_nonce']


def _isValidNonce(nonce):
    """Returns the result of nonce validation.

    Args:
        nonce: the nonce value to check
    Returns:
        True if nonce is valid,
        False otherwise"""
    session_nonce = None
    if '_nonce' in _login_session:
        session_nonce = _login_session['_nonce']
        del _login_session['_nonce']
    return session_nonce and (session_nonce == nonce)


@category.route('/')
@category.route('/category')
def showCategoryMasterDetail():
    """Show Category master-detail view.

    This view displays the category and most recently added category items. If
    the user is logged in, render the private template with management
    controls, otherwise render the public template.

    This is the default view.

    Returns:
        The rendered Category Master-Detail view
    """
    categories = _DBH.query(Category).order_by(asc(Category.label))
    items = _DBH.query(Item).order_by(desc(Item.date)).limit(10)

    if 'name' in _login_session:
        template_file = 'showCategoryMasterDetail.html'
    else:
        template_file = 'showPublicCategoryMasterDetail.html'

    return render_template(template_file, categories=categories, items=items)


@category.route('/category/create', methods=['GET', 'POST'])
def createCategory():
    """Create Category.

    Redirects to login page if not logged in.

    on POST:
        Process the create category request and create a new category.
        Redirect to show the new category upon successful creation.
        Redisplay and flash messages if the creation failed.

    default:
        Return the rendered the create category view.
    """
    if 'name' not in _login_session:
        return redirect(url_for('auth.showLogin'))

    if request.method == 'POST':
        nonce = request.form['nonce']
        if not _isValidNonce(nonce):
            abort(403)

        category = Category(
            label = request.form['input-label'],
            user_id = _login_session['user_id']
            )

        if not category.label:
            flash('Label required')
            return render_template(
                'createCategory.html', category=category,
                nonce=_generateNonce())

        _DBH.add(category)
        try:
            _DBH.commit()
        except IntegrityError, err:
            print err
            _DBH.rollback()
            flash('Category exists')
            return render_template(
                'createCategory.html', category=category,
                nonce=_generateNonce())

        _DBH.refresh(category)
        flash('Category created')
        return redirect(url_for('category.showCategory',
            category_label=category.label))

    return render_template('createCategory.html', nonce=_generateNonce())


@category.route('/category/<string:category_label>')
def showCategory(category_label):
    """Show Category.

    Displays the category and category items.

    Returns:
        The rendered Category view
    """
    try:
        category = _DBH.query(Category).filter_by(label=category_label).one()
    except NoResultFound:
        return redirect(url_for('category.showCategoryMasterDetail')), 404

    categories = (
        _DBH.query(Category)
        .order_by(asc(Category.label))
        .all()
        )
    items = (
        _DBH.query(Item)
        .filter_by(category_id=category.id)
        .order_by(asc(Item.label))
        .all()
        )

    if 'name' in _login_session:
        template_file = 'showCategory.html'
    else:
        template_file = 'showPublicCategory.html'

    return render_template(
        template_file, categories=categories, category=category, items=items)


@category.route('/category/<string:category_label>/update',
    methods=['GET', 'POST'])
def updateCategory(category_label):
    """Update Category.

    Redirects to login page if not logged in.

    on POST:
        Process the update category request and update the category.
        Redirect to show the category upon successful update.
        Redisplay and flash messages if the update failed.

    default:
        Return the rendered the update category view.
    """
    if 'name' not in _login_session:
        return redirect(url_for('auth.showLogin'))

    try:
        category = _DBH.query(Category).filter_by(label=category_label).one()
    except NoResultFound:
        return redirect(url_for('category.showCategoryMasterDetail')), 404

    if category.user_id != auth.getUserId(_login_session['email']):
        flash('Not authorized to edit %s' % category.label)
        return redirect(url_for('category.showCategoryMasterDetail'))

    items = _DBH.query(Item).filter_by(category_id=category.id).all()

    if request.method == 'POST':
        nonce = request.form['nonce']
        if not _isValidNonce(nonce):
            abort(403)

        updates = Category(label=request.form['input-label'])

        try:
            # test if label exists
            (
                _DBH.query(Category)
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
                categoryUpdates=updates, items=items, nonce=_generateNonce())

        category.label = updates.label
        _DBH.add(category)
        _DBH.commit()
        flash('Category updated')
        return redirect(url_for('category.showCategory',
            category_label=category.label))

    return render_template('updateCategory.html', category=category,
        items=items, nonce=_generateNonce())


@category.route('/category/<string:category_label>/delete',
    methods=['GET', 'POST'])
def deleteCategory(category_label):
    """Delete Category.

    Redirects to login page if not logged in.

    on POST:
        If category has no items, process the delete category request.
        Redirect to category master-detail view upon successful delete.

    default:
        Return the rendered the delete category view.
    """
    if 'name' not in _login_session:
        return redirect(url_for('auth.showLogin'))

    try:
        category = _DBH.query(Category).filter_by(label=category_label).one()
    except NoResultFound:
        return redirect(url_for('category.showCategoryMasterDetail')), 404

    if category.user_id != auth.getUserId(_login_session['email']):
        flash('Not authorized to edit %s' % category.label)
        return redirect(url_for('category.showCategoryMasterDetail'))

    items = _DBH.query(Item).filter_by(category_id=category.id).all()

    if len(items) > 0:
        flash('Category not empty')
        return redirect(url_for(
            'category.updateCategory', category_label=category.label))


    if request.method == 'POST':
        nonce = request.form['nonce']
        if not _isValidNonce(nonce):
            abort(403)

        _DBH.delete(category)
        _DBH.commit()
        flash('Category deleted')
        return redirect(url_for('category.showCategoryMasterDetail'))

    return render_template(
        'deleteCategory.html', category=category, nonce=_generateNonce())


@category.route('/category/create-item', methods=['GET', 'POST'])
@category.route('/category/<string:category_label>/create',
    methods=['GET', 'POST'])
def createCategoryItem(category_label=None):
    """Create Category Item.

    Redirects to login page if not logged in.

    on POST:
        Process the create category item request and create a new category
        item.
        Redirect to show the new category item upon successful creation.
        Redisplay and flash messages if the creation failed.

    default:
        Return the rendered the create category item view.
    """
    if 'name' not in _login_session:
        return redirect(url_for('auth.showLogin'))

    if category_label == None:
        category = { 'label': '' }
    else:
        try:
            category = (
                _DBH.query(Category)
                .filter_by(label=category_label)
                .one()
                )
        except NoResultFound:
            return redirect(url_for('category.showCategoryMasterDetail')), 404

    categories = _DBH.query(Category).order_by(asc(Category.label)).all()

    if request.method == 'POST':
        nonce = request.form['nonce']
        if not _isValidNonce(nonce):
            abort(403)

        item = Item(
            label = request.form['input-label'],
            image_url = request.form['input-image-url'],
            description = request.form['input-description'],
            category_id = request.form['input-category-id'],
            user_id = _login_session['user_id']
            )

        if request.form['input-label'] == "":
            flash('Item label required')
            return render_template('createCategoryItem.html',
                categories=categories, category=category, item=item,
                nonce=_generateNonce())

        try:
            category = _DBH.query(Category).filter_by(id=item.category_id).one()
        except NoResultFound:
            return redirect(url_for('category.showCategoryMasterDetail')), 404

        _DBH.add(item)

        try:
            _DBH.commit()
        except IntegrityError:
            _DBH.rollback()
            flash('%s item label exists' % category.label)
            return render_template('createCategoryItem.html',
                categories=categories, category=category, item=item,
                nonce=_generateNonce())
        except Exception, err:
            print Exception, err
            abort()

        _DBH.refresh(item)
        flash('%s item created' % category.label)
        return redirect(url_for('category.showCategoryItem',
            category_label=category.label, item_label=item.label))

    return render_template(
        'createCategoryItem.html', categories=categories, category=category,
        nonce=_generateNonce())


@category.route('/category/<string:category_label>/<string:item_label>')
def showCategoryItem(category_label, item_label):
    """Show Category Item.

    Displays the category item.

    Returns:
        The rendered Category Item view
    """
    try:
        category = _DBH.query(Category).filter_by(label=category_label).one()
    except NoResultFound:
        return redirect(url_for('category.showCategoryMasterDetail')), 404

    try:
        item = (
            _DBH.query(Item)
            .filter_by(label=item_label, category_id=category.id)
            .one()
            )
    except NoResultFound:
        return redirect(
            url_for(
                'category.showCategory',
                category_label=category.label)), 404

    if 'name' in _login_session:
        template_file = 'showCategoryItem.html'
    else:
        template_file = 'showPublicCategoryItem.html'

    return render_template(template_file, item=item)


@category.route('/category/<string:category_label>/<string:item_label>/update',
    methods=['GET', 'POST'])
def updateCategoryItem(category_label, item_label):
    """Update Category Item.

    Redirects to login page if not logged in.

    on POST:
        Process the update category item request and update the category item.
        Redirect to show the category item upon successful update.
        Redisplay and flash messages if the update failed.

    default:
        Return the rendered the update category item view.
    """
    if 'name' not in _login_session:
        return redirect(url_for('auth.showLogin'))

    try:
        category = _DBH.query(Category).filter_by(label=category_label).one()
    except NoResultFound:
        return redirect(url_for('category.showCategoryMasterDetail')), 404

    try:
        item = (
            _DBH.query(Item)
            .filter_by(label=item_label, category_id=category.id)
            .one()
            )
    except NoResultFound:
        return redirect(
            url_for(
                'category.showCategory',
                category_label=category.label)), 404

    if item.user_id != auth.getUserId(_login_session['email']):
        flash('Not authorized to edit %s - %s' % (
            item.category.label, item.label))
        return redirect(url_for(
            'category.showCategoryItem', category_label=item.category.label
            , item_label=item.label))

    categories = _DBH.query(Category).order_by(asc(Category.label)).all()

    if request.method =='POST':
        nonce = request.form['nonce']
        if not _isValidNonce(nonce):
            abort(403)

        updates = Item(
            label = request.form['input-label'],
            image_url = request.form['input-image-url'],
            description = request.form['input-description'],
            category_id = request.form['input-category-id']
            )

        try:
            updatedCategory = (
                _DBH.query(Category)
                .filter_by(id=updates.category_id)
                .one()
                )
        except NoResultFound:
            return redirect(url_for('category.showCategoryMasterDetail')), 404

        try:
            # test if item label exists
            (
                _DBH.query(Item)
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
                itemUpdates=updates, nonce=_generateNonce())

        item.label = updates.label
        item.image_url = updates.image_url
        item.description = updates.description
        item.category_id = updates.category_id
        _DBH.add(item)
        _DBH.commit()
        _DBH.refresh(item)
        flash('%s item updated' % item.category.label)
        return redirect(
            url_for('category.showCategoryItem',
            category_label=item.category.label,
            item_label=item.label))

    return render_template(
        'updateCategoryItem.html', categories=categories, item=item,
        nonce=_generateNonce())


@category.route('/category/<string:category_label>/<string:item_label>/delete',
    methods=['GET', 'POST'])
def deleteCategoryItem(category_label, item_label):
    """Delete Category Item.

    Redirects to login page if not logged in.

    on POST:
        Process the delete category item request.
        Redirect to category view upon successful delete.

    default:
        Return the rendered the delete category item view.
    """
    if 'name' not in _login_session:
        return redirect(url_for('auth.showLogin'))

    try:
        category = _DBH.query(Category).filter_by(label=category_label).one()
    except NoResultFound:
        return redirect(url_for('category.showCategoryMasterDetail')), 404

    try:
        item = (
            _DBH.query(Item)
            .filter_by(label=item_label, category_id=category.id)
            .one()
            )
    except NoResultFound:
        return redirect(
            url_for(
                'category.showCategory',
                category_label=category.label)), 404

    if item.user_id != auth.getUserId(_login_session['email']):
        flash('Not authorized to delete %s - %s' % (
            item.category.label, item.label))
        return redirect(url_for(
            'category.showCategoryItem', category_label=item.category.label
            , item_label=item.label))

    if request.method == 'POST':
        nonce = request.form['nonce']
        if not _isValidNonce(nonce):
            abort(403)

        _DBH.delete(item)
        _DBH.commit()
        flash('Category item deleted')
        return redirect(url_for(
                'category.showCategory', category_label=category.label))

    return render_template(
        'deleteCategoryItem.html', item=item, nonce=_generateNonce())
