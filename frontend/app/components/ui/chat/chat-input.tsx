import { useEffect, useRef, useState } from "react";
import { Button } from "../button";
import FileUploader from "../file-uploader";
import { Input } from "../input";
import UploadImagePreview from "../upload-image-preview";
import { ChatHandler } from "./chat.interface";
import AudioRecorder from "./audio-recorder";

export default function ChatInput(
  props: Pick<
    ChatHandler,
    | "isLoading"
    | "input"
    | "onFileUpload"
    | "onFileError"
    | "handleSubmit"
    | "handleInputChange"
    | "setInput"
  > & {
    multiModal?: boolean;
  }
) {
  const [imageUrl, setImageUrl] = useState<string | null>(null);
  const [audioUrl, setAudioUrl] = useState<string | null>(null);

  const needsSubmit = useRef(false);

  const buttonRef = useRef<HTMLButtonElement>(null);

  const onSubmit = (e: React.FormEvent<HTMLFormElement>) => {
    if (imageUrl) {
      props.handleSubmit(e, {
        data: { imageUrl: imageUrl },
      });
      setImageUrl(null);
      return;
    }

    console.log({ audioUrl });
    if (audioUrl) {
      props.handleSubmit(e, {
        data: { audioUrl: audioUrl },
      });
      setAudioUrl(null);
      return;
    }
    props.handleSubmit(e);
  };

  const onRemovePreviewImage = () => setImageUrl(null);

  const handleUploadImageFile = async (file: File) => {
    const base64 = await new Promise<string>((resolve, reject) => {
      const reader = new FileReader();
      reader.readAsDataURL(file);
      reader.onload = () => resolve(reader.result as string);
      reader.onerror = (error) => reject(error);
    });
    setImageUrl(base64);
  };

  // const handleUploadFile = async (file: File) => {
  //   try {
  //     if (props.multiModal && file.type.startsWith("image/")) {
  //       return await handleUploadImageFile(file);
  //     }
  //     props.onFileUpload?.(file);
  //   } catch (error: any) {
  //     props.onFileError?.(error.message);
  //   }
  // };

  const handleAudioRecorderStop = () => {
    // buttonRef.current?.click();
    needsSubmit.current = true;
  };

  useEffect(() => {
    if (needsSubmit.current) {
      setTimeout(() => {
        buttonRef.current?.click();
      }, 100);
      needsSubmit.current = false;
    }
  }, [props.input]);

  return (
    <form
      onSubmit={onSubmit}
      className="rounded-xl bg-white p-4 shadow-xl space-y-4"
    >
      {imageUrl && (
        <UploadImagePreview url={imageUrl} onRemove={onRemovePreviewImage} />
      )}
      <div className="flex w-full items-start justify-between gap-4 ">
        <AudioRecorder
          setInput={props.setInput}
          setAudioUrl={handleAudioRecorderStop}
        />
        <Input
          autoFocus
          name="message"
          placeholder="Type a message"
          className="flex-1"
          value={props.input}
          onChange={props.handleInputChange}
        />
        {/* <FileUploader
          onFileUpload={handleUploadFile}
          onFileError={props.onFileError}
        /> */}
        <Button
          type="submit"
          ref={buttonRef}
          className="disabled:bg-slate-500"
          disabled={props.isLoading}
        >
          Send message
        </Button>
      </div>
    </form>
  );
}
