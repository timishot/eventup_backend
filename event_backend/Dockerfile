FROM python:3.12-slim

WORKDIR /usr/src/event_backend

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

RUN apt-get update && apt-get install -y netcat-openbsd

RUN pip install --upgrade pip
COPY ./requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY ./entrypoint.sh .
RUN sed -i 's/\r$//g' /usr/src/event_backend/entrypoint.sh
RUN chmod +x /usr/src/event_backend/entrypoint.sh

COPY . .

ENTRYPOINT [ "/usr/src/event_backend/entrypoint.sh"]
