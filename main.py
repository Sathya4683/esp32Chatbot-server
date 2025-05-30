from fastapi import FastAPI, UploadFile, File, HTTPException
import uvicorn
from fastapi.responses import StreamingResponse
from io import BytesIO

# Assuming these are your imports from services modules
from services.STT import transcribe_audio, transcribe_audio_with_whisper
from services.TTS import synthesize_audio
from services.LLM import generate_response

app = FastAPI()

@app.post("/convert")
async def convert(audio: UploadFile = File(...)):
    # 1. Validate content type
    valid_types = ["audio/", "application/octet-stream"]
    if not any(audio.content_type.startswith(t) for t in valid_types):
        raise HTTPException(status_code=400, detail="Invalid file type. Please upload an audio file.")

    # 2. Read audio bytes from UploadFile
    audio_bytes = await audio.read()

    # 3. Transcribe audio (speech-to-text)
    try:
        user_text = transcribe_audio(audio_bytes)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Speech transcription failed: {str(e)}")
    
    print("USER PROMTPT: ", user_text)

    # 4. Generate response text from LLM
    user_id = 1
    past_conversations = ["oof this summer is really bad and warm"]
    user_info = ["The users likes having icecreams during summer", "The user likes having watermelon juice in summer"]
    llm_text = generate_response(user_text, user_id, past_conversations, user_info)

    # 5. Synthesize audio (text-to-speech)
    try:
        response_audio_bytes = synthesize_audio(llm_text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Audio synthesis failed: {str(e)}")

    # 6. Return audio file as StreamingResponse (mp3)
    return StreamingResponse(BytesIO(response_audio_bytes), media_type="audio/mpeg")

if __name__=="__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)