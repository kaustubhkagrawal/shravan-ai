import { useState, useRef } from "react";
import { useVoiceRecorder } from "../../../hooks/use-voice-recorder";

interface AudioRecorderProps {
  setAudioUrl: (value: string) => void;
}

const AudioRecorder = ({ setAudioUrl }: AudioRecorderProps) => {
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
      setAudioUrl(result);
    });
  });
  // const [isRecording, setIsRecording] = useState(false);
  // const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  // const audioChunksRef = useRef<Blob[]>([]);

  // const startRecording = async () => {
  //   const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
  //   mediaRecorderRef.current = new MediaRecorder(stream);
  //   mediaRecorderRef.current.addEventListener("dataavailable", (event) => {
  //     if (event.data.size > 0) {
  //       audioChunksRef.current.push(event.data);
  //     }
  //   });
  //   mediaRecorderRef.current.start();
  //   setIsRecording(true);
  // };

  // const stopRecording = () => {
  //   mediaRecorderRef.current?.stop();
  //   setIsRecording(false);
  //   saveRecording();
  // };

  // const saveRecording = () => {
  //   const audioBlob = new Blob(audioChunksRef.current, { type: "audio/wav" });
  //   const audioUrl = URL.createObjectURL(audioBlob);

  //   setAudioUrl(audioUrl);

  //   // You can now send `audioBlob` to the server using the API
  // };

  // // const handleUploadAudioFile = async (file: File) => {
  // //   const base64 = await new Promise<string>((resolve, reject) => {
  // //     const reader = new FileReader();
  // //     reader.readAsDataURL(file);
  // //     reader.onload = () => resolve(reader.result as string);
  // //     reader.onerror = (error) => reject(error);
  // //   });
  // //   setAudioUrl(base64);
  // // };

  return (
    <div>
      <button onClick={isRecording ? stop : start}>
        {isRecording ? "Stop Recording" : "Start Recording"}
      </button>
      {/* <>
        {records.map((data, idx) => (
          <div key={idx}>
            <audio src={data} controls preload={"metadata"} />
          </div>
        ))}
      </> */}
      {/* {isRecording || <button onClick={saveRecording}>Save Recording</button>} */}
    </div>
  );
};

export default AudioRecorder;
