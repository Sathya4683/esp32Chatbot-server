#==============================IMPORTS AND JUST GETTING SCRIPTS FROM PYTHON PACKAGES(services/local/database)=====================
from fastapi import FastAPI, UploadFile, File, HTTPException, Depends, Request
from fastapi.responses import StreamingResponse
from io import BytesIO
import threading, json, httpx, os, time, uvicorn, psycopg2, schedule, asyncio
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, RedirectResponse
from redis import Redis
from dotenv import load_dotenv
from psycopg2.extras import RealDictCursor
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from pydantic import BaseModel
from database import models
from database.database import engine, get_db, Base
from sqlalchemy.orm import Session
import urllib.parse

#imports from services modules
from services.STT import transcribe_audio, transcribe_audio_with_whisper
from services.TTS import synthesize_audio
from services.LLM import generate_response

#getting database details from .env file
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")

#getting redis (caching recent conversation-short term memory implementation) related details from .env file
REDIS_HOST=os.getenv("REDIS_HOST")
REDIS_PORT=os.getenv("REDIS_PORT")


#=================================SETTING UP THE FASTAPI APP (INTIALIZE POSTGRESQL ORM, LIFESPAN, REDIS CACHE, SCHEDULERS)====================================
# Use lifespan for startup/shutdown logic.... set up redis client, postgresql database connector and some scheduling for the long-term memory task
@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Starting async scheduler loop...")
    app.state.redis = Redis(host=REDIS_HOST, port=REDIS_PORT)
    app.state.http_client = httpx.AsyncClient()
    models.Base.metadata.create_all(bind = engine)

    #connect to the postgres server
    while True:
        try:
            conn = psycopg2.connect(
                host=DB_HOST,
                port=DB_PORT,
                database=DB_NAME,
                user=DB_USER,
                password=DB_PASSWORD,
                cursor_factory=RealDictCursor
            )
            cursor =conn.cursor()
            print("connection complete")
            break
        except Exception as error:
            print("connection not done",error)
            time.sleep(2)
    # Start background scheduler task
    app.state.scheduler_task = asyncio.create_task(run_scheduler(app))
    yield  # app runs here
    # Cleanup
    app.state.scheduler_task.cancel()
    await app.state.http_client.aclose()
    app.state.redis.close()
    print("App shutdown — scheduler stopped and client closed.")

app = FastAPI(lifespan=lifespan)

# Add CORS middleware, since everything running on local development just allowing all origins and methods
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods (GET, POST, PUT, etc.)
    allow_headers=["*"],  # Allow all headers
)



#=================================================ROUTES===================================================================
#just a simple route to check if the server is active (taking in requests)
@app.get("/")
def return_status():
    return {"status":"healthy"}

#the only needed route tbh.......takes in the audio request (in .wav form as of now) sent by esp32s (using HTTP.client module), and then does transcription, LLM response generation and return a converted audio reponse (which can then be played using ESP32 audio output forms)
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



#============================START THE UVICORN SERVER BY RUNNING main.py=========================================================

if __name__=="__main__":
    #this line runs the uvicorn asgi server on localhost
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)