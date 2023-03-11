from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


PG_DSN = 'postgresql+asyncpg://artur:8114@127.0.0.1:5431/netology'


engine = create_async_engine(PG_DSN)
Base = declarative_base()
Session = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)


class SwapiPeople(Base):
    __tablename__ = "peoples"

    id = Column(Integer, primary_key=True)
    birth_year = Column(String(60))
    eye_color = Column(String(60))
    films = Column(String())
    gender = Column(String(60))
    hair_color = Column(String(60))
    height = Column(String(40))
    homeworld = Column(String(100))
    mass = Column(String(60))
    name = Column(String(100))
    skin_color = Column(String(60))
    species = Column(String())
    starships = Column(String())
    vehicles = Column(String())
