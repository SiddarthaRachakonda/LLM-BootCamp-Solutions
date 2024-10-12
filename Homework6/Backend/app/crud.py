from sqlalchemy.orm import Session
import app.models as models
import app.schemas as schemas
from datetime import datetime



def get_or_create_user(db: Session, username: str):
    user = db.query(models.User).filter(models.User.username == username).first()
    if not user:
        user = models.User(username=username)
        db.add(user)
        db.commit()
        db.refresh(user)
    return user

def add_message(db: Session, message: schemas.MessageBase, username: str):
    # TODO:  Implement the add_message function. It should:
    # - get or create the user with the username
    # - create a models.Message instance
    # - pass the retrieved user to the message instance
    # - save the message instance to the database
    user = get_or_create_user(db, username)
    message = models.Message(message=message.message, type=message.type, user=user, timestamp=datetime.now(), user_id=user.id)
    db.add(message)
    db.commit()
    db.refresh(message)
    return message

def get_user_chat_history(db: Session, username: str):
    
    user = get_or_create_user(db, username)
    return user.messages