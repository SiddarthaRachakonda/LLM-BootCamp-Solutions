from langchain_core.runnables import Runnable
from langchain_core.callbacks import BaseCallbackHandler
from fastapi import FastAPI, Request, Depends
from sse_starlette.sse import EventSourceResponse
from langserve.serialization import WellKnownLCSerializer
from typing import List
from sqlalchemy.orm import Session

from app.chains import simple_chain, formatted_chain, history_chain, rag_chain
import app.crud as crud
import app.models as models
import app.schemas as schemas
from app.database import SessionLocal, engine
from app.callbacks import LogResponseCallback
from app.prompts import format_chat_history

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


async def generate_stream(input_data: schemas.BaseModel, runnable: Runnable, callbacks: List[BaseCallbackHandler]=[]):
    for output in runnable.stream(input_data.dict(), config={"callbacks": callbacks}): 
        data = WellKnownLCSerializer().dumps(output).decode("utf-8")
        yield {'data': data, "event": "data"} 
    yield {"event": "end"}


@app.post("/simple/stream")
async def simple_stream(request: Request):
    data = await request.json()
    user_question = schemas.UserQuestion(**data['input'])
    return EventSourceResponse(generate_stream(user_question, simple_chain))


@app.post("/formatted/stream")
async def formatted_stream(request: Request):
    # TODO: use the formatted_chain to implement the "/formatted/stream" endpoint.
    data = await request.json()
    user_question = schemas.UserQuestion(**data['input'])
    return EventSourceResponse(generate_stream(user_question, formatted_chain))


@app.post("/history/stream")
async def history_stream(request: Request, db: Session = Depends(get_db)):  
    # TODO: Let's implement the "/history/stream" endpoint. The endpoint should follow those steps:
    # - The endpoint receives the request
    # - The request is parsed into a user request
    # - The user request is used to pull the chat history of the user
    # - We add as part of the user history the current question by using add_message.
    # - We create an instance of HistoryInput by using format_chat_history.
    # - We use the history input within the history chain.
    data = await request.json()
    user_request = schemas.UserRequest(**data['input'])
    user_name = user_request.username
    chat_history = crud.get_user_chat_history(db, user_name)
    chat_history_str = format_chat_history(chat_history)
    crud.add_message(db, schemas.MessageBase(message=user_request.question, type="user"), user_name)
    history_input = schemas.HistoryInput(chat_history=chat_history_str, question=user_request.question)
    # print(history_input)
    return EventSourceResponse(generate_stream(history_input, history_chain, [LogResponseCallback(user_request, db)]))


@app.post("/rag/stream")
async def rag_stream(request: Request, db: Session = Depends(get_db)):  
    # TODO: Let's implement the "/rag/stream" endpoint. The endpoint should follow those steps:
    # - The endpoint receives the request
    # - The request is parsed into a user request
    # - The user request is used to pull the chat history of the user
    # - We add as part of the user history the current question by using add_message.
    # - We create an instance of HistoryInput by using format_chat_history.
    # - We use the history input within the rag chain.
    data = await request.json()
    user_request = schemas.UserRequest(**data['input'])
    user_name = user_request.username
    chat_history = crud.get_user_chat_history(db, user_name)
    chat_history_str = format_chat_history(chat_history)
    crud.add_message(db, schemas.MessageBase(message=user_request.question, type="user"), user_name)
    history_input = schemas.HistoryInput(chat_history=chat_history_str, question=user_request.question)
    return EventSourceResponse(generate_stream(history_input, rag_chain, [LogResponseCallback(user_request, db)]))


@app.post("/filtered_rag/stream")
async def filtered_rag_stream(request: Request, db: Session = Depends(get_db)):  
    # TODO: Let's implement the "/filtered_rag/stream" endpoint. The endpoint should follow those steps:
    # - The endpoint receives the request
    # - The request is parsed into a user request
    # - The user request is used to pull the chat history of the user
    # - We add as part of the user history the current question by using add_message.
    # - We create an instance of HistoryInput by using format_chat_history.
    # - We use the history input within the filtered rag chain.
    raise NotImplemented


# API to get the chat history
@app.post("/chat_history")
async def chat_history(request: Request, db: Session = Depends(get_db)):
    data = await request.json()
    user_name = data['username']
    chat_history = crud.get_user_chat_history(db, user_name)
    return chat_history
    


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="localhost", reload=True,  port=8000)