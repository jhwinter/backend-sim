from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from sqlalchemy import (
    Column,
    Integer,
    Sequence,
    String,
)


Base = declarative_base()


class User(Base):
    __tablename__ = 'users'

    id = Column(
        Integer,
        Sequence('animal_id_seq', increment=1),
        primary_key=True
    )
    email = Column(String)
    api_key = Column(String)

    def as_dict(self):
        return {
            'id': self.id,
            'email': self.email,
            'api_key': self.api_key
        }

    def __repr__(self):
        return f"<User(email={self.email}, api_key={self.api_key})>"


class Animal(Base):
    __tablename__ = 'animals'

    id = Column(
        Integer,
        Sequence('animal_id_seq', increment=1),
        primary_key=True
    )
    name = Column(String)
    species = Column(String)

    def as_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'species': self.species,
        }

    def __repr__(self):
        return f"<Animal(name={self.name}, species={self.species})>"


class Database(object):
    def __init__(self, config):
        self.config = config
        connection_string = 'sqlite:///{0}'.format(self.config['db'])
        self._engine = create_engine(connection_string)
        self._sessionmaker = sessionmaker(bind=self._engine)

    def create_session(self):
        return self._sessionmaker()
