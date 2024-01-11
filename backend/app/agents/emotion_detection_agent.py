import logging
import os
from typing import List
from llama_index import (
    SimpleDirectoryReader,
    VectorStoreIndex,
    StorageContext,
    load_index_from_storage,
)

from app.engine.constants import STORAGE_DIR
from app.engine.context import create_service_context
from llama_index.chat_engine.types import BaseChatEngine, ChatMode
from llama_index.agent import ReActAgent

from llama_index.tools import QueryEngineTool, ToolMetadata

from app.api.routers.chat import _Message


def get_emotion_detection_agent(messages: List[_Message]):
    service_context = create_service_context()
    logger = logging.getLogger("uvicorn")
    

    query_engine_tools = [
        
    ]
    
    agent = ReActAgent.from_tools(
        query_engine_tools, llm=service_context.llm, verbose=True
    )
    # The line `return index.as_chat_engine(chat_mode= ChatMode, verbose=False)` is returning an
    # instance of a chat engine.
    return agent.as_chat_engine(chat_mode=ChatMode.REACT, verbose=True)
