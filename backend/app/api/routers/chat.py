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

from app.agents.emotion_detection_agent import get_emotion_detection_output

system_prompt = ""

chat_router = r = APIRouter()


class _Message(BaseModel):
    role: MessageRole
    content: str


class _VoiceData(BaseModel):
    audioUrl: str


class ApiRequest(BaseModel):
    messages: List[_Message]


@r.post("")
async def chat(
    request: Request,
    data: ApiRequest,
    chat_engine: BaseChatEngine = Depends(get_chat_engine),
):
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


# define new router for transcribing voice input
model = whisper.load_model("tiny")


# Create a dependency that will provide the loaded model
def get_model():
    return model


@r.post("/voice")
async def voice(
    voice_data: _VoiceData,
    request: Request,
    model: whisper.Whisper = Depends(get_model),  # Inject the model dependency
) -> str:
    _, voice_base_64 = voice_data.audioUrl.split(",", 1)
    try:
        # Decode base64 voice data
        audio_bytes = base64.b64decode(voice_base_64)
        # Write the audio data to a temporary file
        with tempfile.NamedTemporaryFile(suffix=".webm") as temp:
            temp.write(audio_bytes)
            temp.seek(0)
            result = model.transcribe(temp.name, language="en")
        # Return the transcribed text
        return result["text"]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )

@r.post("/emotion")

async def emotion(
    request: Request,
    data: ApiRequest,
):
    if len(data.messages) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No messages provided",
        )
    try:
        concatenated_messages = "\n".join(message.content for message in data.messages)
        emotion_output = await get_emotion_detection_output(concatenated_messages)
        return emotion_output.emotion
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))