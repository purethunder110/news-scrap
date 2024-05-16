from sqlalchemy import create_engine
from sqlalchemy.engine import URL
from sqlalchemy.orm import sessionmaker,scoped_session

url= URL.create(
    drivername="postgresql",
    username="lallan",
    host="localhost",
    database="lallandb",
    password="123456789",
    port=5432
)

engine=create_engine(url,pool_size=50,max_overflow=20)

#conn=engine.connect()

session_factory=sessionmaker(engine)
Session_threaded=scoped_session(session_factory)