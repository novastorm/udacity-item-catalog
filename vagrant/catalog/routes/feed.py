"""ATOM feed feature

Generates ATOM feed of recent items entered into the application
"""


import flask

from database_setup import Item
from flask import request
from flask import url_for
from sqlalchemy import desc
from sqlalchemy.orm import sessionmaker
from urlparse import urljoin
from werkzeug.contrib.atom import AtomFeed


_DBSession = sessionmaker()
_DBH = _DBSession()

feed = flask.Blueprint('feed', __name__)

def make_external(url):
    return urljoin(request.url_root, url)

@feed.route('/recent.atom')
def recent_feed():
    """Generate ATOM feed.

    Generate ATOM feed containing the item label, description, date, and a URL
    link to the item
    """
    feed = AtomFeed('Item Catalog', feed_url=request.url, url=request.url_root)
    items = _DBH.query(Item).order_by(desc(Item.date)).limit(15).all()

    for item in items:
        feed.add(
            title=item.label,
            content=item.description,
            content_type='text',
            url=make_external(url_for('category.showCategoryItem',
                category_label=item.category.label,
                item_label=item.label)),
            updated=item.date
            )

    return feed.get_response()
