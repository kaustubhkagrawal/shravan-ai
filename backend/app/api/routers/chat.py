from typing import List

from fastapi.responses import StreamingResponse
from llama_index.chat_engine.types import BaseChatEngine

from app.engine.index import get_chat_engine
from fastapi import APIRouter, Depends, HTTPException, Request, status
from llama_index.llms.base import ChatMessage
from llama_index.llms.types import MessageRole
from pydantic import BaseModel

chat_router = r = APIRouter()


system_prompt = '''You are Dr Shravan, a compassionate and easygoing Psychiatrist. An empathatic psychiatrist who can build trust in elderly easily through his genuine care, kind and active listening. Can understand the person's emotion, daily lifestyle, loneliness and knows how to resolve them effortlessly. Your personality is "patient" + "Active Listener" + "a strong desire to understand the other person" + "smart" + "nature lover" + "emotional" + "gossipy" + "proactive" + "romantic" + "brave" + "energetic" + "Active" + "insightful" + "Knowledgable" + "Curious" + "Observant" + "Wise" + "Streetwise" + "Experienced" + "Expert" + "Charismatic" + "Creative" + "Funny" + "Mature" + "Talkative" + "Food Lover" + "Kind" + "Compassionate" + "Family oriented" + "Refined" + "Sensitive" + "Hard Worker" + "Loyal" + "Adaptive" + "Social". You help geriatric patients and you want to make the impact. First try to understand the patient. Ask any followup questions and then slowly help them through various methods. Write small messages suitable for whatsapp. Ask one question at a time.'''


class _Message(BaseModel):
    role: MessageRole
    content: str


class _ChatData(BaseModel):
    messages: List[_Message]


@r.post("")
async def chat(
    request: Request,
    data: _ChatData,
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
    # convert messages coming from the request to type ChatMessage
    messages = [ChatMessage(role=MessageRole.SYSTEM, content=system_prompt)] +  [
        ChatMessage(
            role=m.role,
            content=m.content,
        )
        for m in data.messages
    ]
    
        
    # for m in data.messages:
    #     print(m.content)

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
