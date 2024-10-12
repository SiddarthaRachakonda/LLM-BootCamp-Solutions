from sqlalchemy import Column, ForeignKey, Integer, String, DateTime
from sqlalchemy.orm import relationship

from app.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    messages = relationship("Message", back_populates="user")

# TODO: Implement the Message SQLAlchemy model. Message should have a primary key, 
# a message attribute to store the content of messages, a type, AI or Human, 
# depending on if it is a user question or an AI response, a timestamp to 
# order by time and a user attribute to get the user instance associated 
# with the message. We also need a user_id that will use the User.id 
# attribute as a foreign key.
class Message(Base):
    __tablename__ = "messages"
    id = Column(Integer, primary_key=True, index=True)
    message = Column(String)
    type = Column(String)
    timestamp = Column(DateTime)
    user_id = Column(Integer, ForeignKey("users.id"))
    user = relationship("User", back_populates="messages")