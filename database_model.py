from sqlalchemy import Column,Integer,Text
from sqlalchemy.orm import declarative_base
from DB_engine import engine

BASE=declarative_base()

class NewsData(BASE):
    __tablename__= "NEWSDATA"

    id=Column(Integer(),primary_key=True,autoincrement=True)
    newsID=Column(Text,nullable=True)
    title=Column(Text)
    url=Column(Text)
    body=Column(Text)
    description=Column(Text)

BASE.metadata.create_all(engine)