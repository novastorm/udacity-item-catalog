import json
import os

import config as Config

from optparse import OptionParser
from pprint import PrettyPrinter

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.exc import NoResultFound

from routes.auth import createUser
from routes.auth import getUserId

from database_setup import Base
from database_setup import Category
from database_setup import Item

DatabaseEngineURL = Config.DatabaseEngineURL

engine = create_engine(DatabaseEngineURL)
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
DBH = DBSession()

def main():
    parser = OptionParser()
    parser.add_option("-d", "--data", dest="datafile",
        help="import data from json DATAFILE", default="test_data.json")

    """Populate Catalog with test data"""

    (options, args) = parser.parse_args()

    filename = options.datafile

    assert os.path.exists(filename), \
        '%s File does not exist' % filename

    with open(filename) as test_data_filehandle:
        test_data = json.load(test_data_filehandle)
    test_data_filehandle.close()

    pp = PrettyPrinter(indent=4)
    for user in test_data['Users']:
        createUser({
            'name': user['name'],
            'email': user['email'],
            'picture': ''
            })
    aUserID = getUserId(test_data['Users'][0]['email'])
    for category_record in test_data['Categories']:
        category = Category(
            label = category_record['label'],
            user_id = aUserID
            )
        DBH.add(category)
        DBH.commit()
        DBH.refresh(category)
        print "category %s => id %s" % (category.label, category.id)

        for item_record in category_record['items']:
            item = Item(
                label = item_record['label'],
                image_url = item_record['image_url'],
                description = item_record['description'],
                category_id = category.id,
                user_id = aUserID
                )
            DBH.add(item)
            DBH.commit()


if __name__ == '__main__':
    main()
