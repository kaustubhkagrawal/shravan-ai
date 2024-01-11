import Header from "@/app/components/header";
import ChatSection from "./chat-section";
import Image from "next/image";
import { useState } from "react";
import axios from "axios";
import { envConfig } from "../config/env.config";
import React from "react";

export function ChatPage() {
  const [emotion, setEmotion] = useState("");

  const handleEmotion = (messages: any) => {
    axios
      .post(`${envConfig.apiURL}/chat/emotion`, {
        messages,
      })
      .then((response) => {
        console.log(response.data);
        setEmotion(response.data);
      })
      .catch((err) => console.log(err));
  };
  return (
    <main className="flex min-h-screen  p-5 lg:p-12 background-gradient">
      <div className="flex w-20">
        {emotion ? (
          <div className="flex items-start">
            <Image
              src={`/emoticons/${emotion}.png`}
              alt={emotion}
              width={100}
              height={100}
              priority
            />
          </div>
        ) : null}
      </div>
      <div className="flex flex-col flex-grow items-center gap-10">
        <Header />
        <ChatSection handleEmotion={handleEmotion} />
      </div>
      {/* <a href="tel:+918768775550">Call Kaustubh</a> */}
    </main>
  );
}
