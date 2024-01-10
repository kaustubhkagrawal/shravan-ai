import os

from llama_index import ServiceContext
# from llama_index.llms import OpenAI
from llama_index.llms import Perplexity
from llama_index.llms import HuggingFaceLLM

from llama_index.prompts import PromptTemplate


pplx_api_key = os.environ.get("PPLX_API_KEY", None)

# query_wrapper_prompt = PromptTemplate(
#     "Below is an instruction that describes a task. "
#     "Write a response that appropriately completes the request.\n\n"
#     "### Instruction:\n{query_str}\n\n### Response:"
# )


def create_base_context():
    model = os.getenv("MODEL", "gpt-3.5-turbo")
        
    # llm = HuggingFaceLLM(
    #     context_window=2048,
    #     max_new_tokens=256,
    #     generate_kwargs={"temperature": 0.25, "do_sample": False},
    #     query_wrapper_prompt=query_wrapper_prompt,
    #     model_name=model,
    #     device_map="auto",
    #     tokenizer_kwargs={"max_length": 2048},
    #     # uncomment this if using CUDA to reduce memory usage
    #     # model_kwargs={"torch_dtype": torch.float16}
    # )
    return ServiceContext.from_defaults(
        # llm = llm
        llm = Perplexity(
            api_key=pplx_api_key, model="mixtral-8x7b-instruct", temperature=0.5
        ), 
        embed_model='local'
        # llm  = OpenAI(model=model, temperature=0.5)
    )
