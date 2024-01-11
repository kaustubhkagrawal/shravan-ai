import logging
import os
from typing import List
from llama_index.llms import Perplexity

from app.engine.constants import STORAGE_DIR
from app.engine.context import create_service_context
from llama_index.chat_engine.types import BaseChatEngine, ChatMode
from llama_index.agent import ReActAgent

from llama_index.program import GuidancePydanticProgram

from app.api.routers.chat import _Message

from pydantic import BaseModel

class EmotionOutput(BaseModel):
    emotion: str

pplx_api_key = os.environ.get("PPLX_API_KEY", None)

async def get_emotion_detection_output(chat_messages: str):
    program = GuidancePydanticProgram(
        output_cls=EmotionOutput,
        prompt_template_str=(
            "Generate an output emotional label among [angry, calm, fearful, happy, sad], given the conversation history so far."
            " The conversation history is as follows:\n\n"
            "{{chat_messages}}\n"
        ),
        guidance_llm=Perplexity(
            api_key=pplx_api_key, model="mistral-8x7b-instruct", temperature=1
        ),
        verbose=False,
    )

    return program(conversation_history=chat_messages)


