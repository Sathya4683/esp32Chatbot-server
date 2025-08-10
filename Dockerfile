# 1. Base image (Python 3.11 slim for smaller size)
FROM python:3.11-slim

# 2. Set working directory inside container
WORKDIR /app

# 3. Install system dependencies (if needed by your packages)
RUN apt-get update && apt-get install -y \
    build-essential \
    libsndfile1 \
    && rm -rf /var/lib/apt/lists/*

# 4. Copy only required files
COPY requirements.txt .
COPY services/ ./services/
COPY main.py .
COPY demo.env .env  # Rename demo.env to .env inside container

# 5. Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# 6. Expose the port FastAPI will run on
EXPOSE 8000

# 7. Command to run the app
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
