"use client";

import { useChat } from "ai/react";
import { ChatInput, ChatMessages } from "./ui/chat";
import { useState } from "react";
import { envConfig } from "../config/env.config";
import axios from "axios";
import Image from "next/image";

export default function ChatSection({ handleEmotion }: any) {
  const [extraFormData, setExtraFormData] = useState(new FormData());

  const {
    messages,
    input,
    setInput,
    isLoading,
    handleSubmit,
    handleInputChange,
    reload,
    stop,
    setMessages,
  } = useChat({
    api: `${envConfig.apiURL}/chat`,
    headers: {
      "Content-Type": "application/json", // using JSON because of vercel/ai 2.2.26
    },
  });

  const handleSubmitWrapper: typeof handleSubmit = (e) => {
    handleSubmit(e);
    if (messages.length > 0) {
      handleEmotion(messages);
    }
  };

  return (
    <div className="space-y-4 max-w-5xl w-full">
      <ChatMessages
        messages={messages}
        isLoading={isLoading}
        reload={reload}
        stop={stop}
      />
      <ChatInput
        input={input}
        handleSubmit={handleSubmitWrapper}
        setInput={setInput}
        handleInputChange={handleInputChange}
        isLoading={isLoading}
        multiModal={process.env.NEXT_PUBLIC_MODEL === "gpt-4-vision-preview"}
      />
    </div>
  );
}
