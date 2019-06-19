from sqlalchemy import create_engine
from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

import config

engine = create_engine(config.DB_STRING, connect_args={'connect_timeout': 10})
Base = declarative_base()


class Task(Base):
    __tablename__ = 'tasks'
    SUCCESS = 'done'
    ERROR = 'error'
    RUNNING = 'running'

    id = Column(Integer, primary_key=True)
    md5 = Column(String)
    url = Column(String)
    status = Column(String)


Base.metadata.create_all(engine)
Session = sessionmaker(engine)
session = Session()


def create_new_task(url: str) -> str:
    task = Task(url=url, status=Task.RUNNING)
    session.add(task)
    session.commit()
    return task.id


def write_result(id: int, hash_sum: str) -> None:
    task = session.query(Task).get(id)
    if hash_sum:
        task.status = Task.SUCCESS
        task.md5 = hash_sum
    else:
        task.status = Task.ERROR
    session.commit()


def get_by_id(id: int):
    return session.query(Task).get(id)
