from typing import List
import base64
import whisper
import tempfile

from fastapi.responses import StreamingResponse
from llama_index.chat_engine.types import BaseChatEngine

from app.engine.index import get_chat_engine
from fastapi import APIRouter, Depends, HTTPException, Request, status
from llama_index.llms.base import ChatMessage
from llama_index.llms.types import MessageRole
from pydantic import BaseModel

from app.prompts.system import SYSTEM_PROMPT

system_prompt = ""

chat_router = r = APIRouter()


class _Message(BaseModel):
    role: MessageRole
    content: str

class _VoiceData(BaseModel):
    audioUrl: str

class ApiRequest(BaseModel):
    messages: List[_Message]
    data: _VoiceData


@r.post("")
async def chat(
    request: Request,
    data: ApiRequest,
    chat_engine: BaseChatEngine = Depends(get_chat_engine),
):
    _, voice_base_64 = data.data.audioUrl.split(',',1)
    audio_data = base64.b64decode(voice_base_64)
    # save temp webm file
    model = whisper.load_model("base")
    with tempfile.NamedTemporaryFile(suffix=".webm") as temp:
        temp.write(audio_data)
        temp.seek(0)
        result = model.transcribe(temp.name,language='en')
    # remove last message
    if len(data.messages) > 0:
        data.messages.pop()
    # append new user message 
    data.messages.append(ChatMessage(role=MessageRole.USER, content=result["text"]))
    # check preconditions and get last message
    if len(data.messages) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No messages provided",
        )
    lastMessage = data.messages.pop()
    if lastMessage.role != MessageRole.USER:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Last message must be from user",
        )

    with open("app/prompts/system_prompt.txt", "r") as file:
        system_prompt = file.read()

    # convert messages coming from the request to type ChatMessage
    messages = [ChatMessage(role=MessageRole.SYSTEM, content=system_prompt)] + [
        ChatMessage(
            role=m.role,
            content=m.content,
        )
        for m in data.messages
    ]
    

    # query chat engine
    response = chat_engine.stream_chat(lastMessage.content, messages)

    # stream response
    async def event_generator():
        for token in response.response_gen:
            # If client closes connection, stop sending events
            if await request.is_disconnected():
                break
            yield token

    return StreamingResponse(event_generator(), media_type="text/plain")
