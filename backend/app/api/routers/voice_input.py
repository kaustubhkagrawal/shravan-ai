import whisper

model = whisper.load_model("base")
result = model.transcribe("happy.wav" ,language='en')
print(result["text"])