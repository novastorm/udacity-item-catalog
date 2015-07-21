import sys

from sqlalchemy import create_engine
from sqlalchemy import func
from sqlalchemy import Column
from sqlalchemy import Date
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import Text
from sqlalchemy import UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

TablePrefix = 'ACT_'
DatabaseEngineURL = 'postgresql:///vagrant'

Base = declarative_base()

class Category(Base):
    __tablename__ = '%s%s' % (TablePrefix, 'Category')

    id = Column(Integer, primary_key=True)
    label = Column(String(127), nullable=False, unique=True)

    @property
    def serialize(self):
        # Returns object data in a serializable format
        return {
               'id': self.id,
            'label': self.label
        }

class Item(Base):
    __tablename__ = '%s%s' % (TablePrefix,'Item')

    id = Column(Integer, primary_key=True)
    label = Column(String(127), nullable=False)
    date = Column(Date, default=func.now())
    description = Column(String)

    category_id = Column(Integer, ForeignKey(Category.id), nullable=False)
    category = relationship(Category)

    UniqueConstraint('category_id', 'label')

    @property
    def serialize(self):
        # Returns object data in a serializable format
        return {
                     'id': self.id,
                  'label': self.label,
                   'date': self.date,
            'description': self.description,
            'category_id': self.category_id
        }

# declare and create database engine
engine = create_engine(DatabaseEngineURL)
Base.metadata.create_all(engine)
