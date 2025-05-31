from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.sql.expression import null
from .database import Base

class Chats(Base):
    __tablename__ = "chats"

    id = Column(Integer, primary_key = True, nullable = False, autoincrement = True)
    email = Column(String, default = True, nullable = False)
