import os

from llama_index import ServiceContext
# from llama_index.llms import OpenAI
from llama_index.llms import Perplexity



pplx_api_key = "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"

def create_base_context():
    model = os.getenv("MODEL", "gpt-3.5-turbo")
    return ServiceContext.from_defaults(
        llm = Perplexity(
            api_key=pplx_api_key, model="mixtral-8x7b-instruct", temperature=0.5
        ), 
embed_model='local'
    )
