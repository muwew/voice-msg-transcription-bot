import whisper

model = whisper.load_model("small")

def transcribe_file(file_path, language = "auto"):
    if language == "auto":
        result = model.transcribe(file_path)
    else:
        result = model.transcribe(file_path, language=language)
    return result["text"]
