FROM python:3.10-slim

RUN apt-get update && \
    apt-get install -y unrar-free && \
    apt-get clean

WORKDIR /app
COPY . .
RUN pip install --no-cache-dir -r requirements.txt

CMD ["bash", "-c", "python app/init_db.py && uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"]
