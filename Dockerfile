FROM python:3.10-slim

WORKDIR /app

COPY . /app

RUN pip install --no-cache-dir fastapi uvicorn pandas openpyxl patool sqlite3 jinja2 python-multipart passlib[bcrypt]

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]