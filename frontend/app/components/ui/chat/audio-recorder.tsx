import { useState, useRef } from "react";
import { useVoiceRecorder } from "../../../hooks/use-voice-recorder";
import { Mic, MicOff, Square, StopCircle } from "lucide-react";

import axios from "axios";
import { envConfig } from "@/app/config/env.config";
interface AudioRecorderProps {
  setAudioUrl: () => void;
  setInput?: (value: string) => void;
}

const AudioRecorder = ({ setAudioUrl, setInput }: AudioRecorderProps) => {
  const [records, updateRecords] = useState<string[]>([]);

  const blobToBase64 = (blob: Blob) => {
    const reader = new FileReader();
    reader.readAsDataURL(blob);
    return new Promise((resolve: (val: string) => void) => {
      reader.onloadend = () => {
        resolve(reader.result as string);
      };
    });
  };
  const { isRecording, stop, start } = useVoiceRecorder((data) => {
    updateRecords([...records, window.URL.createObjectURL(data)]);

    blobToBase64(data).then((result: string) => {
      transcribeAudio(result);
    });
  });

  const transcribeAudio = (audioUrl: string) => {
    axios
      .post(`${envConfig.apiURL}/chat/voice`, {
        audioUrl,
      })
      .then((response) => {
        setInput?.((response?.data as string) ?? "");
        setAudioUrl();
      })
      .catch((err) => console.log(err));
  };

  const handleStart = (e) => {
    // e.preventDefault();
    // setInput?.(" ");
    start();
  };

  return (
    <div>
      <button
        type={isRecording ? "submit" : "button"}
        className={`rounded-full relative ${
          isRecording ? "bg-red-500" : "bg-green-500"
        } p-2`}
        onClick={isRecording ? stop : handleStart}
      >
        {isRecording ? (
          <span className="animate-ping absolute inline-flex left-0 top-0 h-full w-full rounded-full bg-red-400 opacity-75"></span>
        ) : null}
        {isRecording ? (
          <Square color="white" size={20} />
        ) : (
          <Mic color="white" size={20} />
        )}
      </button>
    </div>
  );
};

export default AudioRecorder;
