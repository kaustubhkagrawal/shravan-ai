import logging
import os
from llama_index.llms import Perplexity


from llama_index.program import LLMTextCompletionProgram
from llama_index.output_parsers import PydanticOutputParser


from pydantic import BaseModel

class EmotionOutput(BaseModel):
    emotion: str

pplx_api_key = os.environ.get("PPLX_API_KEY", None)

async def get_emotion_detection_output(chat_messages: str):
    program = LLMTextCompletionProgram.from_defaults(
        output_cls=EmotionOutput,
        prompt_template_str=(
            "Generate an output emotional label among [angry, calm, fearful, happy, sad], given the conversation history so far."
            " The conversation history is as follows:\n\n"
            "{{chat_messages}}\n"
        ),
        llm=Perplexity(
            api_key=pplx_api_key, model="mistral-7b-instruct", temperature=0
        ),
        verbose=False,
    )

    return program(chat_messages=chat_messages)


