
# from langserve import RemoteRunnable
# chain = RemoteRunnable("https://hugsid-backend.hf.space/history")
# stream = chain.stream(input={'question':'You know my content is very limited and the audience are very smart. I dont know will that be ok?', 'username':'test'})
# for chunk in stream:
#     print(chunk, end="", flush=True)

import requests

url = "https://hugsid-backend.hf.space/chat_history"

response = requests.post(url, json={"username": "test"})

print(response.json())
