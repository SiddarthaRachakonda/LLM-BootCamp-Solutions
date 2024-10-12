from typing import Dict, Any, List
from langchain_core.callbacks import BaseCallbackHandler
import app.schemas as schemas
import app.crud as crud


class LogResponseCallback(BaseCallbackHandler):

    def __init__(self, user_request: schemas.UserRequest, db):
        super().__init__()
        self.user_request = user_request
        self.db = db

    def on_llm_end(self, outputs: Dict[str, Any], **kwargs: Any) -> Any:
        """Run when llm ends running."""
        # TODO: The function on_llm_end is going to be called when the LLM stops sending 
        # the response. Use the crud.add_message function to capture that response.
        # print(outputs)
        # print(outputs.generations[0][0].text)
        crud.add_message(self.db, schemas.MessageBase(message=outputs.generations[0][0].text, type="assistant"), self.user_request.username)

    def on_llm_start(
        self, serialized: Dict[str, Any], prompts: List[str], **kwargs: Any
    ) -> Any:
        for prompt in prompts:
            print(prompt)