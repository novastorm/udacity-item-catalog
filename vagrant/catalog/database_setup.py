import sys

from sqlalchemy import create_engine
from sqlalchemy import Column
from sqlalchemy import Enum
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import Text
from sqlalchemy import Index
from sqlalchemy import UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

TablePrefix = 'ACT_'
# DatabaseEngine = 'sqlite:///restaurantmenu.db'
DatabaseEngineURL = 'postgresql:///vagrant'

Base = declarative_base()


class Course(Base):
    __tablename__ = '%s%s' % (TablePrefix, 'Course')

    id = Column(Integer, primary_key=True)
    label = Column(String(127), nullable=False, unique=True)
    description = Column(Text)

    @property
    def serialize(self):
        # Returns object data in a serializable format
        return {
                     'id': self.id,
                  'label': self.label,
            'description': self.description
        }


class Skill(Base):
    __tablename__ = '%s%s' % (TablePrefix, 'Skill')

    id = Column(Integer, primary_key=True)
    label = Column(String(127), nullable=False)
    level = Column(Integer)
    rank = Column(Integer)
    category = Column(String(127))
    subcategory = Column(String(127))
    description = Column(Text)
    example = Column(Text)

    course_id = Column(Integer, ForeignKey(Course.id), nullable=False)
    course = relationship(Course)

    __table_args__ = (UniqueConstraint('course_id', 'label'), None)

    @property
    def serialize(self):
        # Returns object data in a serializable format
        return {
                     'id': self.id,
                  'label': self.label,
                  'level': self.level,
                   'rank': self.rank,
               'category': self.category,
            'subcategory': self.subcategory,
            'description': self.description,
                'example': self.example,
        }


class Exercise(Base):
    __tablename__ = '%s%s' % (TablePrefix, 'Exercise')

    id = Column(Integer, primary_key=True)
    label = Column(String(127), nullable=False)
    type = Column(
        Enum(
            'none',
            'walk thru',
            'skill practice',
            'level',
            'alternate',
            'challenge',
            'bonus',
            name='exercise_types'),
        default='none')
    weight = Column(Integer, default=0)
    difficulty = Column(Integer, default=0)
    group = Column(String)
    task = Column(Text)
    hint = Column(Text)

    course_id = Column(Integer, ForeignKey(Course.id), nullable=False)
    course = relationship(Course)

    __table_args__ = (UniqueConstraint('course_id', 'label'), None)

    @property
    def serialize(self):
        # Returns object data in a serializable format
        return {
                    'id': self.id,
                 'label': self.label,
                  'type': self.type,
                'weight': self.weight,
            'difficulty': self.difficulty,
                 'group': self.group,
                  'task': self.task,
                  'hint': self.hint,
        }



# declare and create database engine
engine = create_engine(DatabaseEngineURL)
Base.metadata.create_all(engine)