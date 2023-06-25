FROM python:3.9-alpine

ARG EMULATOR_PORT
ENV EMULATOR_PORT $EMULATOR_PORT

WORKDIR /app

COPY src/requirements.txt .
RUN pip3 install -r requirements.txt

COPY src .

COPY data /

CMD gunicorn --bind 0.0.0.0:${EMULATOR_PORT} -k eventlet wsgi:app
