
#  ESP32 Chatbot Server

FastAPI backend for ESP32 audio interaction. It accepts audio input from ESP32 devices, processes it via LLM, and returns synthesized audio responses.

---

##  How to Run

### 1. Create and activate virtual environment

####  Linux / macOS
```bash
python3 -m venv venv
source venv/bin/activate
````

####  Windows (CMD)

```cmd
python -m venv venv
venv\Scripts\activate
```

---

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

---

### 3. Run the FastAPI server

```bash
python3 main.py
# or (on Windows)
python main.py
```

---

##  Routes

### `GET /`

* Health check endpoint.
* Returns:

  ```json
  {
    "status": "healthy"
  }
  ```

---

### `POST /convert`

* Accepts audio file (WAV/MP3).
* Transcribes speech to text.
* Sends to LLM for response generation.
* Converts response text to audio.
* Returns audio as a streaming MP3 response.

---
###  Optional: Test the `/convert` Route Locally

You can simulate an ESP32 audio POST request using the following script:

```
request/python_simulation/post_simulation.py
```

This script is useful for logical and intuitive testing of the POST request and response retrieval functionality without actual hardware.

##  System Design

![System Design](assets/systemdesign.png)


---
##  Tech Stack

* FastAPI
* Redis (for conversation memory/short term)
* ChromaDB (for personal information recall/long term)
* Speech Recognition & Text-to-Speech
* ESP32 HTTP client integration
* LangChain and Gemini AI for initial implementation testing
* SQLite (storage of ChromaDB personal information recall)
  

---


