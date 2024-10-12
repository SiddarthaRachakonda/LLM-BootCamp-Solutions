import os
from langchain_huggingface import HuggingFaceEndpoint
from langchain_core.runnables import RunnablePassthrough
import app.schemas as schemas
from app.prompts import (
    raw_prompt,
    raw_prompt_formatted,
    history_prompt_formatted,
    standalone_prompt_formatted,
    format_context,
    rag_prompt_formatted,
    tokenizer
)
from app.data_indexing import DataIndexer

data_indexer = DataIndexer()

llm = HuggingFaceEndpoint( # type: ignore
    repo_id="meta-llama/Meta-Llama-3-8B-Instruct",
    huggingfacehub_api_token=os.environ['HF_TOKEN'],
    max_new_tokens=512,
    stop_sequences=[tokenizer.eos_token],
    streaming=True,
)

simple_chain = (raw_prompt | llm).with_types(input_type=schemas.UserQuestion) # type: ignore

# TODO: create formatted_chain by piping raw_prompt_formatted and the LLM endpoint.
formatted_chain = (raw_prompt_formatted | llm).with_types(input_type=schemas.UserQuestion) 

# TODO: use history_prompt_formatted and HistoryInput to create the history_chain
history_chain = (history_prompt_formatted | llm).with_types(input_type=schemas.HistoryInput)

# TODO: Let's construct the standalone_chain by piping standalone_prompt_formatted with the LLM
standalone_chain = (standalone_prompt_formatted | llm).with_types(input_type=schemas.HistoryInput)

input_1 = RunnablePassthrough.assign(new_question=standalone_chain)
input_2 = {
    'context': lambda x: format_context(data_indexer.search(x['new_question'])),
    'standalone_question': lambda x: x['new_question']
}
input_to_rag_chain = input_1 | input_2

# TODO: use input_to_rag_chain, rag_prompt_formatted, 
# HistoryInput and the LLM to build the rag_chain.
rag_chain = (input_to_rag_chain | rag_prompt_formatted | llm).with_types(input_type=schemas.HistoryInput)

# TODO:  Implement the filtered_rag_chain. It should be the 
# same as the rag_chain but with hybrid_search = True.

input_1 = RunnablePassthrough.assign(new_question=standalone_chain)
input_2 = {
    'context': lambda x: format_context(data_indexer.search(x['new_question'], hybrid_search=True)),
    'standalone_question': lambda x: x['new_question']
}
filtered_input_to_rag_chain = input_1 | input_2
filtered_rag_chain = (filtered_input_to_rag_chain | rag_prompt_formatted | llm).with_types(input_type=schemas.HistoryInput)






