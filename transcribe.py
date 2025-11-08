import whisper

# Load the model
model = whisper.load_model("base")

# Transcribe an audio file (change this to your file path)
result = model.transcribe("your_audio_file.mp3")

# Print the result
print(result["text"])