from flask import Flask
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
@app.route('/hello')
def HelloWorld():
    restaurant = session.query(Restaurant).first()
    items = session.query(MenuItem).filter_by(restaurant_id=restaurant.id)
    output = ''
    for i in items:
        output += "%s<br />" % i.name
        output += "%s<br />" % i.price
        output += "%s<br />" % i.description
        output += '<br />'

    return output

if __name__ == '__main__':
    app.debug = True
    app.run(host = '0.0.0.0', port=PORT)
