from lightapi import LightApi
from lightapi.database import Base
from sqlalchemy import Column, Integer, String

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    name = Column(String)

app = LightApi()
app.register(User)
app.run()

