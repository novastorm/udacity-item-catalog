from flask import Flask
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
def restaurantList():
    restaurants = session.query(Restaurant).all()
    return render_template('restaurants.html', restaurants=restaurants)


@app.route('/restaurants/<int:restaurant_id>/menu_items')
def restaurantMenu(restaurant_id):
    restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()
    menuItems = session.query(MenuItem).filter_by(restaurant_id=restaurant.id)
    return render_template('restaurant_menus.html', restaurant=restaurant, menuItems=menuItems)


# Task 1: Create route for newMenuItem function here
@app.route('/restaurants/<int:restaurant_id>/menu_items/create', methods=['GET', 'POST'])
def createMenuItem(restaurant_id):
    if request.method == 'POST':
        newMenuItem = MenuItem(restaurant_id=restaurant_id,  name=request.form['name'])
        session.add(newMenuItem)
        session.commit()
        return redirect(url_for('restaurantMenu', restaurant_id=restaurant_id))
    else:
        restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()
        return render_template('restaurant_menu_create.html', restaurant=restaurant)


# Task 2: Create route for editMenuItem function here
@app.route('/restaurants/<int:restaurant_id>/menu_items/<int:menuItem_id>/edit', methods=['GET', 'POST'])
def editMenuItem(restaurant_id, menuItem_id):
    if request.method == 'POST':
        menuItem = session.query(MenuItem).filter_by(restaurant_id=restaurant_id, id=menuItem_id).one()
        menuItem.name=request.form['input-menuItem-name']
        session.add(menuItem)
        session.commit()
        return redirect(url_for('restaurantMenu', restaurant_id=restaurant_id))
    else:
        restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()
        menuItem = session.query(MenuItem).filter_by(id=menuItem_id).one()
        return render_template('restaurant_menu_edit.html', restaurant=restaurant, menuItem=menuItem)


# Task 3: Create a route for deleteMenuItem function here
@app.route('/restaurants/<int:restaurant_id>/menu_items/<int:menuItem_id>/delete', methods=['GET', 'POST'])
def deleteMenuItem(restaurant_id, menuItem_id):
    if request.method == 'POST':
        menuItem = session.query(MenuItem).filter_by(id=menuItem_id).one()
        session.delete(menuItem)
        session.commit()
        return redirect(url_for('restaurantMenu', restaurant_id=restaurant_id))
    else:
        restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()
        menuItem = session.query(MenuItem).filter_by(id=menuItem_id).one()
        return render_template('restaurant_menu_delete.html', restaurant=restaurant, menuItem=menuItem)


if __name__ == '__main__':
    app.debug = True
    app.run(host = '0.0.0.0', port=PORT)
