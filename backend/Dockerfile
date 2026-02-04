FROM python:3.11-slim

RUN apt-get update && apt-get install curl -y

ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache -r requirements.txt

COPY /backend /app/backend/

EXPOSE 5050

CMD ["python", "-m", "backend.app"]