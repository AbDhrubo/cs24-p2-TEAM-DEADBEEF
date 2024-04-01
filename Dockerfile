# syntax=docker/dockerfile:1
FROM python:3.12.1-slim-bookworm

ENV FLASK_APP=main:app

WORKDIR /app

COPY . .

RUN bash -c "pip install --upgrade pip"
RUN bash -c "pip install -r requirements.txt"

# RUN bash -c "python init_db.py"

EXPOSE 5000

CMD ["flask", "run", "--host=127.0.0.1", "--port=5000"]

