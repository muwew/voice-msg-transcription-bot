FROM python:3.10-slim

# Install ffmpeg and other dependencies
RUN apt-get update && apt-get install -y ffmpeg git && apt-get clean

# Set working directory
WORKDIR /app

# Copy code
COPY . .

# Install Python deps
RUN pip install --upgrade pip && pip install -r requirements.txt

# Run your bot
CMD ["python", "main.py"]
