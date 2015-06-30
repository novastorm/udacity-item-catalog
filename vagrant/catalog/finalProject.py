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
    restaurants = session.query(Restaurant).all()
    return render_template('restaurants.html', restaurants=restaurants)


@app.route('/restaurants/create', methods=['GET', 'POST'])
def createRestaurant():
    if request.method == 'POST':
        restaurant = Restaurant(name=request.form['input-name'])
        session.add(restaurant)
        session.commit()
        return redirect(url_for('listRestaurants'))
    else:
        return render_template('restaurant_create.html')


@app.route('/restaurants/<int:restaurant_id>/update', methods=['GET', 'POST'])
def updateRestaurant(restaurant_id):
    restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()
    if request.method == 'POST':
        restaurant.name = request.form['input-name']
        session.add(restaurant)
        session.commit()
        return redirect(url_for('listRestaurants'))
    else:
        return render_template('restaurant_update.html', restaurant=restaurant)


@app.route('/restaurants/<int:restaurant_id>/delete', methods=['GET', 'POST'])
def deleteRestaurant(restaurant_id):
    restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()
    if request.method == 'POST':
        session.delete(restaurant)
        session.commit()
        return redirect(url_for('listRestaurants'))
    else:
        return render_template('restaurant_delete.html', restaurant=restaurant)


@app.route('/restaurants/<int:restaurant_id>/menu_items')
def listMenuItems(restaurant_id):
    return render_template('restaurant_menuItems.html', restaurant=restaurant, menuItems=items)


@app.route('/restaurants/<int:restaurant_id>/menu_items/create', methods=['GET', 'POST'])
def createMenuItem(restaurant_id):
    return render_template('restaurant_menuItem_create.html', restaurant=restaurant)


@app.route('/restaurants/<int:restaurant_id>/menu_items/<int:menuItem_id>/update', methods=['GET', 'POST'])
def updateMenuItem(restaurant_id, menuItem_id):
    return render_template('restaurant_menuItem_update.html', restaurant=restaurant, menuItem=item)


@app.route('/restaurants/<int:restaurant_id>/menu_items/<int:menuItem_id>/delete', methods=['GET', 'POST'])
def deleteMenuItem(restaurant_id, menuItem_id):
    return render_template('restaurant_menuItem_delete.html', restaurant=restaurant, menuItem=item)


if __name__ == '__main__':
    app.secret_key = 'asdf1234'
    app.debug = True
    app.run(host = '0.0.0.0', port=PORT)
