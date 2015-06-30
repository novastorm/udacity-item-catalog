from flask import Flask
from flask import flash
from flask import jsonify
from flask import redirect
from flask import request
from flask import render_template
from flask import url_for
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base
from database_setup import Restaurant
from database_setup import MenuItem

PORT = 5000
app = Flask(__name__)
engine = create_engine('sqlite:///restaurantmenu.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

@app.route('/')
@app.route('/restaurants')
def listRestaurants():
    return "restaurant list"


@app.route('/restaurants/create', methods=['GET', 'POST'])
def createRestaurant():
    return "create restaurant"


@app.route('/restaurants/<int:restaurant_id>/update', methods=['GET', 'POST'])
def updateRestaurant(restaurant_id):
    return "update restaurant %s" % restaurant_id


@app.route('/restaurants/<int:restaurant_id>/delete', methods=['GET', 'POST'])
def deleteRestaurant(restaurant_id):
    return "delete restaurant %s" % restaurant_id


@app.route('/restaurants/<int:restaurant_id>/menu_items')
def restaurantMenu(restaurant_id):
    return "restaurant %s menu_item list" % restaurant_id


@app.route('/restaurants/<int:restaurant_id>/menu_items/create', methods=['GET', 'POST'])
def createMenuItem(restaurant_id):
    return "create restaurant %s menu_item" % restaurant_id


@app.route('/restaurants/<int:restaurant_id>/menu_items/<int:menuItem_id>/update', methods=['GET', 'POST'])
def updateMenuItem(restaurant_id, menuItem_id):
    return "update restaurant %s menu_item %s" % (restaurant_id, menuItem_id)


@app.route('/restaurants/<int:restaurant_id>/menu_items/<int:menuItem_id>/delete', methods=['GET', 'POST'])
def deleteMenuItem(restaurant_id, menuItem_id):
    return "delete restaurant %s menu_item %s" % (restaurant_id, menuItem_id)


if __name__ == '__main__':
    app.secret_key = 'asdf1234'
    app.debug = True
    app.run(host = '0.0.0.0', port=PORT)
